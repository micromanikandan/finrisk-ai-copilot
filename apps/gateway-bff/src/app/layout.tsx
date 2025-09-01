import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ApolloWrapper } from '@/lib/apollo-wrapper'
import { AuthProvider } from '@/providers/auth-provider'
import { ThemeProvider } from '@/providers/theme-provider'
import { ToastProvider } from '@/providers/toast-provider'
import { QueryProvider } from '@/providers/query-provider'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'FinRisk AI Copilot',
  description: 'Advanced Financial Crime Investigation Platform with AI-powered insights',
  keywords: ['financial crime', 'risk management', 'AI', 'compliance', 'investigation'],
  authors: [{ name: 'FinRisk Team' }],
  creator: 'FinRisk AI Copilot',
  publisher: 'FinRisk',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: '/',
    title: 'FinRisk AI Copilot',
    description: 'Advanced Financial Crime Investigation Platform with AI-powered insights',
    siteName: 'FinRisk AI Copilot',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'FinRisk AI Copilot',
    description: 'Advanced Financial Crime Investigation Platform with AI-powered insights',
  },
  robots: {
    index: false,
    follow: false,
    googleBot: {
      index: false,
      follow: false,
    },
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <AuthProvider>
          <ThemeProvider>
            <QueryProvider>
              <ApolloWrapper>
                <ToastProvider>
                  {children}
                </ToastProvider>
              </ApolloWrapper>
            </QueryProvider>
          </ThemeProvider>
        </AuthProvider>
      </body>
    </html>
  )
}
