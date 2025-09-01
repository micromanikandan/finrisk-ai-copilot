'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  AlertTriangle,
  CheckCircle,
  XCircle,
  Plus
} from 'lucide-react'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

interface CaseStatistics {
  totalCases: number
  openCases: number
  inProgressCases: number
  closedCases: number
  highPriorityCases: number
  averageResolutionTime: number
}

interface CaseOverviewProps {
  data?: CaseStatistics
}

const mockData = {
  totalCases: 156,
  openCases: 42,
  inProgressCases: 38,
  closedCases: 76,
  highPriorityCases: 18,
  averageResolutionTime: 4.2,
}

const casesByType = [
  { name: 'Money Laundering', value: 45, color: '#ef4444' },
  { name: 'Fraud', value: 32, color: '#f97316' },
  { name: 'Sanctions', value: 28, color: '#eab308' },
  { name: 'Terrorist Financing', value: 18, color: '#22c55e' },
  { name: 'Other', value: 13, color: '#6366f1' },
]

const casesTrend = [
  { month: 'Jan', opened: 12, closed: 8 },
  { month: 'Feb', opened: 15, closed: 11 },
  { month: 'Mar', opened: 18, closed: 14 },
  { month: 'Apr', opened: 22, closed: 16 },
  { month: 'May', opened: 19, closed: 18 },
  { month: 'Jun', opened: 16, closed: 15 },
]

export function CaseOverview({ data = mockData }: CaseOverviewProps) {
  const resolutionTimeChange = 12.5 // Mock percentage change

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold">Case Overview</CardTitle>
        <Button size="sm" className="gap-2">
          <Plus className="h-4 w-4" />
          New Case
        </Button>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Key Metrics */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="flex items-center justify-center w-8 h-8 bg-blue-100 rounded-full mx-auto mb-2">
              <Clock className="h-4 w-4 text-blue-600" />
            </div>
            <p className="text-2xl font-bold text-blue-600">{data.openCases}</p>
            <p className="text-xs text-blue-600">Open Cases</p>
          </div>
          
          <div className="text-center p-3 bg-yellow-50 rounded-lg">
            <div className="flex items-center justify-center w-8 h-8 bg-yellow-100 rounded-full mx-auto mb-2">
              <AlertTriangle className="h-4 w-4 text-yellow-600" />
            </div>
            <p className="text-2xl font-bold text-yellow-600">{data.inProgressCases}</p>
            <p className="text-xs text-yellow-600">In Progress</p>
          </div>
          
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="flex items-center justify-center w-8 h-8 bg-green-100 rounded-full mx-auto mb-2">
              <CheckCircle className="h-4 w-4 text-green-600" />
            </div>
            <p className="text-2xl font-bold text-green-600">{data.closedCases}</p>
            <p className="text-xs text-green-600">Closed</p>
          </div>
          
          <div className="text-center p-3 bg-red-50 rounded-lg">
            <div className="flex items-center justify-center w-8 h-8 bg-red-100 rounded-full mx-auto mb-2">
              <XCircle className="h-4 w-4 text-red-600" />
            </div>
            <p className="text-2xl font-bold text-red-600">{data.highPriorityCases}</p>
            <p className="text-xs text-red-600">High Priority</p>
          </div>
        </div>

        {/* Resolution Time */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <h4 className="text-sm font-medium text-gray-700">Average Resolution Time</h4>
            <div className="flex items-center space-x-1">
              {resolutionTimeChange > 0 ? (
                <TrendingUp className="h-4 w-4 text-red-500" />
              ) : (
                <TrendingDown className="h-4 w-4 text-green-500" />
              )}
              <span className={`text-sm font-medium ${
                resolutionTimeChange > 0 ? 'text-red-500' : 'text-green-500'
              }`}>
                {Math.abs(resolutionTimeChange)}%
              </span>
            </div>
          </div>
          <div className="text-2xl font-bold text-gray-900">
            {data.averageResolutionTime} days
          </div>
          <p className="text-xs text-gray-500 mt-1">
            {resolutionTimeChange > 0 ? 'Increase' : 'Decrease'} from last month
          </p>
        </div>

        {/* Cases by Type Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Cases by Type</h4>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={casesByType}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {casesByType.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => [`${value} cases`, 'Cases']} />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 mt-2">
            {casesByType.map((type) => (
              <div key={type.name} className="flex items-center space-x-2">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: type.color }}
                />
                <span className="text-xs text-gray-600 truncate">{type.name}</span>
                <span className="text-xs font-medium text-gray-900 ml-auto">{type.value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Trend Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">6-Month Trend</h4>
          <div className="h-32">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={casesTrend}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis 
                  dataKey="month" 
                  tick={{ fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip />
                <Bar dataKey="opened" fill="#3b82f6" name="Opened" radius={[2, 2, 0, 0]} />
                <Bar dataKey="closed" fill="#10b981" name="Closed" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Recent Cases */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-gray-700">Recent Cases</h4>
            <Button variant="ghost" size="sm">View All</Button>
          </div>
          <div className="space-y-2">
            {[
              { id: 'CASE-2024-045', type: 'Money Laundering', priority: 'High', status: 'Open', time: '2 hours ago' },
              { id: 'CASE-2024-044', type: 'Fraud', priority: 'Medium', status: 'In Progress', time: '4 hours ago' },
              { id: 'CASE-2024-043', type: 'Sanctions', priority: 'Low', status: 'Closed', time: '1 day ago' },
            ].map((case_, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-white border rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-1">
                    <span className="text-sm font-medium text-gray-900">{case_.id}</span>
                    <Badge 
                      variant="outline" 
                      className={`text-xs ${
                        case_.priority === 'High' ? 'border-red-200 text-red-700' :
                        case_.priority === 'Medium' ? 'border-yellow-200 text-yellow-700' :
                        'border-gray-200 text-gray-700'
                      }`}
                    >
                      {case_.priority}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-500">{case_.type}</p>
                </div>
                <div className="text-right">
                  <Badge 
                    variant="outline"
                    className={`text-xs mb-1 ${
                      case_.status === 'Open' ? 'border-blue-200 text-blue-700' :
                      case_.status === 'In Progress' ? 'border-yellow-200 text-yellow-700' :
                      'border-green-200 text-green-700'
                    }`}
                  >
                    {case_.status}
                  </Badge>
                  <p className="text-xs text-gray-400">{case_.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
