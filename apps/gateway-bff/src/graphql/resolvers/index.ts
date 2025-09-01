import { DateTimeResolver, JSONResolver } from 'graphql-scalars'

// Mock data for development
const mockDashboardData = {
  caseStatistics: {
    totalCases: 156,
    openCases: 42,
    inProgressCases: 38,
    closedCases: 76,
    highPriorityCases: 18,
    averageResolutionTime: 4.2,
  },
  riskMetrics: {
    highRiskTransactions: 234,
    suspiciousPatterns: 87,
    mlAlertsGenerated: 145,
    falsePositiveRate: 8.2,
  },
  systemHealth: {
    uptime: 99.98,
    processingSpeed: 1250,
    errorRate: 0.02,
    activeUsers: 24,
  },
  recentAlerts: [
    {
      id: '1',
      type: 'ML Alert',
      severity: 'high',
      message: 'High-risk transaction pattern detected for entity ENT-9821',
      timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
      caseId: 'CASE-2024-045',
      status: 'active',
      metadata: {}
    },
    {
      id: '2',
      type: 'Rule Violation',
      severity: 'medium',
      message: 'Transaction exceeds threshold limit for customer KYC level',
      timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
      caseId: 'CASE-2024-044',
      status: 'active',
      metadata: {}
    },
    {
      id: '3',
      type: 'System',
      severity: 'info',
      message: 'Weekly risk assessment completed successfully',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
      status: 'resolved',
      metadata: {}
    }
  ],
}

const mockCases = [
  {
    id: '1',
    caseNumber: 'CASE-2024-045',
    type: 'MONEY_LAUNDERING',
    status: 'OPEN',
    priority: 'HIGH',
    title: 'Suspicious Transaction Pattern - Entity ENT-9821',
    description: 'Multiple high-value transactions with unusual velocity patterns detected.',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
    assignedTo: {
      id: '1',
      name: 'John Doe',
      email: 'john.doe@finrisk.com',
      role: 'Senior Investigator',
      avatar: null
    },
    createdBy: {
      id: '2',
      name: 'ML System',
      email: 'system@finrisk.com',
      role: 'System',
      avatar: null
    },
    tags: ['ml-detected', 'high-velocity', 'cross-border'],
    riskScore: 87.5,
    metadata: {}
  },
  {
    id: '2',
    caseNumber: 'CASE-2024-044',
    type: 'FRAUD',
    status: 'IN_PROGRESS',
    priority: 'MEDIUM',
    title: 'Identity Verification Fraud',
    description: 'Suspicious identity documentation provided during account opening.',
    createdAt: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString(),
    updatedAt: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
    assignedTo: {
      id: '3',
      name: 'Jane Smith',
      email: 'jane.smith@finrisk.com',
      role: 'Fraud Investigator',
      avatar: null
    },
    createdBy: {
      id: '1',
      name: 'John Doe',
      email: 'john.doe@finrisk.com',
      role: 'Senior Investigator',
      avatar: null
    },
    tags: ['fraud', 'identity', 'documentation'],
    riskScore: 72.3,
    metadata: {}
  }
]

