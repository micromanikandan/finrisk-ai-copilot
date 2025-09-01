import { gql } from '@apollo/client'

export const GET_DASHBOARD_DATA = gql`
  query GetDashboardData {
    dashboard {
      caseStatistics {
        totalCases
        openCases
        inProgressCases
        closedCases
        highPriorityCases
        averageResolutionTime
      }
      riskMetrics {
        highRiskTransactions
        suspiciousPatterns
        mlAlertsGenerated
        falsePositiveRate
      }
      systemHealth {
        uptime
        processingSpeed
        errorRate
        activeUsers
      }
      recentAlerts {
        id
        type
        severity
        message
        timestamp
      }
    }
  }
`

export const GET_CASE_OVERVIEW = gql`
  query GetCaseOverview {
    caseOverview {
      totalCases
      openCases
      inProgressCases
      closedCases
      highPriorityCases
      averageResolutionTime
      casesByType {
        type
        count
        percentage
      }
      recentCases {
        id
        caseNumber
        type
        priority
        status
        createdAt
        assignedTo {
          id
          name
        }
      }
    }
  }
`

export const GET_RISK_METRICS = gql`
  query GetRiskMetrics {
    riskMetrics {
      highRiskTransactions
      suspiciousPatterns
      mlAlertsGenerated
      falsePositiveRate
      riskTrend {
        date
        highRisk
        mediumRisk
        lowRisk
      }
      riskCategories {
        category
        riskScore
        trend
        changePercentage
        activeCases
      }
    }
  }
`

export const GET_RECENT_ACTIVITY = gql`
  query GetRecentActivity($limit: Int = 10) {
    recentActivity(limit: $limit) {
      alerts {
        id
        type
        severity
        message
        timestamp
        caseId
      }
      systemEvents {
        id
        type
        title
        description
        timestamp
        status
      }
      userActions {
        id
        userId
        userName
        action
        target
        timestamp
      }
    }
  }
`

export const GET_AI_INSIGHTS = gql`
  query GetAIInsights {
    aiInsights {
      insights {
        id
        type
        title
        description
        confidence
        priority
        timestamp
        recommendations
        metadata
      }
      modelStatuses {
        modelName
        version
        status
        accuracy
        lastUpdated
        metrics
      }
      recommendations {
        id
        title
        description
        impact
        effort
        category
        estimatedBenefit
      }
    }
  }
`
