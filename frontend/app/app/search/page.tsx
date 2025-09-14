'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Search, Users, Package, ArrowRight } from 'lucide-react';

export default function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <Search className="h-16 w-16 text-blue-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Search Everything
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300">
            Find contacts, products, and more with our powerful search engine
          </p>
        </div>

        {/* Quick Search */}
        <div className="mb-12">
          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search across all your data..."
              className="w-full pl-12 pr-4 py-4 text-lg border border-gray-300 rounded-xl 
                       focus:ring-2 focus:ring-blue-500 focus:border-blue-500 
                       bg-white dark:bg-gray-800 dark:border-gray-700 
                       text-gray-900 dark:text-white placeholder-gray-500"
            />
          </div>
        </div>

        {/* Search Categories */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* Contact Search */}
          <Link 
            href="/app/search/contacts"
            className="group block bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between mb-6">
              <Users className="h-12 w-12 text-blue-600" />
              <ArrowRight className="h-6 w-6 text-gray-400 group-hover:text-blue-600 transition-colors" />
            </div>
            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-3">
              Search Contacts
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Find contacts by name, email, company, or any other information.
              Use advanced filters to narrow down your results.
            </p>
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm rounded-full">
                Name search
              </span>
              <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm rounded-full">
                Company filter
              </span>
              <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-sm rounded-full">
                Status filter
              </span>
            </div>
          </Link>

          {/* Product Search */}
          <Link 
            href="/app/search/products"
            className="group block bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between mb-6">
              <Package className="h-12 w-12 text-green-600" />
              <ArrowRight className="h-6 w-6 text-gray-400 group-hover:text-green-600 transition-colors" />
            </div>
            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-3">
              Search Products
            </h3>
            <p className="text-gray-600 dark:text-gray-300 mb-4">
              Search your inventory by product name, SKU, description, or category.
              Find products quickly with intelligent search.
            </p>
            <div className="flex flex-wrap gap-2">
              <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-sm rounded-full">
                SKU search
              </span>
              <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-sm rounded-full">
                Category filter
              </span>
              <span className="px-3 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-sm rounded-full">
                Price range
              </span>
            </div>
          </Link>
        </div>

        {/* Search Tips */}
        <div className="mt-12 bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-8">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Search Tips
          </h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm text-gray-600 dark:text-gray-300">
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                Basic Search
              </h4>
              <ul className="space-y-1">
                <li>• Type keywords to find matches</li>
                <li>• Search works across all text fields</li>
                <li>• Results are ranked by relevance</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 dark:text-white mb-2">
                Advanced Features
              </h4>
              <ul className="space-y-1">
                <li>• Use filters to narrow results</li>
                <li>• Sort by different criteria</li>
                <li>• Recent searches are saved</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}