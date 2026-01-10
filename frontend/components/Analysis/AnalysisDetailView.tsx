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
  BarChart
} from 'lucide-react';
import { Analysis, AnalysisResult, AnalysisFile } from '@/types/analysis';
import { analysisAPI } from '@/lib/api';
import Button from '@/components/ui/Button';

interface AnalysisDetailViewProps {
  analysisId: string;
}

const AnalysisDetailView: React.FC<AnalysisDetailViewProps> = ({ analysisId }) => {
  const [analysis, setAnalysis] = useState<any | null>(null);
  const [results, setResults] = useState<any[]>([]);
  const [files, setFiles] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    fetchAnalysisData();
  }, [analysisId]);

  const fetchAnalysisData = async () => {
    try {
      setIsLoading(true);
      const [analysisData, resultsData] = await Promise.all([
        analysisAPI.getAnalysis(analysisId),
        analysisAPI.getAnalysisResults(analysisId)
      ]);
      
      setAnalysis(analysisData);
      setResults(resultsData);
      // setFiles(analysisData.files || []); // TODO: Add files endpoint
    } catch (err: any) {
      setError(err.detail || 'Failed to load analysis');
    } finally {
      setIsLoading(false);
    }
  };

  const getResultIcon = (type: string) => {
    switch (type) {
      case 'summary': return <FileText className="w-5 h-5 text-blue-600" />;
      case 'recommendation': return <Target className="w-5 h-5 text-green-600" />;
      case 'plan': return <Calendar className="w-5 h-5 text-purple-600" />;
      case 'plot': return <BarChart className="w-5 h-5 text-orange-600" />;
      default: return <FileText className="w-5 h-5 text-gray-600" />;
    }
  };

  const formatContent = (content: string) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !analysis) {
    return (
      <div className="text-center py-12">
        <div className="text-red-600 mb-4">{error || 'Analysis not found'}</div>
        <Button variant="outline" onClick={() => router.push('/dashboard')}>
          Back to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => router.back()}
            className="text-gray-400 hover:text-gray-600"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Training Analysis
            </h1>
            <p className="text-gray-600">
              {analysis.analysis_type} • {new Date(analysis.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            analysis.status === 'completed' ? 'bg-green-100 text-green-800' :
            analysis.status === 'running' ? 'bg-blue-100 text-blue-800' :
            analysis.status === 'failed' ? 'bg-red-100 text-red-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {analysis.status.charAt(0).toUpperCase() + analysis.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Analysis Metadata */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Clock className="w-5 h-5 text-gray-400 mr-2" />
            <div>
              <div className="text-sm text-gray-500">Duration</div>
              <div className="font-medium">
                {analysis.start_date && analysis.end_date ? 
                  `${Math.ceil((new Date(analysis.end_date).getTime() - new Date(analysis.start_date).getTime()) / (1000 * 60))} min` :
                  'In progress'
                }
              </div>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <Zap className="w-5 h-5 text-gray-400 mr-2" />
            <div>
              <div className="text-sm text-gray-500">Tokens Used</div>
              <div className="font-medium">{analysis.total_tokens.toLocaleString()}</div>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <DollarSign className="w-5 h-5 text-gray-400 mr-2" />
            <div>
              <div className="text-sm text-gray-500">Estimated Cost</div>
              <div className="font-medium">{analysis.estimated_cost || 'Calculating...'}</div>
            </div>
          </div>
        </div>

        <div className="bg-white p-4 rounded-lg border">
          <div className="flex items-center">
            <TrendingUp className="w-5 h-5 text-gray-400 mr-2" />
            <div>
              <div className="text-sm text-gray-500">Progress</div>
              <div className="font-medium">{analysis.progress_percentage}%</div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Summary */}
      {analysis.summary && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-blue-600" />
            Analysis Summary
          </h2>
          <div 
            className="prose max-w-none text-gray-700"
            dangerouslySetInnerHTML={{ __html: formatContent(analysis.summary) }}
          />
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Target className="w-5 h-5 mr-2 text-green-600" />
            Recommendations
          </h2>
          <div 
            className="prose max-w-none text-gray-700"
            dangerouslySetInnerHTML={{ __html: formatContent(analysis.recommendations) }}
          />
        </div>
      )}

      {/* Weekly Plan */}
      {analysis.weekly_plan && (
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
            <Calendar className="w-5 h-5 mr-2 text-purple-600" />
            Weekly Training Plan
          </h2>
          <div className="space-y-4">
            {typeof analysis.weekly_plan === 'object' ? (
              <pre className="bg-gray-50 p-4 rounded text-sm overflow-x-auto">
                {JSON.stringify(analysis.weekly_plan, null, 2)}
              </pre>
            ) : (
              <div 
                className="prose max-w-none text-gray-700"
                dangerouslySetInnerHTML={{ __html: formatContent(analysis.weekly_plan.toString()) }}
              />
            )}
          </div>
        </div>
      )}

      {/* Detailed Results */}
      {results.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Detailed Results
          </h2>
          <div className="space-y-4">
            {results.map((result) => (
              <div key={result.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-3">
                    {getResultIcon(result.result_type)}
                    <div>
                      <h3 className="font-medium text-gray-900">{result.title}</h3>
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <span>From: {result.node_name}</span>
                        <span>•</span>
                        <span>{result.tokens_used} tokens</span>
                        {result.processing_time && (
                          <>
                            <span>•</span>
                            <span>{result.processing_time}s</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {result.file_path && (
                    <Button variant="outline" size="sm">
                      <Download className="w-4 h-4 mr-1" />
                      Download
                    </Button>
                  )}
                </div>

                {result.content && (
                  <div className="mt-4 pt-4 border-t">
                    <div 
                      className="prose max-w-none text-gray-700 text-sm"
                      dangerouslySetInnerHTML={{ __html: formatContent(result.content) }}
                    />
                  </div>
                )}

                {result.data && (
                  <div className="mt-4 pt-4 border-t">
                    <details className="cursor-pointer">
                      <summary className="text-sm text-gray-600 hover:text-gray-800">
                        View structured data
                      </summary>
                      <pre className="mt-2 bg-gray-50 p-3 rounded text-xs overflow-x-auto">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </details>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisDetailView;