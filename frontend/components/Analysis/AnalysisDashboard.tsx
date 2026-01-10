'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Play, FileText, Download, Eye, Clock, DollarSign, Zap } from 'lucide-react';
import { Analysis, AnalysisSummary } from '@/types/analysis';
import { analysisAPI } from '@/lib/api';
import Button from '@/components/ui/Button';

interface AnalysisDashboardProps {
  trainingProfiles?: any[];
}

const AnalysisDashboard: React.FC<AnalysisDashboardProps> = ({ trainingProfiles = [] }) => {
  const [analyses, setAnalyses] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchAnalyses();
  }, []);

  const fetchAnalyses = async () => {
    try {
      setIsLoading(true);
      const data = await analysisAPI.getAnalyses();
      setAnalyses(data);
    } catch (err: any) {
      setError(err.detail || 'Failed to load analyses');
    } finally {
      setIsLoading(false);
    }
  };

  const handleViewAnalysis = (analysisId: string) => {
    router.push(`/analysis/${analysisId}`);
  };

  const handleStartNewAnalysis = () => {
    router.push('/analysis/new');
  };

  const getStatusBadge = (status: string) => {
    const statusStyles: Record<string, string> = {
      pending: 'bg-yellow-100 text-yellow-800',
      running: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      cancelled: 'bg-gray-100 text-gray-800'
    };

    const statusIcons: Record<string, any> = {
      pending: <Clock className="w-3 h-3" />,
      running: <Zap className="w-3 h-3" />,
      completed: '✓',
      failed: '✗',
      cancelled: '○'
    };

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${statusStyles[status] || 'bg-gray-100 text-gray-800'}`}>
        <span className="mr-1">{statusIcons[status] || '•'}</span>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">{error}</div>
        <Button variant="outline" onClick={fetchAnalyses}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Training Analysis</h2>
          <p className="text-gray-600">AI-powered insights from your training data</p>
        </div>
        <Button onClick={handleStartNewAnalysis} className="flex items-center">
          <Play className="w-4 h-4 mr-2" />
          Start New Analysis
        </Button>
      </div>

      {/* Recent Analyses */}
      {analyses.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
            <svg fill="none" stroke="currentColor" viewBox="0 0 48 48" className="w-full h-full">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 14v20c0 4.418 7.163 8 16 8 1.381 0 2.721-.087 4-.252M8 14c0 4.418 7.163 8 16 8s16-3.582 16-8M8 14c0-4.418 7.163-8 16-8s16 3.582 16 8m0 0v14m-16-4c0 4.418 7.163 8 16 8 1.381 0 2.721-.087 4-.252" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No analyses yet</h3>
          <p className="text-gray-500 mb-6">
            Start your first AI analysis to get insights from your training data.
          </p>
          <Button onClick={handleStartNewAnalysis} className="flex items-center mx-auto">
            <Play className="w-4 h-4 mr-2" />
            Start Your First Analysis
          </Button>
        </div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <ul className="divide-y divide-gray-200">
            {analyses.map((analysis) => (
              <li key={analysis.id} className="px-6 py-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2">
                      <h3 className="text-lg font-medium text-gray-900">
                        {analysis.training_config_name}
                      </h3>
                      {getStatusBadge(analysis.status)}
                    </div>
                    
                    <div className="flex items-center space-x-6 text-sm text-gray-500">
                      <div className="flex items-center">
                        <FileText className="w-4 h-4 mr-1" />
                        {analysis.analysis_type}
                      </div>
                      
                      {analysis.status === 'running' && (
                        <div className="flex items-center">
                          <div className="w-4 h-4 mr-1">
                            <div className="w-full bg-gray-200 rounded-full h-1.5">
                              <div 
                                className="bg-blue-600 h-1.5 rounded-full transition-all duration-300" 
                                style={{ width: `${analysis.progress_percentage}%` }}
                              ></div>
                            </div>
                          </div>
                          {analysis.progress_percentage}%
                        </div>
                      )}

                      {analysis.estimated_cost && (
                        <div className="flex items-center">
                          <DollarSign className="w-4 h-4 mr-1" />
                          {analysis.estimated_cost}
                        </div>
                      )}

                      <div className="flex items-center">
                        <Zap className="w-4 h-4 mr-1" />
                        {analysis.total_tokens.toLocaleString()} tokens
                      </div>

                      <span>
                        {new Date(analysis.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    {analysis.status === 'completed' && (
                      <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
                        {analysis.has_summary && (
                          <span className="flex items-center">
                            <span className="w-2 h-2 bg-green-400 rounded-full mr-1"></span>
                            Summary
                          </span>
                        )}
                        {analysis.has_recommendations && (
                          <span className="flex items-center">
                            <span className="w-2 h-2 bg-blue-400 rounded-full mr-1"></span>
                            Recommendations
                          </span>
                        )}
                        {analysis.has_weekly_plan && (
                          <span className="flex items-center">
                            <span className="w-2 h-2 bg-purple-400 rounded-full mr-1"></span>
                            Weekly Plan
                          </span>
                        )}
                        {analysis.files_count > 0 && (
                          <span className="flex items-center">
                            <Download className="w-3 h-3 mr-1" />
                            {analysis.files_count} files
                          </span>
                        )}
                      </div>
                    )}
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewAnalysis(analysis.id)}
                      className="flex items-center"
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      View
                    </Button>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default AnalysisDashboard;