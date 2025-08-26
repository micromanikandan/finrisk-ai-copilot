/**
 * GraphQL Schema - Unified API for FinRisk services
 */

import { mergeTypeDefs } from '@graphql-tools/merge';
import { caseTypeDefs } from './case.graphql';
import { searchTypeDefs } from './search.graphql';
import { mlScoringTypeDefs } from './ml-scoring.graphql';
import { rulesTypeDefs } from './rules.graphql';
import { ingestionTypeDefs } from './ingestion.graphql';
import { copilotTypeDefs } from './copilot.graphql';
import { entityTypeDefs } from './entity.graphql';
import { userTypeDefs } from './user.graphql';

// Base schema with common types
const baseTypeDefs = `#graphql
  scalar DateTime
  scalar JSON
  scalar Upload

  type Query {
    # Health check
    health: String!
  }

  type Mutation {
    # Placeholder - actual mutations defined in service schemas
    _placeholder: String
  }

  type Subscription {
    # Real-time updates
    _placeholder: String
  }

  # Common interfaces
  interface Node {
    id: ID!
  }

  interface Timestamped {
    createdAt: DateTime!
    updatedAt: DateTime!
  }

  interface TenantScoped {
    tenantId: String!
    cellId: String!
  }

  # Common enums
  enum SortOrder {
    ASC
    DESC
  }

  enum Status {
    ACTIVE
    INACTIVE
    PENDING
    COMPLETED
    FAILED
    CANCELLED
  }

  # Pagination types
  type PageInfo {
    hasNextPage: Boolean!
    hasPreviousPage: Boolean!
    startCursor: String
    endCursor: String
    totalCount: Int!
  }

  input PaginationInput {
    first: Int
    after: String
    last: Int
    before: String
  }

  # Error types
  type Error {
    code: String!
    message: String!
    path: [String!]
    extensions: JSON
  }

  type ValidationError {
    field: String!
    message: String!
    code: String!
  }

  # Response wrapper types
  type SuccessResponse {
    success: Boolean!
    message: String
  }

  type ErrorResponse {
    success: Boolean!
    errors: [Error!]!
  }

  # Generic filter input
  input FilterInput {
    field: String!
    operator: FilterOperator!
    value: String!
  }

  enum FilterOperator {
    EQUALS
    NOT_EQUALS
    CONTAINS
    NOT_CONTAINS
    STARTS_WITH
    ENDS_WITH
    GREATER_THAN
    GREATER_THAN_OR_EQUAL
    LESS_THAN
    LESS_THAN_OR_EQUAL
    IN
    NOT_IN
    IS_NULL
    IS_NOT_NULL
  }

  # Metrics and analytics
  type Metric {
    name: String!
    value: Float!
    unit: String
    timestamp: DateTime!
    metadata: JSON
  }

  type Analytics {
    totalItems: Int!
    timeRange: String!
    metrics: [Metric!]!
    trends: JSON
  }
`;

export const typeDefs = mergeTypeDefs([
  baseTypeDefs,
  caseTypeDefs,
  searchTypeDefs,
  mlScoringTypeDefs,
  rulesTypeDefs,
  ingestionTypeDefs,
  copilotTypeDefs,
  entityTypeDefs,
  userTypeDefs,
]);
