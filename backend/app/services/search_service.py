"""
TECHGURU ElevateCRM Advanced Search Service

High-performance search service with PostgreSQL full-text search,
fuzzy matching fallback, faceted search, and intelligent caching.
"""
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from datetime import datetime, timedelta
import hashlib
import re

from sqlalchemy import select, func, text, and_, or_, desc, asc, cast, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.dialects.postgresql import TSVECTOR

from app.models.contact import Contact
from app.models.product import Product
from app.core.tenant_context import TenantContext
from app.services.tenant_service import TenantAwareService

logger = logging.getLogger(__name__)


class SearchQuery:
    """Parsed search query with support for phrases, exclusions, and operators"""
    
    def __init__(self, query_string: str):
        self.original = query_string.strip()
        self.terms = []
        self.phrases = []
        self.excluded_terms = []
        self.excluded_phrases = []
        
        if not self.original:
            return
            
        self._parse_query()
    
    def _parse_query(self):
        """Parse search query into terms, phrases, and exclusions"""
        # Extract quoted phrases first
        phrase_pattern = r'(-?)"([^"]+)"'
        phrases = re.findall(phrase_pattern, self.original)
        
        # Remove phrases from original string
        remaining = re.sub(phrase_pattern, ' ', self.original)
        
        # Process phrases
        for neg, phrase in phrases:
            if neg == '-':
                self.excluded_phrases.append(phrase.strip())
            else:
                self.phrases.append(phrase.strip())
        
        # Process remaining terms
        terms = remaining.split()
        for term in terms:
            term = term.strip()
            if not term:
                continue
                
            if term.startswith('-') and len(term) > 1:
                self.excluded_terms.append(term[1:])
            else:
                self.terms.append(term)
    
    def to_tsquery(self) -> str:
        """Convert to PostgreSQL tsquery format"""
        if not self.has_content():
            return ''
        
        parts = []
        
        # Add positive terms (AND by default)
        if self.terms:
            parts.append(' & '.join(f"'{term}':*" for term in self.terms))
        
        # Add positive phrases
        for phrase in self.phrases:
            # Convert phrase to proximity search
            phrase_terms = phrase.split()
            if len(phrase_terms) == 1:
                parts.append(f"'{phrase_terms[0]}':*")
            else:
                parts.append(' <-> '.join(f"'{term}'" for term in phrase_terms))
        
        # Combine positive parts with AND
        positive_query = ' & '.join(f"({part})" for part in parts) if parts else ''
        
        # Add exclusions with AND NOT
        exclusions = []
        for term in self.excluded_terms:
            exclusions.append(f"'{term}':*")
        for phrase in self.excluded_phrases:
            phrase_terms = phrase.split()
            if len(phrase_terms) == 1:
                exclusions.append(f"'{phrase_terms[0]}':*")
            else:
                exclusions.append(' <-> '.join(f"'{term}'" for term in phrase_terms))
        
        if exclusions:
            exclusion_query = ' | '.join(f"({excl})" for excl in exclusions)
            if positive_query:
                return f"({positive_query}) & !({exclusion_query})"
            else:
                return f"!({exclusion_query})"
        
        return positive_query
    
    def to_fuzzy_terms(self) -> List[str]:
        """Get all terms for fuzzy matching"""
        return self.terms + self.phrases + [f"-{term}" for term in self.excluded_terms]
    
    def has_content(self) -> bool:
        """Check if query has any searchable content"""
        return bool(self.terms or self.phrases or self.excluded_terms or self.excluded_phrases)


class SearchFilters:
    """Structured filters for search queries"""
    
    def __init__(self, filters: Dict[str, Any]):
        self.filters = filters or {}
    
    def get_sql_conditions(self, model_class) -> List:
        """Convert filters to SQLAlchemy conditions"""
        conditions = []
        
        for field, value in self.filters.items():
            if not hasattr(model_class, field):
                continue
                
            column = getattr(model_class, field)
            
            if isinstance(value, list):
                # IN clause for lists
                conditions.append(column.in_(value))
            elif isinstance(value, dict):
                # Range or comparison operators
                if 'gte' in value:
                    conditions.append(column >= value['gte'])
                if 'lte' in value:
                    conditions.append(column <= value['lte'])
                if 'gt' in value:
                    conditions.append(column > value['gt'])
                if 'lt' in value:
                    conditions.append(column < value['lt'])
                if 'from' in value and 'to' in value:
                    # Date range
                    conditions.append(and_(
                        column >= value['from'],
                        column <= value['to']
                    ))
            else:
                # Exact match
                conditions.append(column == value)
        
        return conditions


class SearchService:
    """Advanced search service with full-text search and fuzzy matching"""
    
    def __init__(self, db: AsyncSession, tenant_context: TenantContext):
        self.db = db
        self.tenant_context = tenant_context
        self.tenant_service = TenantAwareService(db, tenant_context)
    
    def _generate_cache_key(self, entity_type: str, params: Dict[str, Any]) -> str:
        """Generate cache key for search results"""
        # Normalize parameters for consistent caching
        normalized = {
            'entity': entity_type,
            'tenant': self.tenant_context.company_id,
            'q': params.get('q', ''),
            'filters': json.dumps(params.get('filters', {}), sort_keys=True),
            'sort': params.get('sort', ''),
            'page': params.get('page', 1),
            'limit': params.get('limit', 20)
        }
        
        # Create hash of normalized parameters
        cache_str = json.dumps(normalized, sort_keys=True)
        return f"search:{hashlib.md5(cache_str.encode()).hexdigest()}"
    
    def _parse_sort_params(self, sort_string: str) -> List[Tuple[str, str]]:
        """Parse sort string into field and direction tuples"""
        if not sort_string:
            return []
        
        sorts = []
        for item in sort_string.split(','):
            item = item.strip()
            if item.startswith('-'):
                sorts.append((item[1:], 'desc'))
            else:
                sorts.append((item, 'asc'))
        
        return sorts
    
    def _apply_sorting(self, query, model_class, sort_params: List[Tuple[str, str]], 
                      has_fts_rank: bool = False):
        """Apply sorting to query"""
        if not sort_params:
            # Default sorting: relevance if FTS, then by updated_at desc
            if has_fts_rank:
                return query.order_by(desc(text('ts_rank')), desc(model_class.updated_at))
            else:
                return query.order_by(desc(model_class.updated_at))
        
        order_clauses = []
        
        # Add relevance ranking first if we have FTS
        if has_fts_rank:
            order_clauses.append(desc(text('ts_rank')))
        
        for field, direction in sort_params:
            if not hasattr(model_class, field):
                continue
                
            column = getattr(model_class, field)
            if direction == 'desc':
                order_clauses.append(desc(column))
            else:
                order_clauses.append(asc(column))
        
        return query.order_by(*order_clauses)
    
    async def _search_contacts_fts(self, search_query: SearchQuery, filters: SearchFilters,
                                 sort_params: List[Tuple[str, str]], page: int, limit: int) -> Dict[str, Any]:
        """Full-text search for contacts"""
        tsquery = search_query.to_tsquery()
        
        # Base query with FTS ranking
        base_query = select(
            Contact,
            func.ts_rank(Contact.search_vector, func.to_tsquery('english', tsquery)).label('ts_rank')
        ).where(
            and_(
                Contact.company_id == self.tenant_context.company_id,
                Contact.search_vector.op('@@')(func.to_tsquery('english', tsquery))
            )
        )
        
        # Apply filters
        filter_conditions = filters.get_sql_conditions(Contact)
        if filter_conditions:
            base_query = base_query.where(and_(*filter_conditions))
        
        # Count total results
        count_query = select(func.count()).select_from(
            base_query.subquery()
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting and pagination
        query = self._apply_sorting(base_query, Contact, sort_params, has_fts_rank=True)
        query = query.offset((page - 1) * limit).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        contacts = [row[0] for row in rows]  # Extract Contact objects
        
        return {
            'results': contacts,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    async def _search_contacts_fuzzy(self, search_query: SearchQuery, filters: SearchFilters,
                                   sort_params: List[Tuple[str, str]], page: int, limit: int) -> Dict[str, Any]:
        """Fuzzy search for contacts using trigram similarity"""
        terms = search_query.to_fuzzy_terms()
        
        if not terms:
            # No search terms, just apply filters
            base_query = select(Contact).where(
                Contact.company_id == self.tenant_context.company_id
            )
        else:
            # Build fuzzy search conditions
            fuzzy_conditions = []
            for term in terms:
                if term.startswith('-'):
                    # Exclusion - skip for fuzzy search
                    continue
                    
                term_conditions = or_(
                    Contact.name.op('%')(term),  # pg_trgm similarity
                    Contact.email.ilike(f'%{term}%'),
                    Contact.company.ilike(f'%{term}%'),
                    Contact.phone.ilike(f'%{term}%')
                )
                fuzzy_conditions.append(term_conditions)
            
            if fuzzy_conditions:
                base_query = select(Contact).where(
                    and_(
                        Contact.company_id == self.tenant_context.company_id,
                        or_(*fuzzy_conditions)
                    )
                )
            else:
                base_query = select(Contact).where(
                    Contact.company_id == self.tenant_context.company_id
                )
        
        # Apply filters
        filter_conditions = filters.get_sql_conditions(Contact)
        if filter_conditions:
            base_query = base_query.where(and_(*filter_conditions))
        
        # Count total results
        count_query = select(func.count()).select_from(
            base_query.subquery()
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting and pagination
        query = self._apply_sorting(base_query, Contact, sort_params, has_fts_rank=False)
        query = query.offset((page - 1) * limit).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        contacts = result.scalars().all()
        
        return {
            'results': contacts,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    async def _search_products_fts(self, search_query: SearchQuery, filters: SearchFilters,
                                 sort_params: List[Tuple[str, str]], page: int, limit: int) -> Dict[str, Any]:
        """Full-text search for products"""
        tsquery = search_query.to_tsquery()
        
        # Base query with FTS ranking
        base_query = select(
            Product,
            func.ts_rank(Product.search_vector, func.to_tsquery('english', tsquery)).label('ts_rank')
        ).where(
            and_(
                Product.company_id == self.tenant_context.company_id,
                Product.search_vector.op('@@')(func.to_tsquery('english', tsquery))
            )
        )
        
        # Apply filters
        filter_conditions = filters.get_sql_conditions(Product)
        if filter_conditions:
            base_query = base_query.where(and_(*filter_conditions))
        
        # Count total results
        count_query = select(func.count()).select_from(
            base_query.subquery()
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting and pagination
        query = self._apply_sorting(base_query, Product, sort_params, has_fts_rank=True)
        query = query.offset((page - 1) * limit).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        rows = result.fetchall()
        
        products = [row[0] for row in rows]  # Extract Product objects
        
        return {
            'results': products,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    async def _search_products_fuzzy(self, search_query: SearchQuery, filters: SearchFilters,
                                   sort_params: List[Tuple[str, str]], page: int, limit: int) -> Dict[str, Any]:
        """Fuzzy search for products using trigram similarity"""
        terms = search_query.to_fuzzy_terms()
        
        if not terms:
            # No search terms, just apply filters
            base_query = select(Product).where(
                Product.company_id == self.tenant_context.company_id
            )
        else:
            # Build fuzzy search conditions
            fuzzy_conditions = []
            for term in terms:
                if term.startswith('-'):
                    # Exclusion - skip for fuzzy search
                    continue
                    
                term_conditions = or_(
                    Product.name.op('%')(term),  # pg_trgm similarity
                    Product.sku.ilike(f'%{term}%'),
                    Product.description.ilike(f'%{term}%'),
                    Product.category.ilike(f'%{term}%'),
                    Product.brand.ilike(f'%{term}%')
                )
                fuzzy_conditions.append(term_conditions)
            
            if fuzzy_conditions:
                base_query = select(Product).where(
                    and_(
                        Product.company_id == self.tenant_context.company_id,
                        or_(*fuzzy_conditions)
                    )
                )
            else:
                base_query = select(Product).where(
                    Product.company_id == self.tenant_context.company_id
                )
        
        # Apply filters
        filter_conditions = filters.get_sql_conditions(Product)
        if filter_conditions:
            base_query = base_query.where(and_(*filter_conditions))
        
        # Count total results
        count_query = select(func.count()).select_from(
            base_query.subquery()
        )
        total_result = await self.db.execute(count_query)
        total = total_result.scalar()
        
        # Apply sorting and pagination
        query = self._apply_sorting(base_query, Product, sort_params, has_fts_rank=False)
        query = query.offset((page - 1) * limit).limit(limit)
        
        # Execute query
        result = await self.db.execute(query)
        products = result.scalars().all()
        
        return {
            'results': products,
            'total': total,
            'page': page,
            'limit': limit
        }
    
    async def _get_contact_facets(self, search_query: Optional[SearchQuery] = None) -> Dict[str, Dict[str, int]]:
        """Generate facet counts for contacts"""
        base_conditions = [Contact.company_id == self.tenant_context.company_id]
        
        # Add search conditions if provided
        if search_query and search_query.has_content():
            tsquery = search_query.to_tsquery()
            if tsquery:
                try:
                    base_conditions.append(
                        Contact.search_vector.op('@@')(func.to_tsquery('english', tsquery))
                    )
                except Exception:
                    # Fall back to fuzzy search conditions
                    terms = search_query.to_fuzzy_terms()
                    if terms:
                        fuzzy_conditions = []
                        for term in terms[:3]:  # Limit terms for performance
                            if not term.startswith('-'):
                                term_conditions = or_(
                                    Contact.name.ilike(f'%{term}%'),
                                    Contact.email.ilike(f'%{term}%'),
                                    Contact.company.ilike(f'%{term}%')
                                )
                                fuzzy_conditions.append(term_conditions)
                        if fuzzy_conditions:
                            base_conditions.append(or_(*fuzzy_conditions))
        
        facets = {}
        
        # Status facets
        status_query = select(
            Contact.status,
            func.count().label('count')
        ).where(
            and_(*base_conditions)
        ).group_by(Contact.status)
        
        result = await self.db.execute(status_query)
        facets['status'] = {row.status: row.count for row in result.fetchall() if row.status}
        
        # Tags facets (limit to top 10)
        tags_query = select(
            func.unnest(Contact.tags).label('tag'),
            func.count().label('count')
        ).where(
            and_(*base_conditions, Contact.tags.isnot(None))
        ).group_by(text('tag')).order_by(desc(text('count'))).limit(10)
        
        result = await self.db.execute(tags_query)
        facets['tags'] = {row.tag: row.count for row in result.fetchall() if row.tag}
        
        return facets
    
    async def _get_product_facets(self, search_query: Optional[SearchQuery] = None) -> Dict[str, Dict[str, int]]:
        """Generate facet counts for products"""
        base_conditions = [Product.company_id == self.tenant_context.company_id]
        
        # Add search conditions if provided
        if search_query and search_query.has_content():
            tsquery = search_query.to_tsquery()
            if tsquery:
                try:
                    base_conditions.append(
                        Product.search_vector.op('@@')(func.to_tsquery('english', tsquery))
                    )
                except Exception:
                    # Fall back to fuzzy search conditions
                    terms = search_query.to_fuzzy_terms()
                    if terms:
                        fuzzy_conditions = []
                        for term in terms[:3]:  # Limit terms for performance
                            if not term.startswith('-'):
                                term_conditions = or_(
                                    Product.name.ilike(f'%{term}%'),
                                    Product.sku.ilike(f'%{term}%'),
                                    Product.category.ilike(f'%{term}%')
                                )
                                fuzzy_conditions.append(term_conditions)
                        if fuzzy_conditions:
                            base_conditions.append(or_(*fuzzy_conditions))
        
        facets = {}
        
        # Category facets
        category_query = select(
            Product.category,
            func.count().label('count')
        ).where(
            and_(*base_conditions)
        ).group_by(Product.category)
        
        result = await self.db.execute(category_query)
        facets['category'] = {row.category: row.count for row in result.fetchall() if row.category}
        
        # Stock status facets
        stock_query = select(
            func.case(
                (Product.stock_quantity == 0, 'out_of_stock'),
                (Product.stock_quantity < Product.low_stock_threshold, 'low_stock'),
                else_='in_stock'
            ).label('stock_status'),
            func.count().label('count')
        ).where(
            and_(*base_conditions)
        ).group_by(text('stock_status'))
        
        result = await self.db.execute(stock_query)
        facets['stock_status'] = {row.stock_status: row.count for row in result.fetchall()}
        
        # Price range facets
        price_ranges = [
            ('0-10', 0, 10),
            ('10-50', 10, 50),
            ('50-100', 50, 100),
            ('100-500', 100, 500),
            ('500+', 500, float('inf'))
        ]
        
        price_facets = {}
        for label, min_price, max_price in price_ranges:
            price_conditions = base_conditions + [Product.price >= min_price]
            if max_price != float('inf'):
                price_conditions.append(Product.price < max_price)
            
            price_query = select(func.count()).where(and_(*price_conditions))
            result = await self.db.execute(price_query)
            count = result.scalar()
            if count > 0:
                price_facets[label] = count
        
        facets['price_range'] = price_facets
        
        return facets
    
    async def search_contacts(self, q: str = '', filters: Optional[Dict[str, Any]] = None,
                            sort: str = '', page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Search contacts with full-text search and facets"""
        search_query = SearchQuery(q)
        search_filters = SearchFilters(filters)
        sort_params = self._parse_sort_params(sort)
        
        # Limit page size for performance
        limit = min(limit, 100)
        page = max(page, 1)
        
        # Try full-text search first if we have a query
        results = None
        if search_query.has_content():
            try:
                results = await self._search_contacts_fts(
                    search_query, search_filters, sort_params, page, limit
                )
            except Exception as e:
                logger.warning(f"FTS search failed, falling back to fuzzy: {e}")
                results = await self._search_contacts_fuzzy(
                    search_query, search_filters, sort_params, page, limit
                )
        else:
            # No query, just filter and sort
            results = await self._search_contacts_fuzzy(
                search_query, search_filters, sort_params, page, limit
            )
        
        # Add facets
        facets = await self._get_contact_facets(search_query if search_query.has_content() else None)
        results['facets'] = {'contacts': facets}
        
        return results
    
    async def search_products(self, q: str = '', filters: Optional[Dict[str, Any]] = None,
                            sort: str = '', page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """Search products with full-text search and facets"""
        search_query = SearchQuery(q)
        search_filters = SearchFilters(filters)
        sort_params = self._parse_sort_params(sort)
        
        # Limit page size for performance
        limit = min(limit, 100)
        page = max(page, 1)
        
        # Try full-text search first if we have a query
        results = None
        if search_query.has_content():
            try:
                results = await self._search_products_fts(
                    search_query, search_filters, sort_params, page, limit
                )
            except Exception as e:
                logger.warning(f"FTS search failed, falling back to fuzzy: {e}")
                results = await self._search_products_fuzzy(
                    search_query, search_filters, sort_params, page, limit
                )
        else:
            # No query, just filter and sort
            results = await self._search_products_fuzzy(
                search_query, search_filters, sort_params, page, limit
            )
        
        # Add facets
        facets = await self._get_product_facets(search_query if search_query.has_content() else None)
        results['facets'] = {'products': facets}
        
        return results