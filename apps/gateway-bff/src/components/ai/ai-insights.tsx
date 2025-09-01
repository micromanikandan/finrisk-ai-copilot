'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Bot, 
  Brain, 
  MessageSquare, 
  Lightbulb, 
  TrendingUp, 
  Target, 
  Zap,
  Send,
  Sparkles,
  ChevronRight
} from 'lucide-react'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

const aiInsights = [
  {
    id: 1,
    type: 'risk_assessment',
    title: 'High-Risk Pattern Detected',
    description: 'ML model identified unusual transaction velocity for entity ENT-4521. Risk score increased from 45 to 87.',
    confidence: 94,
    priority: 'high',
    timestamp: '15 minutes ago',
    recommendations: [
      'Escalate to senior investigator',
      'Request additional KYC documentation',
      'Monitor future transactions closely'
    ]
  },
  {
    id: 2,
    type: 'anomaly_detection',
    title: 'Transaction Anomaly',
    description: 'Detected structuring pattern across multiple accounts with same beneficial owner.',
    confidence: 87,
    priority: 'medium',
    timestamp: '1 hour ago',
    recommendations: [
      'Cross-reference account relationships',
      'Analyze transaction timing patterns',
      'Review account opening dates'
    ]
  },
  {
    id: 3,
    type: 'entity_linking',
    title: 'Entity Connection Discovery',
    description: 'AI discovered previously unknown connection between flagged entity and known high-risk individual.',
    confidence: 92,
    priority: 'high',
    timestamp: '2 hours ago',
    recommendations: [
      'Update entity risk score',
      'Review historical transactions',
      'Add to watchlist monitoring'
    ]
  },
]

const aiRecommendations = [
  {
    id: 1,
    title: 'Optimize Investigation Workflow',
    description: 'Based on case closure patterns, prioritize fraud cases during morning hours for 23% faster resolution.',
    impact: 'High',
    effort: 'Low',
    category: 'workflow'
  },
  {
    id: 2,
    title: 'Enhanced Risk Scoring',
    description: 'Include social network analysis in risk scoring to improve detection accuracy by estimated 15%.',
    impact: 'Medium',
    effort: 'Medium',
    category: 'model'
  },
  {
    id: 3,
    title: 'Alert Tuning',
    description: 'Adjust transaction velocity thresholds to reduce false positives while maintaining detection rate.',
    impact: 'Medium',
    effort: 'Low',
    category: 'rules'
  },
]

const chatHistory = [
  { id: 1, type: 'user', message: 'What are the key risk indicators for case CASE-2024-045?', timestamp: '10:30 AM' },
  { id: 2, type: 'ai', message: 'For case CASE-2024-045, the primary risk indicators include:\n\n1. **Transaction Velocity**: 450% increase in transaction volume over 72 hours\n2. **Geographic Risk**: Transactions involving high-risk jurisdictions\n3. **Entity Risk**: Counterparty flagged in previous investigations\n4. **Pattern Analysis**: Structuring behavior detected\n\nRecommendation: Escalate to Level 2 investigation with focus on beneficial ownership analysis.', timestamp: '10:30 AM' },
  { id: 3, type: 'user', message: 'Generate a summary report for this case', timestamp: '10:35 AM' },
  { id: 4, type: 'ai', message: 'I\'ve generated a comprehensive summary report for CASE-2024-045. The report includes risk assessment, timeline analysis, and recommended actions. Would you like me to export it to PDF or share it with your team?', timestamp: '10:35 AM' },
]

