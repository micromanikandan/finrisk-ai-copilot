import { ApolloServerPlugin } from '@apollo/server'

// Plugin for request logging
const requestLoggingPlugin: ApolloServerPlugin = {
  async requestDidStart() {
    return {
      async didResolveOperation(requestContext) {
        if (process.env.NODE_ENV !== 'production') {
          console.log(`GraphQL Operation: ${requestContext.request.operationName}`)
        }
      },
      async didEncounterErrors(requestContext) {
        console.error(`GraphQL errors for operation ${requestContext.request.operationName}:`, 
          requestContext.errors)
      },
    }
  },
}

// Plugin for performance monitoring
const performancePlugin: ApolloServerPlugin = {
  async requestDidStart() {
    const startTime = Date.now()
    
    return {
      async willSendResponse(requestContext) {
        const duration = Date.now() - startTime
        
        if (duration > 1000) { // Log slow queries (> 1 second)
          console.warn(`Slow GraphQL query detected: ${requestContext.request.operationName} took ${duration}ms`)
        }
        
        // Add performance headers
        if (requestContext.response.http) {
          requestContext.response.http.headers.set('X-Response-Time', `${duration}ms`)
        }
      },
    }
  },
}

// Plugin for authentication
const authPlugin: ApolloServerPlugin = {
  async requestDidStart() {
    return {
      async didResolveOperation(requestContext) {
        const operation = requestContext.request.operationName
        const publicOperations = ['IntrospectionQuery']
        
        // Skip auth for public operations
        if (publicOperations.includes(operation || '')) {
          return
        }
        
        // Check if user is authenticated (this would be more sophisticated in production)
        const context = requestContext.contextValue as any
        if (!context.user && process.env.NODE_ENV === 'production') {
          throw new Error('Authentication required')
        }
      },
    }
  },
}

export const plugins = [
  requestLoggingPlugin,
  performancePlugin,
  authPlugin,
]
