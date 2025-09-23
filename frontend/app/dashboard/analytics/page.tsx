"use client";

import { SemanticSearch } from '@/components/SemanticSearch';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { api } from '@/lib/api';
import { useState } from 'react';
import { toast } from 'react-hot-toast';

import { Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

// Mock data until API is fully integrated
const mockForecastData = [
  { name: 'Week 1', demand: 4000 },
  { name: 'Week 2', demand: 3000 },
  { name: 'Week 3', demand: 2000 },
  { name: 'Week 4', demand: 2780 },
];

const mockLeadScores = [
  { name: 'New Leads', score: 75 },
  { name: 'Contacted Leads', score: 60 },
  { name: 'Qualified Leads', score: 85 },
];

const mockChurnData = [
    { name: 'Jan', churnRate: 4.0 },
    { name: 'Feb', churnRate: 3.0 },
    { name: 'Mar', churnRate: 5.0 },
    { name: 'Apr', churnRate: 4.5 },
];

export default function AnalyticsPage() {
  const [forecastData, setForecastData] = useState(mockForecastData);
  const [leadScores, setLeadScores] = useState(mockLeadScores);
  const [churnData, setChurnData] = useState(mockChurnData);
  const [selectedProduct, setSelectedProduct] = useState<string | null>(null);

  const handleForecast = async () => {
    if (!selectedProduct) {
      toast.error("Please select a product to forecast.");
      return;
    }
    try {
      const response = await api.post('/ai/forecast', { product_id: selectedProduct });
      // This is a simplified representation. You'd likely get a more complex object.
      const newForecast = { name: 'Next Month', demand: response.data.predicted_demand };
      setForecastData(prev => [...prev.slice(-3), newForecast]);
      toast.success("Demand forecast updated!");
    } catch (error) {
      toast.error("Failed to fetch forecast.");
      console.error(error);
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">AI & Analytics Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

        <Card className="col-span-1 md:col-span-2">
          <CardHeader>
            <CardTitle>Demand Forecast</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={forecastData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="demand" stroke="#8884d8" activeDot={{ r: 8 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 flex items-center gap-4">
                <Select onValueChange={setSelectedProduct}>
                    <SelectTrigger>
                        <SelectValue placeholder="Select a Product" />
                    </SelectTrigger>
                    <SelectContent>
                        {/* This should be populated from your products API */}
                        <SelectItem value="a1b2c3d4-e5f6-7890-1234-567890abcdef">Product A</SelectItem>
                        <SelectItem value="b2c3d4e5-f6a7-8901-2345-67890abcdef0">Product B</SelectItem>
                    </SelectContent>
                </Select>
                <Button onClick={handleForecast}>Forecast</Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Lead Scores</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={leadScores} layout="vertical">
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis type="number" />
                        <YAxis type="category" dataKey="name" width={120} />
                        <Tooltip />
                        <Legend />
                        <Bar dataKey="score" fill="#82ca9d" />
                    </BarChart>
                </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Churn Rate</CardTitle>
          </CardHeader>
          <CardContent>
             <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={churnData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="name" />
                        <YAxis />
                        <Tooltip />
                        <Legend />
                        <Line type="monotone" dataKey="churnRate" stroke="#ff7300" />
                    </LineChart>
                </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        <Card className="col-span-1 md:col-span-3">
          <CardHeader>
            <CardTitle>Product Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            {/* Recommendations would be fetched and displayed here */}
            <p>Recommendations feature coming soon.</p>
          </CardContent>
        </Card>

        <div className="col-span-1 md:col-span-3">
          <SemanticSearch />
        </div>

      </div>
    </div>
  );
}
