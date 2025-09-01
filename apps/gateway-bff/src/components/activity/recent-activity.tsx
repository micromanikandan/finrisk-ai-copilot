'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { 
  Activity, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  FileText, 
  Users, 
  Bot,
  ExternalLink
} from 'lucide-react'
import { formatRelativeTime } from '@/lib/utils'

interface RecentAlert {
  id: string
  type: string
  severity: string
  message: string
  timestamp: string
}

interface RecentActivityProps {
  alerts?: RecentAlert[]
}

const mockAlerts: RecentAlert[] = [
  {
    id: '1',
    type: 'ML Alert',
    severity: 'high',
    message: 'Suspicious transaction pattern detected for entity ID: ENT-9821',
    timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(), // 15 minutes ago
  },
  {
    id: '2',
    type: 'Rule Violation',
    severity: 'medium',
    message: 'Transaction exceeds threshold limit for customer KYC level',
    timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // 45 minutes ago
  },
  {
    id: '3',
    type: 'System',
    severity: 'info',
    message: 'Weekly risk assessment completed successfully',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(), // 2 hours ago
  },
  {
    id: '4',
    type: 'Case Update',
    severity: 'low',
    message: 'Case CASE-2024-043 has been closed by investigator',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4).toISOString(), // 4 hours ago
  },
  {
    id: '5',
    type: 'Sanctions',
    severity: 'high',
    message: 'Entity matched against updated sanctions list',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 6).toISOString(), // 6 hours ago
  },
]

const systemEvents = [
  {
    id: 1,
    type: 'data_ingestion',
    title: 'Transaction Data Processed',
    description: '1,247 new transactions ingested and analyzed',
    timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    icon: FileText,
    color: 'blue',
  },
  {
    id: 2,
    type: 'ml_prediction',
    title: 'ML Model Predictions',
    description: '89 risk scores calculated, 12 high-risk cases identified',
    timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
    icon: Bot,
    color: 'purple',
  },
  {
    id: 3,
    type: 'entity_resolution',
    title: 'Entity Resolution',
    description: '45 entities updated, 3 new entities created',
    timestamp: new Date(Date.now() - 1000 * 60 * 90).toISOString(),
    icon: Users,
    color: 'green',
  },
  {
    id: 4,
    type: 'case_workflow',
    title: 'Case Workflow Update',
    description: '5 cases auto-assigned, 2 cases escalated',
    timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(),
    icon: CheckCircle,
    color: 'orange',
  },
]

function getSeverityIcon(severity: string) {
  switch (severity) {
    case 'high':
      return <AlertTriangle className="h-4 w-4 text-red-500" />
    case 'medium':
      return <Clock className="h-4 w-4 text-yellow-500" />
    case 'low':
      return <CheckCircle className="h-4 w-4 text-green-500" />
    default:
      return <Activity className="h-4 w-4 text-blue-500" />
  }
}

function getSeverityColor(severity: string) {
  switch (severity) {
    case 'high':
      return 'border-red-200 text-red-700 bg-red-50'
    case 'medium':
      return 'border-yellow-200 text-yellow-700 bg-yellow-50'
    case 'low':
      return 'border-green-200 text-green-700 bg-green-50'
    default:
      return 'border-blue-200 text-blue-700 bg-blue-50'
  }
}

export function RecentActivity({ alerts = mockAlerts }: RecentActivityProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Recent Activity
          </CardTitle>
          <Button variant="ghost" size="sm">
            View All
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Recent Alerts */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">Latest Alerts</h4>
          <div className="space-y-3 max-h-64 overflow-y-auto custom-scrollbar">
            {alerts.slice(0, 5).map((alert) => (
              <div key={alert.id} className="border-l-4 border-l-blue-400 pl-4 py-2">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-2 flex-1">
                    {getSeverityIcon(alert.severity)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="text-sm font-medium text-gray-900">
                          {alert.type}
                        </span>
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${getSeverityColor(alert.severity)}`}
                        >
                          {alert.severity}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-1">{alert.message}</p>
                      <p className="text-xs text-gray-400">
                        {formatRelativeTime(alert.timestamp)}
                      </p>
                    </div>
                  </div>
                  <Button variant="ghost" size="sm">
                    <ExternalLink className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* System Events */}
        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-3">System Events</h4>
          <div className="space-y-3">
            {systemEvents.map((event) => {
              const Icon = event.icon
              const colorClass = {
                blue: 'bg-blue-100 text-blue-600',
                purple: 'bg-purple-100 text-purple-600',
                green: 'bg-green-100 text-green-600',
                orange: 'bg-orange-100 text-orange-600',
              }[event.color]

              return (
                <div key={event.id} className="flex items-start space-x-3">
                  <div className={`p-2 rounded-lg ${colorClass} mt-0.5`}>
                    <Icon className="h-3 w-3" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900">{event.title}</p>
                    <p className="text-xs text-gray-600 mb-1">{event.description}</p>
                    <p className="text-xs text-gray-400">
                      {formatRelativeTime(event.timestamp)}
                    </p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>

        {/* Activity Summary */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Today's Summary</h4>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">23</p>
              <p className="text-xs text-gray-600">New Alerts</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">8</p>
              <p className="text-xs text-gray-600">Cases Closed</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">15</p>
              <p className="text-xs text-gray-600">In Progress</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">1.2k</p>
              <p className="text-xs text-gray-600">Transactions</p>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="border-t pt-4">
          <div className="flex items-center justify-between text-sm">
            <span className="text-gray-600">System uptime</span>
            <span className="font-medium text-green-600">99.98%</span>
          </div>
          <div className="flex items-center justify-between text-sm mt-2">
            <span className="text-gray-600">Processing speed</span>
            <span className="font-medium text-blue-600">1.2s avg</span>
          </div>
          <div className="flex items-center justify-between text-sm mt-2">
            <span className="text-gray-600">Active users</span>
            <span className="font-medium text-gray-900">24</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
