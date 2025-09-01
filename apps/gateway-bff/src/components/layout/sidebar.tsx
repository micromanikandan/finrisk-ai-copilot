'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import {
  LayoutDashboard,
  FileText,
  Search,
  Bot,
  BarChart3,
  Settings,
  Shield,
  Users,
  Database,
  AlertTriangle,
  X,
  ChevronDown,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { useState } from 'react'

interface SidebarProps {
  isOpen: boolean
  onClose: () => void
}

const navigation = [
  {
    name: 'Dashboard',
    href: '/',
    icon: LayoutDashboard,
    current: true,
    badge: null,
  },
  {
    name: 'Cases',
    href: '/cases',
    icon: FileText,
    current: false,
    badge: '12',
    submenu: [
      { name: 'All Cases', href: '/cases' },
      { name: 'My Cases', href: '/cases/my' },
      { name: 'High Priority', href: '/cases/priority' },
      { name: 'Overdue', href: '/cases/overdue' },
    ],
  },
  {
    name: 'Search & Investigation',
    href: '/search',
    icon: Search,
    current: false,
    badge: null,
    submenu: [
      { name: 'Entity Search', href: '/search/entities' },
      { name: 'Transaction Search', href: '/search/transactions' },
      { name: 'Pattern Analysis', href: '/search/patterns' },
      { name: 'Advanced Search', href: '/search/advanced' },
    ],
  },
  {
    name: 'AI Copilot',
    href: '/copilot',
    icon: Bot,
    current: false,
    badge: 'NEW',
    submenu: [
      { name: 'Chat Assistant', href: '/copilot/chat' },
      { name: 'Risk Scoring', href: '/copilot/scoring' },
      { name: 'Recommendations', href: '/copilot/recommendations' },
      { name: 'Auto Investigation', href: '/copilot/auto-investigation' },
    ],
  },
  {
    name: 'Analytics',
    href: '/analytics',
    icon: BarChart3,
    current: false,
    badge: null,
    submenu: [
      { name: 'Risk Metrics', href: '/analytics/risk' },
      { name: 'Performance', href: '/analytics/performance' },
      { name: 'Trends', href: '/analytics/trends' },
      { name: 'Reports', href: '/analytics/reports' },
    ],
  },
  {
    name: 'Alerts',
    href: '/alerts',
    icon: AlertTriangle,
    current: false,
    badge: '8',
    submenu: [
      { name: 'Active Alerts', href: '/alerts/active' },
      { name: 'ML Alerts', href: '/alerts/ml' },
      { name: 'Rule-based', href: '/alerts/rules' },
      { name: 'Alert History', href: '/alerts/history' },
    ],
  },
]

const systemNavigation = [
  {
    name: 'User Management',
    href: '/admin/users',
    icon: Users,
    current: false,
  },
  {
    name: 'System Health',
    href: '/admin/system',
    icon: Database,
    current: false,
  },
  {
    name: 'Security',
    href: '/admin/security',
    icon: Shield,
    current: false,
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    current: false,
  },
]

export function Sidebar({ isOpen, onClose }: SidebarProps) {
  const pathname = usePathname()
  const [expandedItems, setExpandedItems] = useState<string[]>(['Cases'])

  const toggleExpanded = (itemName: string) => {
    setExpandedItems(prev =>
      prev.includes(itemName)
        ? prev.filter(item => item !== itemName)
        : [...prev, itemName]
    )
  }

  return (
    <>
      {/* Mobile sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-gray-800 transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0",
        isOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
      )}>
        <div className="flex h-full flex-col">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <Shield className="h-5 w-5 text-white" />
                </div>
              </div>
              <div className="ml-3">
                <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
                  FinRisk
                </h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  AI Copilot
                </p>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className="lg:hidden"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto custom-scrollbar">
            <div className="space-y-1">
              {navigation.map((item) => {
                const isActive = pathname === item.href || pathname?.startsWith(item.href + '/')
                const isExpanded = expandedItems.includes(item.name)
                
                return (
                  <div key={item.name}>
                    {item.submenu ? (
                      <Collapsible open={isExpanded} onOpenChange={() => toggleExpanded(item.name)}>
                        <CollapsibleTrigger asChild>
                          <Button
                            variant="ghost"
                            className={cn(
                              "w-full justify-start h-auto p-3 font-normal",
                              isActive
                                ? "bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-200"
                                : "text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700"
                            )}
                          >
                            <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                            <span className="flex-1 text-left">{item.name}</span>
                            {item.badge && (
                              <Badge
                                variant={item.badge === 'NEW' ? 'default' : 'secondary'}
                                className="ml-2 h-5 text-xs"
                              >
                                {item.badge}
                              </Badge>
                            )}
                            <ChevronDown className={cn(
                              "ml-2 h-4 w-4 transition-transform",
                              isExpanded && "rotate-180"
                            )} />
                          </Button>
                        </CollapsibleTrigger>
                        <CollapsibleContent className="space-y-1 pl-6 mt-1">
                          {item.submenu.map((subItem) => {
                            const isSubActive = pathname === subItem.href
                            return (
                              <Link key={subItem.href} href={subItem.href}>
                                <Button
                                  variant="ghost"
                                  className={cn(
                                    "w-full justify-start h-auto p-2 font-normal text-sm",
                                    isSubActive
                                      ? "bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-200"
                                      : "text-gray-600 hover:bg-gray-50 dark:text-gray-400 dark:hover:bg-gray-700"
                                  )}
                                >
                                  {subItem.name}
                                </Button>
                              </Link>
                            )
                          })}
                        </CollapsibleContent>
                      </Collapsible>
                    ) : (
                      <Link href={item.href}>
                        <Button
                          variant="ghost"
                          className={cn(
                            "w-full justify-start h-auto p-3 font-normal",
                            isActive
                              ? "bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-200"
                              : "text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700"
                          )}
                        >
                          <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                          {item.name}
                          {item.badge && (
                            <Badge
                              variant={item.badge === 'NEW' ? 'default' : 'secondary'}
                              className="ml-auto h-5 text-xs"
                            >
                              {item.badge}
                            </Badge>
                          )}
                        </Button>
                      </Link>
                    )}
                  </div>
                )
              })}
            </div>

            {/* System section */}
            <div className="pt-6 mt-6 border-t border-gray-200 dark:border-gray-700">
              <h3 className="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                Administration
              </h3>
              <div className="mt-3 space-y-1">
                {systemNavigation.map((item) => {
                  const isActive = pathname === item.href
                  return (
                    <Link key={item.name} href={item.href}>
                      <Button
                        variant="ghost"
                        className={cn(
                          "w-full justify-start h-auto p-3 font-normal",
                          isActive
                            ? "bg-blue-50 text-blue-700 dark:bg-blue-900/50 dark:text-blue-200"
                            : "text-gray-700 hover:bg-gray-50 dark:text-gray-300 dark:hover:bg-gray-700"
                        )}
                      >
                        <item.icon className="mr-3 h-5 w-5 flex-shrink-0" />
                        {item.name}
                      </Button>
                    </Link>
                  )
                })}
              </div>
            </div>
          </nav>

          {/* User info */}
          <div className="flex-shrink-0 border-t border-gray-200 dark:border-gray-700 p-4">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 bg-gray-300 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-gray-700">JD</span>
                </div>
              </div>
              <div className="ml-3 flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                  John Doe
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                  Senior Investigator
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
