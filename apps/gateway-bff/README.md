# FinRisk AI Copilot - Frontend UI

A comprehensive, modern web interface for the FinRisk AI Copilot financial crime investigation platform. Built with Next.js, TypeScript, GraphQL, and Tailwind CSS.

## 🚀 Features

### Core Functionality
- **Dashboard Overview**: Real-time metrics, case statistics, and system health monitoring
- **Case Management**: Create, update, assign, and track investigation cases
- **AI-Powered Insights**: ML-driven risk analysis and pattern detection
- **Advanced Search**: Multi-faceted search across entities, transactions, and cases
- **Real-time Alerts**: Instant notifications for high-risk activities
- **Analytics & Reporting**: Comprehensive risk metrics and trend analysis

### Technical Features
- **Modern UI/UX**: Clean, responsive design with dark/light theme support
- **Real-time Updates**: Live data streaming with GraphQL subscriptions
- **Type Safety**: Full TypeScript implementation with GraphQL codegen
- **Performance**: Optimized with React Query caching and lazy loading
- **Accessibility**: WCAG compliant with keyboard navigation support
- **Mobile Responsive**: Optimized for tablets and mobile devices

## 🛠 Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + Radix UI
- **State Management**: Apollo Client + React Query
- **API**: GraphQL with Apollo Server
- **Icons**: Lucide React
- **Charts**: Recharts
- **Authentication**: Auth0 (configurable)
- **Testing**: Jest + Testing Library

## 📁 Project Structure

```
src/
├── app/                    # Next.js App Router
│   ├── globals.css        # Global styles
│   ├── layout.tsx         # Root layout
│   └── page.tsx           # Home page
├── components/            # React components
│   ├── ui/                # Reusable UI components
│   ├── layout/            # Layout components
│   ├── cases/             # Case management
│   ├── search/            # Search functionality
│   ├── ai/                # AI insights & chat
│   ├── analytics/         # Charts & metrics
│   └── activity/          # Activity feeds
├── graphql/               # GraphQL layer
│   ├── schema/            # GraphQL schema
│   ├── resolvers/         # GraphQL resolvers
│   ├── queries/           # Client queries
│   └── mutations/         # Client mutations
├── lib/                   # Utility functions
├── providers/             # React context providers
└── types/                 # TypeScript definitions
```

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ 
- npm 8+
- Access to FinRisk backend services

### Installation

1. **Install dependencies**:
   ```bash
   cd apps/gateway-bff
   npm install
   ```

2. **Environment Setup**:
   ```bash
   cp .env.example .env.local
   ```
   
   Configure the following variables:
   ```env
   # Application
   NEXT_PUBLIC_APP_URL=http://localhost:3000
   NEXT_PUBLIC_GRAPHQL_URL=http://localhost:3000/api/graphql
   
   # Backend Services
   CASE_SERVICE_URL=http://localhost:8081
   INGESTION_SERVICE_URL=http://localhost:8082
   ML_SCORING_SERVICE_URL=http://localhost:8083
   SEARCH_SERVICE_URL=http://localhost:8084
   COPILOT_SERVICE_URL=http://localhost:8085
   RULES_SERVICE_URL=http://localhost:8086
   ENTITY_SERVICE_URL=http://localhost:8087
   
   # Authentication (optional)
   AUTH0_SECRET=your-auth0-secret
   AUTH0_BASE_URL=http://localhost:3000
   AUTH0_ISSUER_BASE_URL=https://your-domain.auth0.com
   AUTH0_CLIENT_ID=your-client-id
   AUTH0_CLIENT_SECRET=your-client-secret
   ```

3. **Start Development Server**:
   ```bash
   npm run dev
   ```

