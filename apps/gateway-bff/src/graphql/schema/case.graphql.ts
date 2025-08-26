/**
 * GraphQL schema for Case Management
 */

export const caseTypeDefs = `#graphql
  extend type Query {
    # Case queries
    case(id: ID!): Case
    caseByNumber(caseNumber: String!): Case
    cases(
      filter: CaseFilterInput
      pagination: PaginationInput
      sort: CaseSortInput
    ): CaseConnection!
    caseStatistics: CaseStatistics!
    caseAnalytics(timeRange: String!): CaseAnalytics!
  }

  extend type Mutation {
    # Case mutations
    createCase(input: CreateCaseInput!): CreateCaseResponse!
    updateCase(id: ID!, input: UpdateCaseInput!): UpdateCaseResponse!
    assignCase(id: ID!, assigneeId: ID!): AssignCaseResponse!
    closeCase(id: ID!, reason: String!): CloseCaseResponse!
    escalateCase(id: ID!, reason: String!): EscalateCaseResponse!
    addCaseNote(id: ID!, note: String!): AddCaseNoteResponse!
    attachEvidence(id: ID!, evidence: EvidenceInput!): AttachEvidenceResponse!
  }

  extend type Subscription {
    # Case subscriptions
    caseUpdated(id: ID!): Case!
    casesUpdated(filter: CaseFilterInput): Case!
    caseStatusChanged: CaseStatusChange!
  }

  # Case types
  type Case implements Node & Timestamped & TenantScoped {
    id: ID!
    caseNumber: String!
    title: String!
    description: String
    caseType: CaseType!
    priority: Priority!
    status: CaseStatus!
    
    # Relationships
    assignedTo: User
    createdBy: User!
    
    # Case data
    evidence: [Evidence!]!
    notes: [CaseNote!]!
    events: [CaseEvent!]!
    entities: [CaseEntity!]!
    tags: [String!]!
    metadata: JSON
    
    # Timestamps
    createdAt: DateTime!
    updatedAt: DateTime!
    closedAt: DateTime
    
    # Tenant information
    tenantId: String!
    cellId: String!
    
    # Computed fields
    daysSinceCreated: Int!
    isOverdue: Boolean!
    riskScore: Float
    similarCases: [Case!]!
  }

  # Case enums
  enum CaseType {
    FRAUD
    AML
    SANCTIONS
    KYC
    CYBERSECURITY
    INSIDER_TRADING
    COMPLIANCE
    OPERATIONAL_RISK
  }

  enum Priority {
    LOW
    MEDIUM
    HIGH
    CRITICAL
  }

  enum CaseStatus {
    OPEN
    IN_PROGRESS
    PENDING_REVIEW
    ESCALATED
    CLOSED
    ARCHIVED
  }

  # Evidence types
  type Evidence implements Node & Timestamped {
    id: ID!
    evidenceType: EvidenceType!
    source: String!
    contentHash: String!
    storagePath: String
    metadata: JSON
    collectedAt: DateTime!
    collectedBy: User!
    encrypted: Boolean!
    classification: Classification!
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  enum EvidenceType {
    DOCUMENT
    TRANSACTION
    COMMUNICATION
    SCREENSHOT
    AUDIO
    VIDEO
    OTHER
  }

  enum Classification {
    PUBLIC
    INTERNAL
    CONFIDENTIAL
    RESTRICTED
  }

  # Case notes
  type CaseNote implements Node & Timestamped {
    id: ID!
    content: String!
    author: User!
    isInternal: Boolean!
    attachments: [String!]!
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  # Case events (audit trail)
  type CaseEvent implements Node & Timestamped {
    id: ID!
    eventType: CaseEventType!
    description: String!
    actor: User!
    metadata: JSON
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  enum CaseEventType {
    CREATED
    UPDATED
    ASSIGNED
    UNASSIGNED
    STATUS_CHANGED
    PRIORITY_CHANGED
    NOTE_ADDED
    EVIDENCE_ADDED
    ESCALATED
    CLOSED
    REOPENED
  }

  # Case entity relationships
  type CaseEntity implements Node {
    id: ID!
    entity: Entity!
    relationshipType: EntityRelationshipType!
    confidenceScore: Float
    createdAt: DateTime!
  }

  enum EntityRelationshipType {
    SUBJECT
    WITNESS
    RELATED_ACCOUNT
    BENEFICIARY
    COUNTERPARTY
    SUSPECT
    VICTIM
  }

  # Input types
  input CreateCaseInput {
    title: String!
    description: String
    caseType: CaseType!
    priority: Priority = MEDIUM
    assigneeId: ID
    tags: [String!]
    metadata: JSON
  }

  input UpdateCaseInput {
    title: String
    description: String
    priority: Priority
    tags: [String!]
    metadata: JSON
  }

  input EvidenceInput {
    evidenceType: EvidenceType!
    source: String!
    file: Upload
    metadata: JSON
    classification: Classification = INTERNAL
  }

  input CaseFilterInput {
    caseTypes: [CaseType!]
    priorities: [Priority!]
    statuses: [CaseStatus!]
    assigneeIds: [ID!]
    createdByIds: [ID!]
    dateRange: DateRangeInput
    tags: [String!]
    searchQuery: String
  }

  input DateRangeInput {
    from: DateTime!
    to: DateTime!
  }

  input CaseSortInput {
    field: CaseSortField!
    order: SortOrder!
  }

  enum CaseSortField {
    CREATED_AT
    UPDATED_AT
    PRIORITY
    STATUS
    CASE_NUMBER
    TITLE
  }

  # Connection types
  type CaseConnection {
    edges: [CaseEdge!]!
    pageInfo: PageInfo!
    totalCount: Int!
  }

  type CaseEdge {
    node: Case!
    cursor: String!
  }

  # Response types
  type CreateCaseResponse {
    success: Boolean!
    case: Case
    errors: [ValidationError!]
  }

  type UpdateCaseResponse {
    success: Boolean!
    case: Case
    errors: [ValidationError!]
  }

  type AssignCaseResponse {
    success: Boolean!
    case: Case
    message: String
  }

  type CloseCaseResponse {
    success: Boolean!
    case: Case
    message: String
  }

  type EscalateCaseResponse {
    success: Boolean!
    case: Case
    message: String
  }

  type AddCaseNoteResponse {
    success: Boolean!
    note: CaseNote
    errors: [ValidationError!]
  }

  type AttachEvidenceResponse {
    success: Boolean!
    evidence: Evidence
    errors: [ValidationError!]
  }

  # Statistics and analytics
  type CaseStatistics {
    totalCases: Int!
    openCases: Int!
    inProgressCases: Int!
    closedCases: Int!
    highPriorityCases: Int!
    averageResolutionTime: Float
    casesByType: [CaseTypeCount!]!
    casesByStatus: [CaseStatusCount!]!
  }

  type CaseTypeCount {
    caseType: CaseType!
    count: Int!
    percentage: Float!
  }

  type CaseStatusCount {
    status: CaseStatus!
    count: Int!
    percentage: Float!
  }

  type CaseAnalytics {
    timeRange: String!
    totalCases: Int!
    newCases: Int!
    closedCases: Int!
    avgResolutionTime: Float!
    trends: CaseTrends!
    topInvestigators: [InvestigatorStats!]!
  }

  type CaseTrends {
    daily: [DailyCaseStats!]!
    weekly: [WeeklyCaseStats!]!
    monthly: [MonthlyCaseStats!]!
  }

  type DailyCaseStats {
    date: DateTime!
    created: Int!
    closed: Int!
    inProgress: Int!
  }

  type WeeklyCaseStats {
    weekStart: DateTime!
    created: Int!
    closed: Int!
    backlog: Int!
  }

  type MonthlyCaseStats {
    month: String!
    created: Int!
    closed: Int!
    resolution_rate: Float!
  }

  type InvestigatorStats {
    investigator: User!
    activeCases: Int!
    closedCases: Int!
    avgResolutionTime: Float!
  }

  # Subscription payloads
  type CaseStatusChange {
    caseId: ID!
    oldStatus: CaseStatus!
    newStatus: CaseStatus!
    timestamp: DateTime!
    actor: User!
  }
`;
