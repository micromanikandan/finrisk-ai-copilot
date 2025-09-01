'use client'

import React, { useState, useEffect } from 'react'
import { Search, FileText, Users, DollarSign, TrendingUp } from 'lucide-react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'

interface QuickSearchModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

const searchCategories = [
  { id: 'cases', name: 'Cases', icon: FileText, color: 'blue' },
  { id: 'entities', name: 'Entities', icon: Users, color: 'green' },
  { id: 'transactions', name: 'Transactions', icon: DollarSign, color: 'yellow' },
  { id: 'alerts', name: 'Alerts', icon: TrendingUp, color: 'red' },
]

const recentSearches = [
  { id: 1, query: 'Case #CASE-2024-001', type: 'cases' },
  { id: 2, query: 'John Smith', type: 'entities' },
  { id: 3, query: 'Transaction > $10,000', type: 'transactions' },
  { id: 4, query: 'High risk alerts', type: 'alerts' },
]

const quickActions = [
  { id: 1, name: 'Create New Case', shortcut: '⌘+N' },
  { id: 2, name: 'View All Alerts', shortcut: '⌘+A' },
  { id: 3, name: 'Generate Report', shortcut: '⌘+R' },
  { id: 4, name: 'Open AI Copilot', shortcut: '⌘+K' },
]

export function QuickSearchModal({ open, onOpenChange }: QuickSearchModalProps) {
  const [query, setQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  useEffect(() => {
    if (open) {
      setQuery('')
      setSelectedCategory(null)
    }
  }, [open])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.metaKey && e.key === 'k') {
        e.preventDefault()
        onOpenChange(true)
      }
    }

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [onOpenChange])

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Quick Search</DialogTitle>
        </DialogHeader>
        
        <div className="space-y-4">
          {/* Search Input */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <input
              type="text"
              placeholder="Search cases, entities, transactions..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              autoFocus
            />
          </div>

          {/* Search Categories */}
          <div className="grid grid-cols-4 gap-2">
            {searchCategories.map((category) => {
              const Icon = category.icon
              const isSelected = selectedCategory === category.id
              
              return (
                <Button
                  key={category.id}
                  variant={isSelected ? "default" : "outline"}
                  onClick={() => setSelectedCategory(isSelected ? null : category.id)}
                  className={cn(
                    "flex flex-col items-center space-y-1 h-auto py-3",
                    isSelected && "bg-blue-600 text-white"
                  )}
                >
                  <Icon className="h-4 w-4" />
                  <span className="text-xs">{category.name}</span>
                </Button>
              )
            })}
          </div>

          {query ? (
            /* Search Results */
            <div className="space-y-2">
              <h3 className="text-sm font-medium text-gray-700">Search Results</h3>
              <div className="space-y-1 max-h-64 overflow-y-auto">
                {/* Mock search results */}
                {Array.from({ length: 5 }).map((_, i) => (
                  <Button
                    key={i}
                    variant="ghost"
                    className="w-full justify-start h-auto p-3"
                  >
                    <div className="flex items-center space-x-3">
                      <FileText className="h-4 w-4 text-gray-400" />
                      <div className="flex-1 text-left">
                        <p className="text-sm font-medium">Case #{String(i + 1).padStart(3, '0')}</p>
                        <p className="text-xs text-gray-500">Suspicious transaction pattern</p>
                      </div>
                      <Badge variant="outline" className="text-xs">Case</Badge>
                    </div>
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Recent Searches */}
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-700">Recent Searches</h3>
                <div className="space-y-1">
                  {recentSearches.map((search) => (
                    <Button
                      key={search.id}
                      variant="ghost"
                      className="w-full justify-start h-auto p-3"
                      onClick={() => setQuery(search.query)}
                    >
                      <div className="flex items-center space-x-3">
                        <Search className="h-4 w-4 text-gray-400" />
                        <span className="text-sm">{search.query}</span>
                        <Badge variant="outline" className="text-xs ml-auto">
                          {search.type}
                        </Badge>
                      </div>
                    </Button>
                  ))}
                </div>
              </div>

              {/* Quick Actions */}
              <div className="space-y-2">
                <h3 className="text-sm font-medium text-gray-700">Quick Actions</h3>
                <div className="space-y-1">
                  {quickActions.map((action) => (
                    <Button
                      key={action.id}
                      variant="ghost"
                      className="w-full justify-between h-auto p-3"
                    >
                      <span className="text-sm">{action.name}</span>
                      <Badge variant="secondary" className="text-xs">
                        {action.shortcut}
                      </Badge>
                    </Button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}