4. **Access the Application**:
   Open [http://localhost:3000](http://localhost:3000) in your browser

## 🎨 UI Components

### Design System

The UI is built on a consistent design system with:

- **Color Palette**: Professional blue/navy theme with semantic colors
- **Typography**: Inter font family with size scales
- **Spacing**: 4px base unit with consistent spacing scale
- **Components**: Radix UI primitives with custom styling
- **Animations**: Subtle transitions and micro-interactions

### Key Components

#### Dashboard Components
- `Dashboard`: Main dashboard with metrics and insights
- `CaseOverview`: Case statistics and trends
- `RiskMetrics`: Risk analysis and scoring
- `RecentActivity`: Live activity feed
- `QuickActions`: Shortcut actions panel

#### Navigation
- `Sidebar`: Main navigation with collapsible sections
- `Header`: Top bar with search, notifications, and user menu
- `QuickSearchModal`: Global search with keyboard shortcuts

#### Case Management
- `CaseList`: Paginated case listing with filters
- `CaseDetail`: Comprehensive case view
- `CaseForm`: Create/edit case forms
- `CaseTimeline`: Activity timeline

#### AI Features
- `AIInsights`: AI-generated insights and recommendations
- `AIChat`: Interactive chat interface
- `MLModelStatus`: Model performance monitoring

### Theme Support

The application supports both light and dark themes:

```tsx
import { useTheme } from 'next-themes'

function Component() {
  const { theme, setTheme } = useTheme()
  // Component implementation
}
```

## 🔌 API Integration

### GraphQL Schema

The frontend communicates with backend services through a unified GraphQL API:

```graphql
type Query {
  dashboard: Dashboard!
  cases(filters: JSON): [Case!]!
  search(input: SearchInput!): SearchResponse!
  aiInsights: AIInsights!
}

type Mutation {
  createCase(input: CaseInput!): Case!
  updateCase(id: ID!, input: CaseInput!): Case!
  createAlert(input: AlertInput!): Alert!
}
```

### Data Fetching

Using Apollo Client for efficient data management:

```tsx
import { useQuery } from '@apollo/client'
import { GET_DASHBOARD_DATA } from '@/graphql/queries/dashboard'

function Dashboard() {
  const { data, loading, error } = useQuery(GET_DASHBOARD_DATA, {
    pollInterval: 30000, // Refresh every 30 seconds
  })
  
  // Component implementation
}
```

### Real-time Updates

GraphQL subscriptions for live data:

```tsx
import { useSubscription } from '@apollo/client'

function AlertsPanel() {
  const { data } = useSubscription(ALERT_CREATED_SUBSCRIPTION)
  // Handle real-time alert updates
}
```

## 🎯 Performance Optimization

### Code Splitting
- Route-based splitting with Next.js App Router
- Component-level lazy loading for heavy components
- Dynamic imports for non-critical features

### Caching Strategy
- Apollo Client cache with intelligent cache policies
- React Query for REST API calls
- Image optimization with Next.js Image component

### Bundle Optimization
- Tree-shaking with modern build tools
- Webpack bundle analyzer for size monitoring
- Tailwind CSS purging for minimal CSS bundle

## 🧪 Development

### Available Scripts

```bash
# Development
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server

# Code Quality
npm run lint         # Run ESLint
npm run lint:fix     # Fix linting issues
npm run type-check   # TypeScript checking

# Testing
npm run test         # Run unit tests
npm run test:watch   # Run tests in watch mode
npm run test:coverage # Run tests with coverage

# GraphQL
npm run generate:graphql  # Generate TypeScript types from schema
npm run generate:schema   # Generate GraphQL schema

# Storybook
npm run storybook         # Start Storybook dev server
npm run build-storybook   # Build Storybook for production
```

### Code Standards

- **TypeScript**: Strict mode enabled with comprehensive type checking
- **ESLint**: Extended Next.js configuration with custom rules
- **Prettier**: Consistent code formatting
- **Husky**: Git hooks for pre-commit validation

### Development Workflow

1. **Create Feature Branch**: `git checkout -b feature/new-feature`
2. **Implement Changes**: Follow component structure and patterns
3. **Add Tests**: Unit tests for complex logic
4. **Update Documentation**: Update README and comments
5. **Create Pull Request**: Include description and testing notes

## 📱 Responsive Design

The interface is fully responsive with breakpoints:

- **Mobile**: 320px - 768px (single column layout)
- **Tablet**: 768px - 1024px (adapted sidebar, grid layouts)
- **Desktop**: 1024px+ (full sidebar, multi-column layouts)

Key responsive features:
- Collapsible sidebar on mobile
- Adaptive navigation menu
- Responsive data tables with horizontal scroll
- Touch-friendly interactive elements

## 🔒 Security

### Authentication
- JWT token-based authentication
- Role-based access control (RBAC)
- Session management with secure storage

### Data Protection
- Input sanitization for XSS prevention
- CSRF protection with Next.js
- Secure HTTP headers configuration
- Content Security Policy (CSP)

### API Security
- GraphQL query depth limiting
- Rate limiting on sensitive operations
- Input validation with Zod schemas

## 🚀 Deployment

### Build Configuration

```bash
# Production build
npm run build

# Build with analysis
npm run build && npm run analyze
```

### Environment Variables

Required for production:

```env
NODE_ENV=production
NEXT_PUBLIC_APP_URL=https://your-domain.com
NEXT_PUBLIC_GRAPHQL_URL=https://your-domain.com/api/graphql

# Backend service URLs
CASE_SERVICE_URL=https://case-service.your-domain.com
# ... other service URLs

# Authentication
AUTH0_SECRET=your-production-secret
AUTH0_BASE_URL=https://your-domain.com
AUTH0_ISSUER_BASE_URL=https://your-auth-domain.auth0.com
AUTH0_CLIENT_ID=your-production-client-id
AUTH0_CLIENT_SECRET=your-production-client-secret
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

### Coding Guidelines

- Follow TypeScript best practices
- Use functional components with hooks
- Implement proper error boundaries
- Add JSDoc comments for complex functions
- Follow the established component patterns

### Component Development

When creating new components:

1. **Create in appropriate directory**: Group by feature/domain
2. **Use TypeScript**: Define clear interfaces for props
3. **Add Storybook stories**: Document component usage
4. **Include tests**: Unit tests for logic, integration tests for complex flows
5. **Follow naming conventions**: PascalCase for components, camelCase for functions

## 📄 License

This project is part of the FinRisk AI Copilot platform. See the main project LICENSE file for details.

## 🆘 Support

For development questions and issues:

1. Check the [main project documentation](../../README.md)
2. Review the [architecture documentation](../../docs/ARCHITECTURE.md)
3. Create an issue in the project repository
4. Contact the development team

---

**FinRisk AI Copilot** - Advanced Financial Crime Investigation Platform
