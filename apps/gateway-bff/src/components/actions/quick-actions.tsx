'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Plus, 
  Search, 
  FileText, 
  Users, 
  Bot, 
  BarChart3,
  AlertTriangle,
  Download,
  Settings,
  Zap
} from 'lucide-react'

const quickActions = [
  {
    id: 'create-case',
    title: 'Create New Case',
    description: 'Start a new investigation case',
    icon: Plus,
    color: 'bg-blue-500 hover:bg-blue-600',
    shortcut: '⌘+N',
  },
  {
    id: 'search-entities',
    title: 'Search Entities',
    description: 'Look up people, organizations',
    icon: Users,
    color: 'bg-green-500 hover:bg-green-600',
    shortcut: '⌘+E',
  },
  {
    id: 'ai-copilot',
    title: 'AI Copilot',
    description: 'Get AI-powered insights',
    icon: Bot,
    color: 'bg-purple-500 hover:bg-purple-600',
    shortcut: '⌘+K',
    badge: 'NEW',
  },
  {
    id: 'advanced-search',
    title: 'Advanced Search',
    description: 'Complex queries and filters',
    icon: Search,
    color: 'bg-orange-500 hover:bg-orange-600',
    shortcut: '⌘+⇧+F',
  },
  {
    id: 'generate-report',
    title: 'Generate Report',
    description: 'Create compliance reports',
    icon: FileText,
    color: 'bg-indigo-500 hover:bg-indigo-600',
    shortcut: '⌘+R',
  },
  {
    id: 'analytics',
    title: 'View Analytics',
    description: 'Risk metrics and trends',
    icon: BarChart3,
    color: 'bg-teal-500 hover:bg-teal-600',
    shortcut: '⌘+A',
  },
]

const recentActivities = [
  {
    id: 1,
    action: 'Case Created',
    details: 'CASE-2024-045: Suspicious Transaction',
    time: '10 minutes ago',
    user: 'John Doe',
    type: 'case',
  },
  {
    id: 2,
    action: 'Alert Generated',
    details: 'High-risk transaction detected',
    time: '25 minutes ago',
    user: 'ML System',
    type: 'alert',
  },
  {
    id: 3,
    action: 'Entity Updated',
    details: 'Customer profile enhanced',
    time: '1 hour ago',
    user: 'Jane Smith',
    type: 'entity',
  },
  {
    id: 4,
    action: 'Report Generated',
    details: 'Monthly compliance report',
    time: '2 hours ago',
    user: 'System',
    type: 'report',
  },
]

const systemAlerts = [
  {
    id: 1,
    title: 'ML Model Update',
    message: 'New risk scoring model deployed',
    severity: 'info',
    time: '1 hour ago',
  },
  {
    id: 2,
    title: 'High Risk Alert',
    message: '3 new high-priority cases require attention',
    severity: 'warning',
    time: '2 hours ago',
  },
  {
    id: 3,
    title: 'System Maintenance',
    message: 'Scheduled maintenance window tonight',
    severity: 'info',
    time: '4 hours ago',
  },
]

export function QuickActions() {
  return (
    <div className="space-y-6">
      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Quick Actions
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {quickActions.map((action) => {
            const Icon = action.icon
            return (
              <Button
                key={action.id}
                variant="outline"
                className="w-full justify-start h-auto p-4 hover:bg-gray-50"
              >
                <div className="flex items-center space-x-3 w-full">
                  <div className={`p-2 rounded-lg ${action.color} text-white`}>
                    <Icon className="h-4 w-4" />
                  </div>
                  <div className="flex-1 text-left">
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-medium">{action.title}</p>
                      {action.badge && (
                        <Badge variant="secondary" className="text-xs">
                          {action.badge}
                        </Badge>
                      )}
                    </div>
                    <p className="text-xs text-gray-500">{action.description}</p>
                  </div>
                  <Badge variant="outline" className="text-xs">
                    {action.shortcut}
                  </Badge>
                </div>
              </Button>
            )
          })}
        </CardContent>
      </Card>

      {/* Recent Activity */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Recent Activity</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3 p-2 rounded-lg hover:bg-gray-50">
                <div className={`p-1 rounded-full mt-1 ${
                  activity.type === 'case' ? 'bg-blue-100' :
                  activity.type === 'alert' ? 'bg-red-100' :
                  activity.type === 'entity' ? 'bg-green-100' :
                  'bg-gray-100'
                }`}>
                  {activity.type === 'case' && <FileText className="h-3 w-3 text-blue-600" />}
                  {activity.type === 'alert' && <AlertTriangle className="h-3 w-3 text-red-600" />}
                  {activity.type === 'entity' && <Users className="h-3 w-3 text-green-600" />}
                  {activity.type === 'report' && <Download className="h-3 w-3 text-gray-600" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900">{activity.action}</p>
                  <p className="text-xs text-gray-500 truncate">{activity.details}</p>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs text-gray-400">{activity.time}</span>
                    <span className="text-xs text-gray-400">•</span>
                    <span className="text-xs text-gray-500">{activity.user}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
          <Button variant="ghost" size="sm" className="w-full mt-3">
            View All Activity
          </Button>
        </CardContent>
      </Card>

      {/* System Alerts */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">System Alerts</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {systemAlerts.map((alert) => (
              <div key={alert.id} className={`p-3 rounded-lg border-l-4 ${
                alert.severity === 'warning' ? 'bg-yellow-50 border-yellow-400' :
                alert.severity === 'error' ? 'bg-red-50 border-red-400' :
                'bg-blue-50 border-blue-400'
              }`}>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900">{alert.title}</p>
                    <p className="text-xs text-gray-600 mt-1">{alert.message}</p>
                  </div>
                  <span className="text-xs text-gray-400 ml-2">{alert.time}</span>
                </div>
              </div>
            ))}
          </div>
          <Button variant="ghost" size="sm" className="w-full mt-3">
            <Settings className="h-4 w-4 mr-2" />
            Manage Notifications
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
