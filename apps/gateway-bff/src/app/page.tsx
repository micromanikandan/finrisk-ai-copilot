/**
 * Main Application Page - FinRisk AI Copilot Dashboard
 */

import { Suspense } from 'react'
import Dashboard from '@/components/ui/dashboard'
import { AppLayout } from '@/components/layout/app-layout'
import { DashboardSkeleton } from '@/components/ui/dashboard-skeleton'

export default function HomePage() {
  return (
    <AppLayout>
      <Dashboard />
    </AppLayout>
  )
}
