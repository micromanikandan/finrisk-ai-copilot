'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  Shield, 
  Target, 
  Activity 
} from 'lucide-react'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  AreaChart,
  Area
} from 'recharts'

interface RiskMetrics {
  highRiskTransactions: number
  suspiciousPatterns: number
  mlAlertsGenerated: number
  falsePositiveRate: number
}

interface RiskMetricsProps {
  data?: RiskMetrics
}

const mockData = {
  highRiskTransactions: 234,
  suspiciousPatterns: 87,
  mlAlertsGenerated: 145,
  falsePositiveRate: 8.2,
}

const riskTrend = [
  { date: '2024-01-01', high: 45, medium: 78, low: 123 },
  { date: '2024-01-02', high: 52, medium: 82, low: 134 },
  { date: '2024-01-03', high: 48, medium: 75, low: 128 },
  { date: '2024-01-04', high: 61, medium: 88, low: 142 },
  { date: '2024-01-05', high: 55, medium: 79, low: 135 },
  { date: '2024-01-06', high: 49, medium: 73, low: 126 },
  { date: '2024-01-07', high: 58, medium: 85, low: 139 },
]

const alertsData = [
  { time: '00:00', alerts: 12 },
  { time: '04:00', alerts: 8 },
  { time: '08:00', alerts: 24 },
  { time: '12:00', alerts: 32 },
  { time: '16:00', alerts: 28 },
  { time: '20:00', alerts: 18 },
]

const riskCategories = [
  { 
    name: 'Money Laundering', 
    risk: 85, 
    trend: 'up', 
    change: 12,
    cases: 23,
    color: '#ef4444'
  },
  { 
    name: 'Fraud Detection', 
    risk: 72, 
    trend: 'down', 
    change: -5,
    cases: 18,
    color: '#f97316'
  },
  { 
    name: 'Sanctions Screening', 
    risk: 45, 
    trend: 'up', 
    change: 8,
    cases: 12,
    color: '#eab308'
  },
  { 
    name: 'Terrorist Financing', 
    risk: 38, 
    trend: 'down', 
    change: -15,
    cases: 7,
    color: '#22c55e'
  },
]

export function RiskMetrics({ data = mockData }: RiskMetricsProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5" />
          Risk Metrics
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Key Risk Indicators */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              <Badge variant="outline" className="text-red-700 border-red-200">
                +18%
              </Badge>
            </div>
            <p className="text-2xl font-bold text-red-600">{data.highRiskTransactions}</p>
            <p className="text-sm text-red-600">High Risk Transactions</p>
          </div>
          
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <Target className="h-5 w-5 text-orange-600" />
              <Badge variant="outline" className="text-orange-700 border-orange-200">
                +25%
              </Badge>
            </div>
            <p className="text-2xl font-bold text-orange-600">{data.suspiciousPatterns}</p>
            <p className="text-sm text-orange-600">Suspicious Patterns</p>
          </div>
          
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <Activity className="h-5 w-5 text-blue-600" />
              <Badge variant="outline" className="text-blue-700 border-blue-200">
                +8%
              </Badge>
            </div>
            <p className="text-2xl font-bold text-blue-600">{data.mlAlertsGenerated}</p>
            <p className="text-sm text-blue-600">ML Alerts</p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <TrendingDown className="h-5 w-5 text-green-600" />
              <Badge variant="outline" className="text-green-700 border-green-200">
                -12%
              </Badge>
            </div>
            <p className="text-2xl font-bold text-green-600">{data.falsePositiveRate}%</p>
            <p className="text-sm text-green-600">False Positive Rate</p>
          </div>
        </div>

        {/* Risk Trend Chart */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">7-Day Risk Trend</h4>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={riskTrend}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip 
                  labelFormatter={(value) => new Date(value).toLocaleDateString()}
                  formatter={(value, name) => [value, name === 'high' ? 'High Risk' : name === 'medium' ? 'Medium Risk' : 'Low Risk']}
                />
                <Area 
                  type="monotone" 
                  dataKey="high" 
                  stackId="1" 
                  stroke="#ef4444" 
                  fill="#ef4444" 
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="medium" 
                  stackId="1" 
                  stroke="#f97316" 
                  fill="#f97316" 
                  fillOpacity={0.6}
                />
                <Area 
                  type="monotone" 
                  dataKey="low" 
                  stackId="1" 
                  stroke="#22c55e" 
                  fill="#22c55e" 
                  fillOpacity={0.6}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Categories */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Risk Categories</h4>
          <div className="space-y-3">
            {riskCategories.map((category, index) => (
              <div key={index} className="bg-white border rounded-lg p-3">
                <div className="flex items-center justify-between mb-2">
                  <h5 className="text-sm font-medium text-gray-900">{category.name}</h5>
                  <div className="flex items-center space-x-2">
                    {category.trend === 'up' ? (
                      <TrendingUp className="h-4 w-4 text-red-500" />
                    ) : (
                      <TrendingDown className="h-4 w-4 text-green-500" />
                    )}
                    <span className={`text-sm font-medium ${
                      category.trend === 'up' ? 'text-red-500' : 'text-green-500'
                    }`}>
                      {category.change > 0 ? '+' : ''}{category.change}%
                    </span>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="flex-1">
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="h-2 rounded-full transition-all duration-300" 
                        style={{ 
                          width: `${category.risk}%`,
                          backgroundColor: category.color
                        }}
                      />
                    </div>
                  </div>
                  <div className="text-sm font-medium text-gray-900">
                    {category.risk}%
                  </div>
                </div>
                <div className="flex justify-between mt-2">
                  <span className="text-xs text-gray-500">{category.cases} active cases</span>
                  <span className="text-xs text-gray-500">Risk Score: {category.risk}/100</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Alert Timeline */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">24-Hour Alert Pattern</h4>
          <div className="h-32">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={alertsData}>
                <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
                <XAxis 
                  dataKey="time" 
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
                <Line 
                  type="monotone" 
                  dataKey="alerts" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
