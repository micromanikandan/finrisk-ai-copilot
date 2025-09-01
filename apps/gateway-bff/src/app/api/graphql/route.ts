import { NextRequest } from 'next/server'
import { ApolloServer } from '@apollo/server'
import { startServerAndCreateNextHandler } from '@as-integrations/next'
import { typeDefs } from '@/graphql/schema'
import { resolvers } from '@/graphql/resolvers'
import { createContext } from '@/graphql/context'
import { formatError } from '@/lib/error-formatting'
import { plugins } from '@/graphql/plugins'

const server = new ApolloServer({
  typeDefs,
  resolvers,
  formatError,
  plugins,
  introspection: process.env.NODE_ENV === 'development',
  includeStacktraceInErrorResponses: process.env.NODE_ENV === 'development',
})

const handler = startServerAndCreateNextHandler<NextRequest>(server, {
  context: createContext,
})

export { handler as GET, handler as POST }
