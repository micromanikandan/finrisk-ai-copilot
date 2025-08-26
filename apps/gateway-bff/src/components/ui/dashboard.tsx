/**
 * Main Dashboard Component for FinRisk AI Copilot
 */

"use client";

import React, { useState, useEffect } from 'react';
import { useQuery } from '@apollo/client';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  AlertTriangle, 
  Shield, 
  TrendingUp, 
  Users, 
  FileText, 
  Clock,
  Search,
  Bot,
  Database
} from 'lucide-react';
import { CaseOverview } from '@/components/cases/case-overview';
import { RiskMetrics } from '@/components/analytics/risk-metrics';
import { AIInsights } from '@/components/ai/ai-insights';
import { RecentActivity } from '@/components/activity/recent-activity';
import { QuickActions } from '@/components/actions/quick-actions';
import { GET_DASHBOARD_DATA } from '@/graphql/queries/dashboard';

interface DashboardData {
  caseStatistics: {
    totalCases: number;
    openCases: number;
    inProgressCases: number;
    closedCases: number;
    highPriorityCases: number;
    averageResolutionTime: number;
  };
  riskMetrics: {
    highRiskTransactions: number;
    suspiciousPatterns: number;
    mlAlertsGenerated: number;
    falsePositiveRate: number;
  };
  systemHealth: {
    uptime: number;
    processingSpeed: number;
    errorRate: number;
    activeUsers: number;
  };
  recentAlerts: Array<{
    id: string;
    type: string;
    severity: string;
    message: string;
    timestamp: string;
  }>;
}

export default function Dashboard() {
  const { data, loading, error, refetch } = useQuery<{ dashboard: DashboardData }>(
    GET_DASHBOARD_DATA,
    {
      pollInterval: 30000, // Refresh every 30 seconds
      errorPolicy: 'partial'
    }
  );

  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    // Set up real-time updates
    const interval = setInterval(() => {
      refetch();
    }, 30000);

    return () => clearInterval(interval);
  }, [refetch]);

  if (loading && !data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Card className="p-6">
          <CardHeader>
            <CardTitle className="text-red-600">Error Loading Dashboard</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">{error.message}</p>
            <Button onClick={() => refetch()}>Retry</Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const dashboardData = data?.dashboard;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                FinRisk AI Copilot
              </h1>
              <p className="text-sm text-gray-500">
                Financial Crime Investigation Dashboard
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="outline" className="bg-green-50 text-green-700">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                System Healthy
              </Badge>
              <Button variant="outline" size="sm">
                <Search className="w-4 h-4 mr-2" />
                Quick Search
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Active Cases"
            value={dashboardData?.caseStatistics.openCases || 0}
            change={12}
            icon={<FileText className="w-6 h-6" />}
            color="blue"
          />
          <MetricCard
            title="High Risk Alerts"
            value={dashboardData?.riskMetrics.highRiskTransactions || 0}
            change={-8}
            icon={<AlertTriangle className="w-6 h-6" />}
            color="red"
          />
          <MetricCard
            title="ML Predictions"
            value={dashboardData?.riskMetrics.mlAlertsGenerated || 0}
            change={25}
            icon={<TrendingUp className="w-6 h-6" />}
            color="green"
          />
          <MetricCard
            title="Active Users"
            value={dashboardData?.systemHealth.activeUsers || 0}
            change={5}
            icon={<Users className="w-6 h-6" />}
            color="purple"
          />
        </div>

        {/* Main Dashboard Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-5">
            <TabsTrigger value="overview" className="flex items-center space-x-2">
              <Shield className="w-4 h-4" />
              <span>Overview</span>
            </TabsTrigger>
            <TabsTrigger value="cases" className="flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>Cases</span>
            </TabsTrigger>
            <TabsTrigger value="analytics" className="flex items-center space-x-2">
              <TrendingUp className="w-4 h-4" />
              <span>Analytics</span>
            </TabsTrigger>
            <TabsTrigger value="ai" className="flex items-center space-x-2">
              <Bot className="w-4 h-4" />
              <span>AI Copilot</span>
            </TabsTrigger>
            <TabsTrigger value="system" className="flex items-center space-x-2">
              <Database className="w-4 h-4" />
              <span>System</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                <CaseOverview data={dashboardData?.caseStatistics} />
              </div>
              <div>
                <QuickActions />
              </div>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RiskMetrics data={dashboardData?.riskMetrics} />
              <RecentActivity alerts={dashboardData?.recentAlerts} />
            </div>
          </TabsContent>

          <TabsContent value="cases">
            <CaseManagement />
          </TabsContent>

          <TabsContent value="analytics">
            <AnalyticsDashboard />
          </TabsContent>

          <TabsContent value="ai">
            <AIInsights />
          </TabsContent>

          <TabsContent value="system">
            <SystemMonitoring data={dashboardData?.systemHealth} />
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

// Metric Card Component
interface MetricCardProps {
  title: string;
  value: number;
  change: number;
  icon: React.ReactNode;
  color: 'blue' | 'red' | 'green' | 'purple';
}

function MetricCard({ title, value, change, icon, color }: MetricCardProps) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    red: 'bg-red-50 text-red-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600'
  };

  const isPositive = change > 0;

  return (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className="text-3xl font-bold text-gray-900">{value.toLocaleString()}</p>
            <div className="flex items-center mt-2">
              <span
                className={`text-sm font-medium ${
                  isPositive ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {isPositive ? '+' : ''}{change}%
              </span>
              <span className="text-sm text-gray-500 ml-1">vs last period</span>
            </div>
          </div>
          <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Placeholder components for tab content
function CaseManagement() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Case Management</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Comprehensive case management interface will be implemented here.</p>
      </CardContent>
    </Card>
  );
}

function AnalyticsDashboard() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Analytics Dashboard</CardTitle>
      </CardHeader>
      <CardContent>
        <p>Advanced analytics and reporting dashboard will be implemented here.</p>
      </CardContent>
    </Card>
  );
}

function SystemMonitoring({ data }: { data?: any }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>System Monitoring</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex justify-between">
            <span>System Uptime</span>
            <Badge variant="outline">{data?.uptime || 99.9}%</Badge>
          </div>
          <div className="flex justify-between">
            <span>Processing Speed</span>
            <Badge variant="outline">{data?.processingSpeed || 1250}ms avg</Badge>
          </div>
          <div className="flex justify-between">
            <span>Error Rate</span>
            <Badge variant="outline">{data?.errorRate || 0.02}%</Badge>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