export function AIInsights() {
  const [chatMessage, setChatMessage] = useState('')

  const handleSendMessage = () => {
    if (chatMessage.trim()) {
      // Handle sending message to AI
      setChatMessage('')
    }
  }

  return (
    <div className="space-y-6">
      <Tabs defaultValue="insights" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="insights" className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4" />
            Insights
          </TabsTrigger>
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            AI Chat
          </TabsTrigger>
          <TabsTrigger value="recommendations" className="flex items-center gap-2">
            <Target className="h-4 w-4" />
            Recommendations
          </TabsTrigger>
          <TabsTrigger value="models" className="flex items-center gap-2">
            <Brain className="h-4 w-4" />
            Models
          </TabsTrigger>
        </TabsList>

        {/* AI Insights Tab */}
        <TabsContent value="insights" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-purple-600" />
                Latest AI Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {aiInsights.map((insight) => (
                <div key={insight.id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <Bot className="h-5 w-5 text-blue-600" />
                      <h4 className="font-medium text-gray-900">{insight.title}</h4>
                      <Badge 
                        variant="outline"
                        className={`text-xs ${
                          insight.priority === 'high' ? 'border-red-200 text-red-700' :
                          insight.priority === 'medium' ? 'border-yellow-200 text-yellow-700' :
                          'border-green-200 text-green-700'
                        }`}
                      >
                        {insight.priority}
                      </Badge>
                    </div>
                    <span className="text-xs text-gray-500">{insight.timestamp}</span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{insight.description}</p>
                  
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs text-gray-500">Confidence:</span>
                      <div className="w-20 h-2 bg-gray-200 rounded-full">
                        <div 
                          className="h-2 bg-green-500 rounded-full" 
                          style={{ width: `${insight.confidence}%` }}
                        />
                      </div>
                      <span className="text-xs font-medium text-gray-700">{insight.confidence}%</span>
                    </div>
                    <Button variant="ghost" size="sm">
                      View Details <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                  
                  <div className="bg-blue-50 rounded-lg p-3">
                    <h5 className="text-xs font-medium text-blue-800 mb-2">AI Recommendations:</h5>
                    <ul className="text-xs text-blue-700 space-y-1">
                      {insight.recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <span className="text-blue-400 mt-0.5">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Chat Tab */}
        <TabsContent value="chat" className="space-y-4">
          <Card className="h-[600px] flex flex-col">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-blue-600" />
                AI Investigation Assistant
                <Badge variant="outline" className="ml-auto">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-1" />
                  Online
                </Badge>
              </CardTitle>
            </CardHeader>
            <CardContent className="flex-1 flex flex-col">
              {/* Chat History */}
              <div className="flex-1 overflow-y-auto space-y-4 mb-4 custom-scrollbar">
                {chatHistory.map((message) => (
                  <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                    <div className={`max-w-[80%] rounded-lg p-3 ${
                      message.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="text-sm whitespace-pre-line">{message.message}</p>
                      <p className={`text-xs mt-1 ${
                        message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {message.timestamp}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Chat Input */}
              <div className="flex items-center space-x-2 border-t pt-4">
                <input
                  type="text"
                  placeholder="Ask AI about cases, patterns, or risk analysis..."
                  value={chatMessage}
                  onChange={(e) => setChatMessage(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <Button onClick={handleSendMessage} disabled={!chatMessage.trim()}>
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Recommendations Tab */}
        <TabsContent value="recommendations" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-green-600" />
                AI-Powered Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {aiRecommendations.map((rec) => (
                <div key={rec.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="font-medium text-gray-900">{rec.title}</h4>
                    <Badge variant="outline" className="text-xs">
                      {rec.category}
                    </Badge>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{rec.description}</p>
                  
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-1">
                        <span className="text-xs text-gray-500">Impact:</span>
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${
                            rec.impact === 'High' ? 'border-green-200 text-green-700' :
                            rec.impact === 'Medium' ? 'border-yellow-200 text-yellow-700' :
                            'border-gray-200 text-gray-700'
                          }`}
                        >
                          {rec.impact}
                        </Badge>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span className="text-xs text-gray-500">Effort:</span>
                        <Badge 
                          variant="outline" 
                          className={`text-xs ${
                            rec.effort === 'Low' ? 'border-green-200 text-green-700' :
                            rec.effort === 'Medium' ? 'border-yellow-200 text-yellow-700' :
                            'border-red-200 text-red-700'
                          }`}
                        >
                          {rec.effort}
                        </Badge>
                      </div>
                    </div>
                    <Button variant="outline" size="sm">
                      Implement
                    </Button>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Models Tab */}
        <TabsContent value="models" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Risk Scoring Model</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Version</span>
                    <span className="text-sm font-medium">v2.1.3</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Accuracy</span>
                    <span className="text-sm font-medium text-green-600">94.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Last Updated</span>
                    <span className="text-sm font-medium">2 days ago</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Status</span>
                    <Badge variant="outline" className="text-green-700 border-green-200">
                      Active
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Anomaly Detection</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Version</span>
                    <span className="text-sm font-medium">v1.8.2</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Precision</span>
                    <span className="text-sm font-medium text-green-600">89.7%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Last Updated</span>
                    <span className="text-sm font-medium">1 week ago</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Status</span>
                    <Badge variant="outline" className="text-green-700 border-green-200">
                      Active
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Entity Resolution</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Version</span>
                    <span className="text-sm font-medium">v1.4.1</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Match Rate</span>
                    <span className="text-sm font-medium text-green-600">96.8%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Last Updated</span>
                    <span className="text-sm font-medium">5 days ago</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Status</span>
                    <Badge variant="outline" className="text-green-700 border-green-200">
                      Active
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Pattern Recognition</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Version</span>
                    <span className="text-sm font-medium">v3.0.1</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Detection Rate</span>
                    <span className="text-sm font-medium text-green-600">91.5%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Last Updated</span>
                    <span className="text-sm font-medium">3 days ago</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Status</span>
                    <Badge variant="outline" className="text-yellow-700 border-yellow-200">
                      Training
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
