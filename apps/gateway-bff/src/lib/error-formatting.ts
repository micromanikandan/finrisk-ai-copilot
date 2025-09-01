import { GraphQLError, GraphQLFormattedError } from 'graphql'

export function formatError(error: GraphQLError): GraphQLFormattedError {
  // Log the error for debugging
  console.error('GraphQL Error:', {
    message: error.message,
    locations: error.locations,
    path: error.path,
    extensions: error.extensions,
  })

  // Don't expose internal errors in production
  if (process.env.NODE_ENV === 'production') {
    // Filter out internal errors
    if (error.message.includes('Internal')) {
      return new Error('An internal error occurred. Please try again later.')
    }
  }

  // Return formatted error
  return {
    message: error.message,
    locations: error.locations,
    path: error.path,
    extensions: {
      code: error.extensions?.code || 'INTERNAL_ERROR',
      timestamp: new Date().toISOString(),
      ...error.extensions,
    },
  }
}
