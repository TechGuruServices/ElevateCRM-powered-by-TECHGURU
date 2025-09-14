"use client"

import React from 'react'
import { DashboardLayout } from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  TrendingUp, 
  TrendingDown, 
  Users, 
  Package, 
  ShoppingCart, 
  DollarSign,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  Plus,
  Filter,
  Calendar,
  Download,
  RefreshCw,
  AlertCircle,
  CheckCircle,
  Clock,
  Star
} from 'lucide-react'

export default function CustomerManagementPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
              Customer Management
            </h1>
            <p className="text-slate-600 dark:text-slate-400 mt-1">
              Manage your customer relationships and track interactions
            </p>
          </div>
          <div className="flex items-center space-x-3">
            <Button variant="outline" className="hidden sm:flex">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
            <Button variant="outline" className="hidden sm:flex">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700">
              <Plus className="h-4 w-4 mr-2" />
              Add Customer
            </Button>
          </div>
        </div>

        {/* Customer Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/20 border-blue-200 dark:border-blue-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-blue-900 dark:text-blue-100">
                Total Customers
              </CardTitle>
              <Users className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-blue-900 dark:text-blue-100">2,847</div>
              <div className="flex items-center text-xs text-blue-700 dark:text-blue-300 mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                +12.5% from last month
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-green-200 dark:border-green-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-green-900 dark:text-green-100">
                Active Customers
              </CardTitle>
              <Activity className="h-4 w-4 text-green-600 dark:text-green-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-900 dark:text-green-100">1,924</div>
              <div className="flex items-center text-xs text-green-700 dark:text-green-300 mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                +8.2% from last month
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border-purple-200 dark:border-purple-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-purple-900 dark:text-purple-100">
                New This Month
              </CardTitle>
              <Plus className="h-4 w-4 text-purple-600 dark:text-purple-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-purple-900 dark:text-purple-100">189</div>
              <div className="flex items-center text-xs text-purple-700 dark:text-purple-300 mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                +23.1% from last month
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-900/20 dark:to-orange-800/20 border-orange-200 dark:border-orange-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-orange-900 dark:text-orange-100">
                Avg. Value
              </CardTitle>
              <DollarSign className="h-4 w-4 text-orange-600 dark:text-orange-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-900 dark:text-orange-100">$4,892</div>
              <div className="flex items-center text-xs text-orange-700 dark:text-orange-300 mt-1">
                <TrendingUp className="h-3 w-3 mr-1" />
                +5.4% from last month
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Customer List */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Customer Table */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Recent Customers</CardTitle>
                    <CardDescription>
                      Latest customer registrations and updates
                    </CardDescription>
                  </div>
                  <Button variant="ghost" size="sm">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {[
                    {
                      name: "Acme Corporation",
                      contact: "John Smith",
                      email: "john@acme.com",
                      status: "active",
                      value: "$12,500",
                      lastContact: "2 hours ago",
                      rating: 5
                    },
                    {
                      name: "Tech Innovations Ltd",
                      contact: "Sarah Johnson",
                      email: "sarah@techinnovations.com",
                      status: "prospect",
                      value: "$8,750",
                      lastContact: "1 day ago",
                      rating: 4
                    },
                    {
                      name: "Global Solutions Inc",
                      contact: "Mike Chen",
                      email: "mike@globalsolutions.com",
                      status: "active",
                      value: "$15,200",
                      lastContact: "3 days ago",
                      rating: 5
                    },
                    {
                      name: "StartUp Ventures",
                      contact: "Emma Wilson",
                      email: "emma@startupventures.com",
                      status: "lead",
                      value: "$3,400",
                      lastContact: "5 days ago",
                      rating: 3
                    },
                    {
                      name: "Enterprise Systems",
                      contact: "David Brown",
                      email: "david@enterprise.com",
                      status: "active",
                      value: "$22,800",
                      lastContact: "1 week ago",
                      rating: 5
                    }
                  ].map((customer, index) => (
                    <div 
                      key={index}
                      className="flex items-center justify-between p-4 border border-slate-200 dark:border-slate-700 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors cursor-pointer"
                    >
                      <div className="flex items-center space-x-4">
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold">
                          {customer.name.charAt(0)}
                        </div>
                        <div>
                          <h3 className="font-medium text-slate-900 dark:text-white">
                            {customer.name}
                          </h3>
                          <div className="flex items-center space-x-2 text-sm text-slate-500 dark:text-slate-400">
                            <span>{customer.contact}</span>
                            <span>•</span>
                            <span>{customer.email}</span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-right">
                          <div className="font-medium text-slate-900 dark:text-white">
                            {customer.value}
                          </div>
                          <div className="text-sm text-slate-500 dark:text-slate-400">
                            {customer.lastContact}
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="flex">
                            {[...Array(5)].map((_, i) => (
                              <Star 
                                key={i} 
                                className={`h-3 w-3 ${
                                  i < customer.rating 
                                    ? 'text-yellow-400 fill-current' 
                                    : 'text-slate-300 dark:text-slate-600'
                                }`}
                              />
                            ))}
                          </div>
                          <Badge 
                            variant={
                              customer.status === 'active' ? 'success' :
                              customer.status === 'prospect' ? 'warning' : 'info'
                            }
                          >
                            {customer.status}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-700">
                  <Button variant="outline" className="w-full">
                    View All Customers
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Customer Insights */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
                <CardDescription>
                  Common customer management tasks
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <Button variant="outline" className="w-full justify-start">
                  <Plus className="h-4 w-4 mr-2" />
                  Import Customers
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Calendar className="h-4 w-4 mr-2" />
                  Schedule Follow-up
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Download className="h-4 w-4 mr-2" />
                  Export Data
                </Button>
                <Button variant="outline" className="w-full justify-start">
                  <Activity className="h-4 w-4 mr-2" />
                  Customer Analytics
                </Button>
              </CardContent>
            </Card>

            {/* Customer Status */}
            <Card>
              <CardHeader>
                <CardTitle>Customer Status Overview</CardTitle>
                <CardDescription>
                  Current distribution of customer statuses
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full" />
                    <span className="text-sm">Active</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">1,924</span>
                    <Badge variant="success">67.6%</Badge>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                    <span className="text-sm">Prospects</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">534</span>
                    <Badge variant="warning">18.7%</Badge>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full" />
                    <span className="text-sm">Leads</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">289</span>
                    <Badge variant="info">10.1%</Badge>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-slate-400 rounded-full" />
                    <span className="text-sm">Inactive</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-medium">100</span>
                    <Badge variant="secondary">3.6%</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Upcoming Tasks */}
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Tasks</CardTitle>
                <CardDescription>
                  Customer-related tasks and follow-ups
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  {
                    task: "Follow up with Acme Corp",
                    time: "Today, 2:00 PM",
                    priority: "high"
                  },
                  {
                    task: "Send proposal to Tech Innovations",
                    time: "Tomorrow, 10:00 AM",
                    priority: "medium"
                  },
                  {
                    task: "Schedule demo for StartUp Ventures",
                    time: "Dec 15, 3:00 PM",
                    priority: "low"
                  }
                ].map((task, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 bg-slate-50 dark:bg-slate-800/50 rounded-lg">
                    <div className={`w-2 h-2 rounded-full ${
                      task.priority === 'high' ? 'bg-red-500' :
                      task.priority === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 dark:text-white">
                        {task.task}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {task.time}
                      </p>
                    </div>
                    <Clock className="h-4 w-4 text-slate-400" />
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  )
}