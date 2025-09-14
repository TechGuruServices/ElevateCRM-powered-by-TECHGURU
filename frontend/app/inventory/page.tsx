"use client"

import React, { useState } from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { 
  Package,
  Warehouse,
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  Search,
  Filter,
  Plus,
  Download,
  RefreshCw,
  BarChart3,
  Settings,
  Zap,
  Clock,
  CheckCircle,
  XCircle,
  Eye,
  Edit,
  Trash2,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react'

export default function InventoryPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const categories = [
    { id: 'all', name: 'All Items', count: 1247 },
    { id: 'electronics', name: 'Electronics', count: 423 },
    { id: 'clothing', name: 'Clothing', count: 312 },
    { id: 'furniture', name: 'Furniture', count: 189 },
    { id: 'books', name: 'Books', count: 156 },
    { id: 'sports', name: 'Sports', count: 167 }
  ]

  const inventoryItems = [
    {
      id: 'ELEC001',
      name: 'iPhone 15 Pro',
      category: 'Electronics',
      sku: 'IP15P-128-BL',
      quantity: 45,
      minStock: 10,
      price: 999.99,
      value: 44999.55,
      location: 'Warehouse A - A1-B3',
      status: 'in-stock',
      lastUpdated: '2 hours ago',
      supplier: 'Apple Inc.'
    },
    {
      id: 'CLOTH002',
      name: 'Premium Cotton T-Shirt',
      category: 'Clothing',
      sku: 'CT-PREM-M-BLK',
      quantity: 8,
      minStock: 15,
      price: 29.99,
      value: 239.92,
      location: 'Warehouse B - C2-D1',
      status: 'low-stock',
      lastUpdated: '4 hours ago',
      supplier: 'Fashion Co.'
    },
    {
      id: 'FURN003',
      name: 'Ergonomic Office Chair',
      category: 'Furniture',
      sku: 'EOC-BLK-ADJ',
      quantity: 0,
      minStock: 5,
      price: 299.99,
      value: 0,
      location: 'Warehouse A - B3-C2',
      status: 'out-of-stock',
      lastUpdated: '1 day ago',
      supplier: 'Office Solutions'
    },
    {
      id: 'BOOK004',
      name: 'JavaScript: The Complete Guide',
      category: 'Books',
      sku: 'JS-GUIDE-2024',
      quantity: 23,
      minStock: 10,
      price: 49.99,
      value: 1149.77,
      location: 'Warehouse C - A1-A2',
      status: 'in-stock',
      lastUpdated: '6 hours ago',
      supplier: 'Tech Books Ltd.'
    },
    {
      id: 'SPORT005',
      name: 'Professional Basketball',
      category: 'Sports',
      sku: 'BB-PRO-ORG',
      quantity: 67,
      minStock: 20,
      price: 89.99,
      value: 6029.33,
      location: 'Warehouse B - D1-E2',
      status: 'in-stock',
      lastUpdated: '3 hours ago',
      supplier: 'Sports World'
    }
  ]

  const getStatusBadge = (status: string, quantity: number, minStock: number) => {
    if (status === 'out-of-stock' || quantity === 0) {
      return <Badge variant="destructive">Out of Stock</Badge>
    } else if (quantity <= minStock) {
      return <Badge variant="warning">Low Stock</Badge>
    } else {
      return <Badge variant="success">In Stock</Badge>
    }
  }

  const getStatusIcon = (status: string, quantity: number, minStock: number) => {
    if (status === 'out-of-stock' || quantity === 0) {
      return <XCircle className="h-4 w-4 text-red-500" />
    } else if (quantity <= minStock) {
      return <AlertTriangle className="h-4 w-4 text-yellow-500" />
    } else {
      return <CheckCircle className="h-4 w-4 text-green-500" />
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
              Inventory Management
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-1">
              Track your products, stock levels, and warehouse locations
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button variant="outline" className="hidden sm:flex">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" className="hidden sm:flex">
              <BarChart3 className="h-4 w-4 mr-2" />
              Analytics
            </Button>
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              <Plus className="h-4 w-4 mr-2" />
              Add Product
            </Button>
          </div>
        </div>

        {/* Inventory Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-blue-900 dark:text-blue-100">
                Total Products
              </CardTitle>
              <Package className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">1,247</div>
              <div className="flex items-center text-xs text-blue-700 dark:text-blue-300 mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                +5.2% from last month
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-green-900 dark:text-green-100">
                Total Value
              </CardTitle>
              <BarChart3 className="h-4 w-4 text-green-600 dark:text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-900 dark:text-green-100">$2.4M</div>
              <div className="flex items-center text-xs text-green-700 dark:text-green-300 mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                +12.3% from last month
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 dark:from-yellow-900/20 dark:to-yellow-800/20 border-yellow-200 dark:border-yellow-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                Low Stock Alert
              </CardTitle>
              <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-yellow-900 dark:text-yellow-100">23</div>
              <div className="flex items-center text-xs text-yellow-700 dark:text-yellow-300 mt-1">
                <TrendingDown className="h-3 w-3 mr-1" />
                -8 from yesterday
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-purple-900 dark:text-purple-100">
                Warehouses
              </CardTitle>
              <Warehouse className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">3</div>
              <div className="flex items-center text-xs text-purple-700 dark:text-purple-300 mt-1">
                <CheckCircle className="h-3 w-3 mr-1" />
                All operational
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters and Search */}
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <Input
                placeholder="Search products, SKUs, or categories..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
            <Button variant="outline">
              <Settings className="h-4 w-4 mr-2" />
              Columns
            </Button>
          </div>
        </div>

        {/* Category Tabs */}
        <div className="flex gap-2 overflow-x-auto pb-2">
          {categories.map((category) => (
            <Button
              key={category.id}
              variant={selectedCategory === category.id ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedCategory(category.id)}
              className="whitespace-nowrap"
            >
              {category.name}
              <Badge variant="secondary" className="ml-2">
                {category.count}
              </Badge>
            </Button>
          ))}
        </div>

        {/* Inventory Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Product Inventory</CardTitle>
                <CardDescription>
                  Monitor stock levels and manage your product catalog
                </CardDescription>
              </div>
              <Button variant="ghost" size="sm">
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200 dark:border-slate-700">
                    <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400">Product</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400">SKU</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400">Stock</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400">Price</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400">Value</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400">Location</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400">Status</th>
                    <th className="text-left py-3 px-4 font-medium text-slate-500 dark:text-slate-400">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {inventoryItems.map((item) => (
                    <tr 
                      key={item.id} 
                      className="border-b border-slate-100 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800/50"
                    >
                      <td className="py-4 px-4">
                        <div>
                          <div className="font-medium text-slate-900 dark:text-white">
                            {item.name}
                          </div>
                          <div className="text-sm text-slate-500 dark:text-slate-400">
                            {item.category}
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <code className="text-sm bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
                          {item.sku}
                        </code>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(item.status, item.quantity, item.minStock)}
                          <div>
                            <div className="font-medium text-slate-900 dark:text-white">
                              {item.quantity}
                            </div>
                            <div className="text-xs text-slate-500 dark:text-slate-400">
                              Min: {item.minStock}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="font-medium text-slate-900 dark:text-white">
                          ${item.price.toFixed(2)}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="font-medium text-slate-900 dark:text-white">
                          ${item.value.toLocaleString()}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="text-sm text-slate-600 dark:text-slate-300">
                          {item.location}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        {getStatusBadge(item.status, item.quantity, item.minStock)}
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-2">
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between">
              <div className="text-sm text-slate-500 dark:text-slate-400">
                Showing 5 of 1,247 products
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm" disabled>
                  Previous
                </Button>
                <Button variant="outline" size="sm">
                  Next
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions & Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
              <CardDescription>
                Common inventory management tasks
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start">
                <Plus className="h-4 w-4 mr-2" />
                Add New Product
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Download className="h-4 w-4 mr-2" />
                Import Inventory
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Zap className="h-4 w-4 mr-2" />
                Bulk Update
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <BarChart3 className="h-4 w-4 mr-2" />
                Generate Report
              </Button>
            </CardContent>
          </Card>

          {/* Stock Alerts */}
          <Card>
            <CardHeader>
              <CardTitle>Stock Alerts</CardTitle>
              <CardDescription>
                Products requiring immediate attention
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
                <div className="flex items-center space-x-3">
                  <XCircle className="h-4 w-4 text-red-500" />
                  <div>
                    <p className="text-sm font-medium text-red-900 dark:text-red-100">
                      Out of Stock
                    </p>
                    <p className="text-xs text-red-700 dark:text-red-300">
                      5 products
                    </p>
                  </div>
                </div>
                <Badge variant="destructive">Critical</Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                <div className="flex items-center space-x-3">
                  <AlertTriangle className="h-4 w-4 text-yellow-500" />
                  <div>
                    <p className="text-sm font-medium text-yellow-900 dark:text-yellow-100">
                      Low Stock
                    </p>
                    <p className="text-xs text-yellow-700 dark:text-yellow-300">
                      18 products
                    </p>
                  </div>
                </div>
                <Badge variant="warning">Warning</Badge>
              </div>

              <div className="flex items-center justify-between p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <div className="flex items-center space-x-3">
                  <Clock className="h-4 w-4 text-blue-500" />
                  <div>
                    <p className="text-sm font-medium text-blue-900 dark:text-blue-100">
                      Reorder Soon
                    </p>
                    <p className="text-xs text-blue-700 dark:text-blue-300">
                      12 products
                    </p>
                  </div>
                </div>
                <Badge variant="info">Info</Badge>
              </div>
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
              <CardDescription>
                Latest inventory movements and updates
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {[
                {
                  action: "Stock Updated",
                  product: "iPhone 15 Pro",
                  change: "+25 units",
                  time: "2 hours ago",
                  type: "increase"
                },
                {
                  action: "Product Added",
                  product: "Wireless Headphones",
                  change: "New product",
                  time: "4 hours ago",
                  type: "new"
                },
                {
                  action: "Stock Sold",
                  product: "Cotton T-Shirt",
                  change: "-12 units",
                  time: "6 hours ago",
                  type: "decrease"
                },
                {
                  action: "Price Updated",
                  product: "Office Chair",
                  change: "$299.99",
                  time: "1 day ago",
                  type: "update"
                }
              ].map((activity, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                  <div className={`w-2 h-2 rounded-full ${
                    activity.type === 'increase' ? 'bg-green-500' :
                    activity.type === 'decrease' ? 'bg-red-500' :
                    activity.type === 'new' ? 'bg-blue-500' : 'bg-yellow-500'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 dark:text-white">
                      {activity.action}
                    </p>
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      {activity.product} • {activity.change}
                    </p>
                  </div>
                  <div className="text-xs text-slate-400">
                    {activity.time}
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}