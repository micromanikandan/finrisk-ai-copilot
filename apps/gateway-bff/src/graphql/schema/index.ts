import { gql } from 'graphql-tag'

export const typeDefs = gql`
  scalar DateTime
  scalar JSON

  # Dashboard Types
  type CaseStatistics {
    totalCases: Int!
    openCases: Int!
    inProgressCases: Int!
    closedCases: Int!
    highPriorityCases: Int!
    averageResolutionTime: Float!
  }

  type RiskMetrics {
    highRiskTransactions: Int!
    suspiciousPatterns: Int!
    mlAlertsGenerated: Int!
    falsePositiveRate: Float!
  }

  type SystemHealth {
    uptime: Float!
    processingSpeed: Float!
    errorRate: Float!
    activeUsers: Int!
  }

  type Alert {
    id: ID!
    type: String!
    severity: String!
    message: String!
    timestamp: DateTime!
    caseId: String
    entityId: String
    status: String!
    metadata: JSON
  }

  type Dashboard {
    caseStatistics: CaseStatistics!
    riskMetrics: RiskMetrics!
    systemHealth: SystemHealth!
    recentAlerts: [Alert!]!
  }

  # Case Types
  enum CaseStatus {
    OPEN
    IN_PROGRESS
    CLOSED
    ESCALATED
    ON_HOLD
  }

  enum CaseType {
    MONEY_LAUNDERING
    FRAUD
    SANCTIONS
    TERRORIST_FINANCING
    OTHER
  }

  enum Priority {
    LOW
    MEDIUM
    HIGH
    CRITICAL
  }

  type User {
    id: ID!
    name: String!
    email: String!
    role: String!
    avatar: String
  }

  type Case {
    id: ID!
    caseNumber: String!
    type: CaseType!
    status: CaseStatus!
    priority: Priority!
    title: String!
    description: String
    createdAt: DateTime!
    updatedAt: DateTime!
    assignedTo: User
    createdBy: User!
    tags: [String!]!
    riskScore: Float
    metadata: JSON
  }

  # Entity Types
  type Entity {
    id: ID!
    name: String!
    type: String!
    riskScore: Float
    attributes: JSON!
    relationships: [EntityRelationship!]!
    cases: [Case!]!
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  type EntityRelationship {
    id: ID!
    fromEntity: Entity!
    toEntity: Entity!
    relationshipType: String!
    strength: Float!
    metadata: JSON
  }

  # Search Types
  type SearchResult {
    type: String!
    id: ID!
    title: String!
    description: String
    relevanceScore: Float!
    metadata: JSON
  }

  type SearchResponse {
    results: [SearchResult!]!
    totalCount: Int!
    aggregations: JSON
    suggestions: [String!]!
  }

  # AI Types
  type AIInsight {
    id: ID!
    type: String!
    title: String!
    description: String!
    confidence: Float!
    priority: String!
    timestamp: DateTime!
    recommendations: [String!]!
    metadata: JSON
  }

  type MLModel {
    modelName: String!
    version: String!
    status: String!
    accuracy: Float
    lastUpdated: DateTime!
    metrics: JSON
  }

  type AIRecommendation {
    id: ID!
    title: String!
    description: String!
    impact: String!
    effort: String!
    category: String!
    estimatedBenefit: String
  }

  type AIInsights {
    insights: [AIInsight!]!
    modelStatuses: [MLModel!]!
    recommendations: [AIRecommendation!]!
  }

  # Transaction Types
  type Transaction {
    id: ID!
    amount: Float!
    currency: String!
    fromAccount: String!
    toAccount: String!
    timestamp: DateTime!
    type: String!
    riskScore: Float
    flags: [String!]!
    metadata: JSON
  }

  # Input Types
  input CaseInput {
    type: CaseType!
    priority: Priority!
    title: String!
    description: String
    assignedToId: ID
    tags: [String!]
  }

  input SearchInput {
    query: String!
    filters: JSON
    limit: Int = 20
    offset: Int = 0
    sortBy: String
    sortOrder: String = "DESC"
  }

  input AlertInput {
    type: String!
    severity: String!
    message: String!
    caseId: String
    entityId: String
    metadata: JSON
  }

  # Query Type
  type Query {
    # Dashboard
    dashboard: Dashboard!
    
    # Cases
    cases(limit: Int = 20, offset: Int = 0, filters: JSON): [Case!]!
    case(id: ID!): Case
    casesByStatus(status: CaseStatus!): [Case!]!
    
    # Entities
    entities(limit: Int = 20, offset: Int = 0, filters: JSON): [Entity!]!
    entity(id: ID!): Entity
    
    # Search
    search(input: SearchInput!): SearchResponse!
    quickSearch(query: String!): [SearchResult!]!
    
    # AI
    aiInsights: AIInsights!
    aiChat(message: String!, context: JSON): String!
    
    # Transactions
    transactions(limit: Int = 20, offset: Int = 0, filters: JSON): [Transaction!]!
    transaction(id: ID!): Transaction
    
    # Alerts
    alerts(limit: Int = 20, offset: Int = 0, filters: JSON): [Alert!]!
    alert(id: ID!): Alert
    
    # System
    systemHealth: SystemHealth!
    recentActivity(limit: Int = 10): JSON!
    
    # Users
    users: [User!]!
    currentUser: User!
  }

  # Mutation Type
  type Mutation {
    # Cases
    createCase(input: CaseInput!): Case!
    updateCase(id: ID!, input: CaseInput!): Case!
    assignCase(caseId: ID!, userId: ID!): Case!
    closeCase(id: ID!, reason: String!): Case!
    escalateCase(id: ID!, reason: String!): Case!
    
    # Alerts
    createAlert(input: AlertInput!): Alert!
    updateAlert(id: ID!, input: AlertInput!): Alert!
    acknowledgeAlert(id: ID!): Alert!
    resolveAlert(id: ID!, resolution: String!): Alert!
    
    # Entities
    updateEntityRiskScore(entityId: ID!, riskScore: Float!): Entity!
    linkEntities(fromEntityId: ID!, toEntityId: ID!, relationshipType: String!): EntityRelationship!
    
    # AI
    trainModel(modelName: String!, trainingData: JSON!): MLModel!
    deployModel(modelName: String!, version: String!): MLModel!
    
    # System
    refreshData: Boolean!
    exportData(filters: JSON!, format: String!): String!
  }

  # Subscription Type
  type Subscription {
    # Real-time updates
    alertCreated: Alert!
    caseUpdated: Case!
    systemHealthChanged: SystemHealth!
    aiInsightGenerated: AIInsight!
    
    # Dashboard updates
    dashboardUpdated: Dashboard!
    riskMetricsUpdated: RiskMetrics!
  }
`