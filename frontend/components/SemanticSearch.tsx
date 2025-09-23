"use client";

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api';
import { useState } from 'react';
import { toast } from 'react-hot-toast';

interface SearchResult {
  entity_type: string;
  entity_id: string;
  content: string;
  similarity_score: number;
  metadata: Record<string, any>;
}

export function SemanticSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error("Please enter a search query.");
      return;
    }
    setIsLoading(true);
    try {
      const response = await api.post('/ai/semantic-search', { query });
      setResults(response.data.results);
      if (response.data.results.length === 0) {
        toast.success("No results found.");
      }
    } catch (error) {
      toast.error("Search failed.");
      console.error(error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Semantic Search</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex w-full max-w-sm items-center space-x-2">
          <Input
            type="text"
            placeholder="Search for products, contacts, orders..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <Button onClick={handleSearch} disabled={isLoading}>
            {isLoading ? "Searching..." : "Search"}
          </Button>
        </div>
        <div className="mt-6 space-y-4">
          {results.map((result) => (
            <div key={result.entity_id} className="p-4 border rounded-lg">
              <div className="flex justify-between items-center">
                <p className="font-bold text-lg">{result.metadata.name || result.entity_type}</p>
                <p className="text-sm text-gray-500">
                  Similarity: {(result.similarity_score * 100).toFixed(2)}%
                </p>
              </div>
              <p className="text-gray-700 mt-1">{result.content}</p>
              <p className="text-xs text-gray-400 mt-2">
                Type: {result.entity_type} | ID: {result.entity_id}
              </p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
