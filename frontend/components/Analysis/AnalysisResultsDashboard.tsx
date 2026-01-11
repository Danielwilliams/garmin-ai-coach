'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { 
  ArrowLeft, 
  FileText, 
  Download, 
  Clock, 
  Zap, 
  DollarSign,
  Target,
  TrendingUp,
  Calendar,
  BarChart,
  FileDown,
  Loader2,
  AlertCircle,
  CheckCircle,
  Activity,
  Heart,
  Brain,
  Award,
  MapPin,
  Timer,
  RefreshCw,
  Eye,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { AnalysisWithResults, AnalysisResult } from '@/types/analysis';
import { analysisAPI } from '@/lib/api';
import Button from '@/components/ui/Button';
import TrainingMetricsChart from './TrainingMetricsChart';

interface AnalysisResultsDashboardProps {
  analysisId: string;
}

const AnalysisResultsDashboard: React.FC<AnalysisResultsDashboardProps> = ({ analysisId }) => {
  const [analysis, setAnalysis] = useState<AnalysisWithResults | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'results' | 'plan'>('overview');
  const [expandedResult, setExpandedResult] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);
  const [isExportingData, setIsExportingData] = useState(false);
  const [isExportingPlan, setIsExportingPlan] = useState(false);
  const router = useRouter();

  useEffect(() => {
    fetchAnalysisData();
  }, [analysisId]);

  const fetchAnalysisData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const analysisData = await analysisAPI.getAnalysis(analysisId);
      setAnalysis(analysisData);
    } catch (err: any) {
      setError(err.detail || 'Failed to load analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = {
      pending: { bg: 'bg-yellow-100', text: 'text-yellow-800', icon: Clock },
      running: { bg: 'bg-blue-100', text: 'text-blue-800', icon: RefreshCw },
      completed: { bg: 'bg-green-100', text: 'text-green-800', icon: CheckCircle },
      failed: { bg: 'bg-red-100', text: 'text-red-800', icon: AlertCircle },
      cancelled: { bg: 'bg-gray-100', text: 'text-gray-800', icon: AlertCircle }
    };

    const config = statusConfig[status as keyof typeof statusConfig] || statusConfig.pending;
    const Icon = config.icon;

    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.text}`}>
        <Icon className="w-4 h-4 mr-1" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const getAgentIcon = (nodeName: string) => {
    const nodeConfig = {
      'metrics_summarizer': { icon: BarChart, color: 'text-blue-600', name: 'Metrics' },
      'physiology_summarizer': { icon: Heart, color: 'text-red-600', name: 'Physiology' },
      'activity_summarizer': { icon: Activity, color: 'text-green-600', name: 'Activity' },
      'metrics_expert': { icon: TrendingUp, color: 'text-blue-700', name: 'Metrics Expert' },
      'physiology_expert': { icon: Brain, color: 'text-red-700', name: 'Physiology Expert' },
      'activity_expert': { icon: Award, color: 'text-green-700', name: 'Activity Expert' },
      'synthesis': { icon: Brain, color: 'text-purple-600', name: 'Synthesis' },
      'formatting': { icon: FileText, color: 'text-orange-600', name: 'Formatting' },
      'planning': { icon: Calendar, color: 'text-purple-700', name: 'Planning' }
    };

    const config = nodeConfig[nodeName as keyof typeof nodeConfig] || { 
      icon: FileText, 
      color: 'text-gray-600', 
      name: nodeName.replace(/_/g, ' ').replace(/\\b\\w/g, l => l.toUpperCase()) 
    };
    
    const Icon = config.icon;
    return { Icon, color: config.color, name: config.name };
  };

  const formatContent = (content: string) => {
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  };

  const formatWeeklyPlan = (weeklyPlan: any) => {
    if (typeof weeklyPlan === 'string') {
      return weeklyPlan;
    }
    
    if (typeof weeklyPlan === 'object' && weeklyPlan !== null) {
      // Try to format structured weekly plan
      if (Array.isArray(weeklyPlan)) {
        return weeklyPlan.map((week: any, index: number) => (
          <div key={index} className="mb-6 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-semibold text-gray-900 mb-3">Week {index + 1}</h4>
            {typeof week === 'object' ? (
              <div className="space-y-2">
                {Object.entries(week).map(([day, workout]: [string, any]) => (
                  <div key={day} className="flex justify-between items-start">
                    <span className="font-medium text-gray-700 capitalize">{day}:</span>
                    <span className="text-gray-600 text-sm flex-1 ml-2">
                      {typeof workout === 'string' ? workout : JSON.stringify(workout)}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-600">{week}</p>
            )}
          </div>
        ));
      } else {
        // Object format weekly plan
        return (
          <div className="space-y-4">
            {Object.entries(weeklyPlan).map(([key, value]: [string, any]) => (
              <div key={key} className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2 capitalize">
                  {key.replace(/_/g, ' ')}
                </h4>
                <div className="text-gray-600">
                  {typeof value === 'string' ? value : JSON.stringify(value, null, 2)}
                </div>
              </div>
            ))}
          </div>
        );
      }
    }
    
    return <pre className="bg-gray-50 p-4 rounded text-sm overflow-x-auto">{JSON.stringify(weeklyPlan, null, 2)}</pre>;
  };

  const handleGenerateReport = async () => {
    setIsGeneratingReport(true);
    try {
      const response = await analysisAPI.generateReport(analysisId);
      window.open(response.download_url, '_blank');
    } catch (error: any) {
      alert('Failed to generate report: ' + (error.detail || error.message));
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const handleExportData = async (format: 'json' | 'csv') => {
    setIsExportingData(true);
    try {
      const response = await analysisAPI.exportData(analysisId, format);
      window.open(response.download_url, '_blank');
    } catch (error: any) {
      alert('Failed to export data: ' + (error.detail || error.message));
    } finally {
      setIsExportingData(false);
    }
  };

  const handleExportWeeklyPlan = async () => {
    setIsExportingPlan(true);
    try {
      const response = await analysisAPI.exportWeeklyPlan(analysisId);
      window.open(response.download_url, '_blank');
    } catch (error: any) {
      alert('Failed to export weekly plan: ' + (error.detail || error.message));
    } finally {
      setIsExportingPlan(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading analysis results...</p>
        </div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 text-red-500" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Analysis Not Found</h2>
          <p className="text-gray-600 mb-4">{error || 'The requested analysis could not be found.'}</p>
          <Button onClick={() => router.push('/analysis')} className="flex items-center mx-auto">
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Analysis
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => router.push('/analysis')}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Training Analysis Results</h1>
                <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                  <span>{analysis.training_config_name}</span>
                  <span>•</span>
                  <span>{new Date(analysis.created_at).toLocaleDateString()}</span>
                  <span>•</span>
                  <span className="capitalize">{analysis.analysis_type}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              {getStatusBadge(analysis.status)}
              
              {analysis.status === 'completed' && (
                <div className="flex items-center space-x-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleGenerateReport}
                    disabled={isGeneratingReport}
                    className="flex items-center"
                  >
                    {isGeneratingReport ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <FileDown className="w-4 h-4 mr-2" />
                    )}
                    Generate Report
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleExportData('json')}
                    disabled={isExportingData}
                    className="flex items-center"
                  >
                    {isExportingData ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <Download className="w-4 h-4 mr-2" />
                    )}
                    Export Data
                  </Button>
                </div>
              )}
            </div>
          </div>

          {/* Tab Navigation */}
          <div className="flex space-x-8 border-b">
            <button
              onClick={() => setActiveTab('overview')}
              className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'overview'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('results')}
              className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'results'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Detailed Results ({analysis.results?.length || 0})
            </button>
            <button
              onClick={() => setActiveTab('plan')}
              className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === 'plan'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
              disabled={!analysis.weekly_plan}
            >
              Training Plan
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Metrics Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg p-6 border">
                <div className="flex items-center">
                  <Clock className="w-8 h-8 text-blue-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">Processing Time</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {analysis.start_date && analysis.end_date 
                        ? `${Math.ceil((new Date(analysis.end_date).getTime() - new Date(analysis.start_date).getTime()) / (1000 * 60))}m`
                        : 'In progress'
                      }
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg p-6 border">
                <div className="flex items-center">
                  <Zap className="w-8 h-8 text-yellow-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">Tokens Used</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {analysis.total_tokens.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg p-6 border">
                <div className="flex items-center">
                  <DollarSign className="w-8 h-8 text-green-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">Estimated Cost</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {analysis.estimated_cost || '$0.00'}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg p-6 border">
                <div className="flex items-center">
                  <TrendingUp className="w-8 h-8 text-purple-600" />
                  <div className="ml-4">
                    <p className="text-sm text-gray-500">Progress</p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {analysis.progress_percentage}%
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Main Analysis Content */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Summary */}
              {analysis.summary && (
                <div className="bg-white rounded-lg p-6 border">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <FileText className="w-5 h-5 mr-2 text-blue-600" />
                    Executive Summary
                  </h3>
                  <div 
                    className="prose max-w-none text-gray-700"
                    dangerouslySetInnerHTML={{ __html: formatContent(analysis.summary) }}
                  />
                </div>
              )}

              {/* Recommendations */}
              {analysis.recommendations && (
                <div className="bg-white rounded-lg p-6 border">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <Target className="w-5 h-5 mr-2 text-green-600" />
                    Key Recommendations
                  </h3>
                  <div 
                    className="prose max-w-none text-gray-700"
                    dangerouslySetInnerHTML={{ __html: formatContent(analysis.recommendations) }}
                  />
                </div>
              )}
            </div>

            {/* Training Metrics Chart */}
            {analysis.data_summary && (
              <TrainingMetricsChart 
                data={analysis.data_summary} 
                className="lg:col-span-2" 
              />
            )}

            {/* Agent Progress */}
            {analysis.results && analysis.results.length > 0 && (
              <div className="bg-white rounded-lg p-6 border">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Agent Analysis Progress</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {analysis.results.map((result) => {
                    const { Icon, color, name } = getAgentIcon(result.node_name);
                    return (
                      <div key={result.id} className="flex items-center p-3 bg-gray-50 rounded-lg">
                        <Icon className={`w-6 h-6 ${color} mr-3`} />
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{name}</p>
                          <p className="text-sm text-gray-500">{result.tokens_used} tokens</p>
                        </div>
                        <CheckCircle className="w-5 h-5 text-green-500" />
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'results' && (
          <div className="space-y-4">
            {analysis.results && analysis.results.length > 0 ? (
              analysis.results.map((result) => {
                const { Icon, color, name } = getAgentIcon(result.node_name);
                const isExpanded = expandedResult === result.id;
                
                return (
                  <div key={result.id} className="bg-white rounded-lg border">
                    <div 
                      className="p-6 cursor-pointer hover:bg-gray-50 transition-colors"
                      onClick={() => setExpandedResult(isExpanded ? null : result.id)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <Icon className={`w-6 h-6 ${color}`} />
                          <div>
                            <h3 className="text-lg font-medium text-gray-900">{result.title}</h3>
                            <div className="flex items-center space-x-4 text-sm text-gray-500">
                              <span>Agent: {name}</span>
                              <span>•</span>
                              <span>{result.tokens_used} tokens</span>
                              {result.processing_time && (
                                <>
                                  <span>•</span>
                                  <span>{result.processing_time}s processing</span>
                                </>
                              )}
                            </div>
                          </div>
                        </div>
                        {isExpanded ? (
                          <ChevronUp className="w-5 h-5 text-gray-400" />
                        ) : (
                          <ChevronDown className="w-5 h-5 text-gray-400" />
                        )}
                      </div>
                    </div>

                    {isExpanded && (
                      <div className="px-6 pb-6 border-t bg-gray-50">
                        {result.content && (
                          <div className="mt-4">
                            <h4 className="font-medium text-gray-900 mb-2">Analysis Content</h4>
                            <div 
                              className="prose max-w-none text-gray-700 bg-white p-4 rounded border"
                              dangerouslySetInnerHTML={{ __html: formatContent(result.content) }}
                            />
                          </div>
                        )}

                        {result.data && (
                          <div className="mt-4">
                            <h4 className="font-medium text-gray-900 mb-2">Structured Data</h4>
                            <pre className="bg-white p-4 rounded border text-xs overflow-x-auto">
                              {JSON.stringify(result.data, null, 2)}
                            </pre>
                          </div>
                        )}

                        {result.file_path && (
                          <div className="mt-4">
                            <Button variant="outline" size="sm" className="flex items-center">
                              <Download className="w-4 h-4 mr-2" />
                              Download File
                            </Button>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })
            ) : (
              <div className="text-center py-12">
                <FileText className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Detailed Results</h3>
                <p className="text-gray-500">Detailed analysis results are not yet available.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'plan' && (
          <div className="space-y-6">
            {analysis.weekly_plan ? (
              <div className="bg-white rounded-lg border p-6">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-xl font-semibold text-gray-900 flex items-center">
                    <Calendar className="w-6 h-6 mr-2 text-purple-600" />
                    Weekly Training Plan
                  </h3>
                  {analysis.weekly_plan && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleExportWeeklyPlan}
                      disabled={isExportingPlan}
                      className="flex items-center"
                    >
                      {isExportingPlan ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <Download className="w-4 h-4 mr-2" />
                      )}
                      Export Plan
                    </Button>
                  )}
                </div>
                <div className="space-y-4">
                  {formatWeeklyPlan(analysis.weekly_plan)}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Calendar className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No Training Plan</h3>
                <p className="text-gray-500">A weekly training plan is not yet available for this analysis.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisResultsDashboard;