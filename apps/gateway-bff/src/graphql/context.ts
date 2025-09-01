import { NextRequest } from 'next/server'

export interface GraphQLContext {
  req: NextRequest
  user?: {
    id: string
    email: string
    name: string
    role: string
  }
  services: {
    caseService: string
    ingestionService: string
    mlScoringService: string
    searchService: string
    copilotService: string
    rulesService: string
    entityService: string
  }
}

export async function createContext({ req }: { req?: NextRequest }): Promise<GraphQLContext> {
  // Extract user from auth token
  const authHeader = req?.headers.get('authorization')
  let user = null
  
  if (authHeader && authHeader.startsWith('Bearer ')) {
    const token = authHeader.substring(7)
    // In production, validate JWT token and extract user info
    // For now, use mock user data
    user = {
      id: '1',
      email: 'john.doe@finrisk.com',
      name: 'John Doe',
      role: 'Senior Investigator'
    }
  }

  return {
    req: req || {} as NextRequest,
    user,
    services: {
      caseService: process.env.CASE_SERVICE_URL || 'http://localhost:8081',
      ingestionService: process.env.INGESTION_SERVICE_URL || 'http://localhost:8082',
      mlScoringService: process.env.ML_SCORING_SERVICE_URL || 'http://localhost:8083',
      searchService: process.env.SEARCH_SERVICE_URL || 'http://localhost:8084',
      copilotService: process.env.COPILOT_SERVICE_URL || 'http://localhost:8085',
      rulesService: process.env.RULES_SERVICE_URL || 'http://localhost:8086',
      entityService: process.env.ENTITY_SERVICE_URL || 'http://localhost:8087',
    }
  }
}