export const resolvers = {
  DateTime: DateTimeResolver,
  JSON: JSONResolver,

  Query: {
    // Dashboard
    dashboard: () => mockDashboardData,

    // Cases
    cases: async (_, { limit = 20, offset = 0, filters = {} }) => {
      // In production, this would query the case service
      return mockCases.slice(offset, offset + limit)
    },

    case: async (_, { id }) => {
      return mockCases.find(c => c.id === id)
    },

    casesByStatus: async (_, { status }) => {
      return mockCases.filter(c => c.status === status)
    },

    // Entities
    entities: async (_, { limit = 20, offset = 0, filters = {} }) => {
      // Mock entity data
      return []
    },

    entity: async (_, { id }) => {
      return null
    },

    // Search
    search: async (_, { input }) => {
      return {
        results: [],
        totalCount: 0,
        aggregations: {},
        suggestions: []
      }
    },

    quickSearch: async (_, { query }) => {
      // Mock quick search results
      return [
        {
          type: 'case',
          id: '1',
          title: 'CASE-2024-045: Suspicious Transaction Pattern',
          description: 'High-risk money laundering investigation',
          relevanceScore: 0.95,
          metadata: {}
        },
        {
          type: 'entity',
          id: 'ENT-9821',
          title: 'John Smith (Individual)',
          description: 'High-risk entity with multiple flagged transactions',
          relevanceScore: 0.87,
          metadata: {}
        }
      ]
    },

    // AI
    aiInsights: async () => {
      return {
        insights: [
          {
            id: '1',
            type: 'risk_assessment',
            title: 'High-Risk Pattern Detected',
            description: 'ML model identified unusual transaction velocity for entity ENT-4521. Risk score increased from 45 to 87.',
            confidence: 94,
            priority: 'high',
            timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
            recommendations: [
              'Escalate to senior investigator',
              'Request additional KYC documentation',
              'Monitor future transactions closely'
            ],
            metadata: {}
          }
        ],
        modelStatuses: [
          {
            modelName: 'Risk Scoring Model',
            version: 'v2.1.3',
            status: 'active',
            accuracy: 94.2,
            lastUpdated: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
            metrics: {
              precision: 0.942,
              recall: 0.887,
              f1_score: 0.914
            }
          }
        ],
        recommendations: [
          {
            id: '1',
            title: 'Optimize Investigation Workflow',
            description: 'Based on case closure patterns, prioritize fraud cases during morning hours for 23% faster resolution.',
            impact: 'High',
            effort: 'Low',
            category: 'workflow',
            estimatedBenefit: '23% faster case resolution'
          }
        ]
      }
    },

    aiChat: async (_, { message, context = {} }) => {
      // Mock AI chat response
      return `I understand you're asking about: "${message}". Based on the current context, I can help you analyze this case and provide insights. Would you like me to generate a detailed risk assessment or provide specific recommendations?`
    },

    // Transactions
    transactions: async (_, { limit = 20, offset = 0, filters = {} }) => {
      return []
    },

    transaction: async (_, { id }) => {
      return null
    },

    // Alerts
    alerts: async (_, { limit = 20, offset = 0, filters = {} }) => {
      return mockDashboardData.recentAlerts.slice(offset, offset + limit)
    },

    alert: async (_, { id }) => {
      return mockDashboardData.recentAlerts.find(a => a.id === id)
    },

    // System
    systemHealth: async () => {
      return mockDashboardData.systemHealth
    },

    recentActivity: async (_, { limit = 10 }) => {
      return {
        alerts: mockDashboardData.recentAlerts.slice(0, limit),
        systemEvents: [
          {
            id: '1',
            type: 'data_ingestion',
            title: 'Transaction Data Processed',
            description: '1,247 new transactions ingested and analyzed',
            timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
            status: 'completed'
          }
        ],
        userActions: [
          {
            id: '1',
            userId: '1',
            userName: 'John Doe',
            action: 'Case Created',
            target: 'CASE-2024-045',
            timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString()
          }
        ]
      }
    },

    // Users
    users: async () => {
      return [
        {
          id: '1',
          name: 'John Doe',
          email: 'john.doe@finrisk.com',
          role: 'Senior Investigator',
          avatar: null
        },
        {
          id: '2',
          name: 'Jane Smith',
          email: 'jane.smith@finrisk.com',
          role: 'Fraud Investigator',
          avatar: null
        }
      ]
    },

    currentUser: async () => {
      return {
        id: '1',
        name: 'John Doe',
        email: 'john.doe@finrisk.com',
        role: 'Senior Investigator',
        avatar: null
      }
    }
  },

  Mutation: {
    // Cases
    createCase: async (_, { input }) => {
      const newCase = {
        id: String(Date.now()),
        caseNumber: `CASE-${new Date().getFullYear()}-${String(Math.floor(Math.random() * 1000)).padStart(3, '0')}`,
        ...input,
        status: 'OPEN',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        createdBy: {
          id: '1',
          name: 'John Doe',
          email: 'john.doe@finrisk.com',
          role: 'Senior Investigator',
          avatar: null
        },
        assignedTo: input.assignedToId ? {
          id: input.assignedToId,
          name: 'Jane Smith',
          email: 'jane.smith@finrisk.com',
          role: 'Investigator',
          avatar: null
        } : null,
        tags: input.tags || [],
        riskScore: null,
        metadata: {}
      }
      
      mockCases.push(newCase)
      return newCase
    },

    updateCase: async (_, { id, input }) => {
      const caseIndex = mockCases.findIndex(c => c.id === id)
      if (caseIndex === -1) throw new Error('Case not found')
      
      const updatedCase = {
        ...mockCases[caseIndex],
        ...input,
        updatedAt: new Date().toISOString()
      }
      
      mockCases[caseIndex] = updatedCase
      return updatedCase
    },

    assignCase: async (_, { caseId, userId }) => {
      const caseIndex = mockCases.findIndex(c => c.id === caseId)
      if (caseIndex === -1) throw new Error('Case not found')
      
      mockCases[caseIndex].assignedTo = {
        id: userId,
        name: 'Assigned User',
        email: 'user@finrisk.com',
        role: 'Investigator',
        avatar: null
      }
      mockCases[caseIndex].updatedAt = new Date().toISOString()
      
      return mockCases[caseIndex]
    },

    closeCase: async (_, { id, reason }) => {
      const caseIndex = mockCases.findIndex(c => c.id === id)
      if (caseIndex === -1) throw new Error('Case not found')
      
      mockCases[caseIndex].status = 'CLOSED'
      mockCases[caseIndex].updatedAt = new Date().toISOString()
      
      return mockCases[caseIndex]
    },

    escalateCase: async (_, { id, reason }) => {
      const caseIndex = mockCases.findIndex(c => c.id === id)
      if (caseIndex === -1) throw new Error('Case not found')
      
      mockCases[caseIndex].status = 'ESCALATED'
      mockCases[caseIndex].priority = 'CRITICAL'
      mockCases[caseIndex].updatedAt = new Date().toISOString()
      
      return mockCases[caseIndex]
    },

    // Alerts
    createAlert: async (_, { input }) => {
      const newAlert = {
        id: String(Date.now()),
        ...input,
        timestamp: new Date().toISOString(),
        status: 'active',
        metadata: input.metadata || {}
      }
      
      mockDashboardData.recentAlerts.unshift(newAlert)
      return newAlert
    },

    acknowledgeAlert: async (_, { id }) => {
      const alertIndex = mockDashboardData.recentAlerts.findIndex(a => a.id === id)
      if (alertIndex === -1) throw new Error('Alert not found')
      
      mockDashboardData.recentAlerts[alertIndex].status = 'acknowledged'
      return mockDashboardData.recentAlerts[alertIndex]
    },

    resolveAlert: async (_, { id, resolution }) => {
      const alertIndex = mockDashboardData.recentAlerts.findIndex(a => a.id === id)
      if (alertIndex === -1) throw new Error('Alert not found')
      
      mockDashboardData.recentAlerts[alertIndex].status = 'resolved'
      mockDashboardData.recentAlerts[alertIndex].metadata = {
        ...mockDashboardData.recentAlerts[alertIndex].metadata,
        resolution
      }
      return mockDashboardData.recentAlerts[alertIndex]
    },

    // System
    refreshData: async () => {
      // Mock data refresh
      return true
    },

    exportData: async (_, { filters, format }) => {
      // Mock data export
      return `data-export-${Date.now()}.${format}`
    }
  },

  Subscription: {
    alertCreated: {
      subscribe: () => {
        // Mock subscription - in production would use real pub/sub
        return null
      }
    },

    caseUpdated: {
      subscribe: () => {
        // Mock subscription
        return null
      }
    },

    systemHealthChanged: {
      subscribe: () => {
        // Mock subscription
        return null
      }
    },

    aiInsightGenerated: {
      subscribe: () => {
        // Mock subscription
        return null
      }
    },

    dashboardUpdated: {
      subscribe: () => {
        // Mock subscription
        return null
      }
    },

    riskMetricsUpdated: {
      subscribe: () => {
        // Mock subscription
        return null
      }
    }
  }
}
