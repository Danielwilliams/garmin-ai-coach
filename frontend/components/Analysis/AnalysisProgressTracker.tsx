'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  CheckCircle,
  Clock,
  Loader2,
  AlertCircle,
  Activity,
  Brain,
  BarChart,
  Heart,
  Target,
  FileText,
  Calendar,
  TrendingUp,
  Award,
  Zap,
  Timer
} from 'lucide-react';
import { analysisAPI } from '@/lib/api';
import Button from '@/components/ui/Button';

interface AnalysisProgressTrackerProps {
  analysisId: string;
  onComplete?: (analysis: any) => void;
}

interface ProgressStep {
  id: string;
  name: string;
  description: string;
  icon: React.ElementType;
  status: 'pending' | 'running' | 'completed' | 'error';
  estimatedTime?: string;
  actualTime?: string;
  tokensUsed?: number;
}

const AnalysisProgressTracker: React.FC<AnalysisProgressTrackerProps> = ({ 
  analysisId, 
  onComplete 
}) => {
  const [analysis, setAnalysis] = useState<any>(null);
  const [progressSteps, setProgressSteps] = useState<ProgressStep[]>([]);
  const [currentStep, setCurrentStep] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const [startTime] = useState<Date>(new Date());
  const router = useRouter();

  // Initialize progress steps
  const initializeSteps = (): ProgressStep[] => [
    {
      id: 'data_extraction',
      name: 'Data Extraction',
      description: 'Connecting to Garmin and extracting training data',
      icon: Activity,
      status: 'pending',
      estimatedTime: '30s'
    },
    {
      id: 'metrics_summarizer',
      name: 'Metrics Analysis',
      description: 'Analyzing training load, VO₂ max, and performance metrics',
      icon: BarChart,
      status: 'pending',
      estimatedTime: '45s'
    },
    {
      id: 'physiology_summarizer',
      name: 'Physiology Analysis',
      description: 'Evaluating recovery patterns and physiological markers',
      icon: Heart,
      status: 'pending',
      estimatedTime: '45s'
    },
    {
      id: 'activity_summarizer',
      name: 'Activity Analysis',
      description: 'Processing workout execution and activity patterns',
      icon: Activity,
      status: 'pending',
      estimatedTime: '45s'
    },
    {
      id: 'metrics_expert',
      name: 'Expert Metrics Review',
      description: 'Advanced sports science analysis and TSB optimization',
      icon: TrendingUp,
      status: 'pending',
      estimatedTime: '60s'
    },
    {
      id: 'physiology_expert',
      name: 'Expert Physiology Review',
      description: 'Exercise physiology expertise and recovery protocols',
      icon: Brain,
      status: 'pending',
      estimatedTime: '60s'
    },
    {
      id: 'activity_expert',
      name: 'Expert Activity Review',
      description: 'Biomechanics and technique optimization insights',
      icon: Award,
      status: 'pending',
      estimatedTime: '60s'
    },
    {
      id: 'synthesis',
      name: 'Strategy Synthesis',
      description: 'Integrating all analyses into unified coaching strategy',
      icon: Brain,
      status: 'pending',
      estimatedTime: '90s'
    },
    {
      id: 'formatting',
      name: 'Report Generation',
      description: 'Creating professional analysis report',
      icon: FileText,
      status: 'pending',
      estimatedTime: '30s'
    },
    {
      id: 'planning',
      name: 'Training Plan',
      description: 'Generating detailed weekly training plan',
      icon: Calendar,
      status: 'pending',
      estimatedTime: '60s'
    }
  ];

  useEffect(() => {
    setProgressSteps(initializeSteps());
    startPolling();

    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [analysisId]);

  const startPolling = () => {
    const interval = setInterval(async () => {
      await updateProgress();
    }, 3000); // Poll every 3 seconds

    setPollingInterval(interval);
  };

  const updateProgress = async () => {
    try {
      const analysisData = await analysisAPI.getAnalysis(analysisId);
      setAnalysis(analysisData);

      // Map current node to progress steps
      const currentNode = analysisData.current_node;
      if (currentNode) {
        setCurrentStep(currentNode);
        updateStepsStatus(currentNode, analysisData);
      }

      // Check if completed
      if (analysisData.status === 'completed') {
        if (pollingInterval) {
          clearInterval(pollingInterval);
        }
        setProgressSteps(prev => prev.map(step => ({
          ...step,
          status: 'completed'
        })));
        
        if (onComplete) {
          onComplete(analysisData);
        }
      } else if (analysisData.status === 'failed') {
        if (pollingInterval) {
          clearInterval(pollingInterval);
        }
        setError(analysisData.error_message || 'Analysis failed');
      }
    } catch (err: any) {
      console.error('Failed to update progress:', err);
    }
  };

  const updateStepsStatus = (currentNode: string, analysisData: any) => {
    setProgressSteps(prev => {
      const newSteps = [...prev];
      
      // Get completed results from API
      const completedNodes = new Set(analysisData.results?.map((r: any) => r.node_name) || []);
      
      return newSteps.map(step => {
        if (completedNodes.has(step.id)) {
          // Find matching result for token count
          const result = analysisData.results?.find((r: any) => r.node_name === step.id);
          return {
            ...step,
            status: 'completed' as const,
            tokensUsed: result?.tokens_used,
            actualTime: result?.processing_time ? `${result.processing_time}s` : undefined
          };
        } else if (step.id === currentNode) {
          return { ...step, status: 'running' as const };
        } else if (newSteps.findIndex(s => s.id === step.id) < newSteps.findIndex(s => s.id === currentNode)) {
          return { ...step, status: 'completed' as const };
        } else {
          return { ...step, status: 'pending' as const };
        }
      });
    });
  };

  const getStepIcon = (step: ProgressStep) => {
    const Icon = step.icon;
    
    switch (step.status) {
      case 'completed':
        return <CheckCircle className="w-6 h-6 text-green-500" />;
      case 'running':
        return <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />;
      case 'error':
        return <AlertCircle className="w-6 h-6 text-red-500" />;
      default:
        return <Icon className="w-6 h-6 text-gray-400" />;
    }
  };

  const getStepBorderColor = (step: ProgressStep) => {
    switch (step.status) {
      case 'completed':
        return 'border-green-200 bg-green-50';
      case 'running':
        return 'border-blue-200 bg-blue-50';
      case 'error':
        return 'border-red-200 bg-red-50';
      default:
        return 'border-gray-200';
    }
  };

  const getElapsedTime = () => {
    const elapsed = Math.floor((new Date().getTime() - startTime.getTime()) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const getEstimatedTotal = () => {
    return progressSteps.reduce((total, step) => {
      const time = parseInt(step.estimatedTime?.replace('s', '') || '0');
      return total + time;
    }, 0);
  };

  const completedSteps = progressSteps.filter(step => step.status === 'completed').length;
  const progressPercentage = Math.round((completedSteps / progressSteps.length) * 100);

  if (error) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center py-12">
          <AlertCircle className="w-16 h-16 mx-auto text-red-500 mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Failed</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="space-x-3">
            <Button variant="outline" onClick={() => router.push('/analysis')}>
              Back to Analysis
            </Button>
            <Button onClick={() => window.location.reload()}>
              Retry Analysis
            </Button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">AI Analysis in Progress</h1>
        <p className="text-gray-600 mb-4">
          Our AI coaches are analyzing your training data and generating personalized insights
        </p>
        
        {/* Progress Bar */}
        <div className="max-w-md mx-auto">
          <div className="flex justify-between text-sm text-gray-500 mb-2">
            <span>{completedSteps} of {progressSteps.length} steps completed</span>
            <span>{progressPercentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all duration-500 ease-out"
              style={{ width: `${progressPercentage}%` }}
            />
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg p-6 border">
          <div className="flex items-center">
            <Timer className="w-8 h-8 text-blue-600" />
            <div className="ml-4">
              <p className="text-sm text-gray-500">Elapsed Time</p>
              <p className="text-2xl font-semibold text-gray-900">{getElapsedTime()}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border">
          <div className="flex items-center">
            <Clock className="w-8 h-8 text-orange-600" />
            <div className="ml-4">
              <p className="text-sm text-gray-500">Estimated Total</p>
              <p className="text-2xl font-semibold text-gray-900">{Math.ceil(getEstimatedTotal() / 60)}min</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg p-6 border">
          <div className="flex items-center">
            <Zap className="w-8 h-8 text-yellow-600" />
            <div className="ml-4">
              <p className="text-sm text-gray-500">Tokens Used</p>
              <p className="text-2xl font-semibold text-gray-900">
                {analysis?.total_tokens?.toLocaleString() || '0'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Progress Steps */}
      <div className="space-y-4">
        {progressSteps.map((step, index) => (
          <div 
            key={step.id} 
            className={`bg-white rounded-lg p-6 border transition-all duration-300 ${getStepBorderColor(step)}`}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                {getStepIcon(step)}
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <h3 className="text-lg font-medium text-gray-900">{step.name}</h3>
                    {step.status === 'running' && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Processing...
                      </span>
                    )}
                  </div>
                  <p className="text-gray-600">{step.description}</p>
                </div>
              </div>
              
              <div className="text-right text-sm text-gray-500">
                {step.actualTime && (
                  <div className="font-medium text-gray-900">{step.actualTime}</div>
                )}
                {step.estimatedTime && !step.actualTime && (
                  <div>Est. {step.estimatedTime}</div>
                )}
                {step.tokensUsed && (
                  <div className="flex items-center justify-end mt-1">
                    <Zap className="w-3 h-3 mr-1" />
                    {step.tokensUsed.toLocaleString()} tokens
                  </div>
                )}
              </div>
            </div>
            
            {step.status === 'running' && (
              <div className="mt-4 pt-4 border-t">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }} />
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="mt-8 text-center">
        <p className="text-sm text-gray-500">
          Your analysis will automatically advance when complete, or you can{' '}
          <button 
            onClick={() => router.push('/analysis')}
            className="text-blue-600 hover:text-blue-800 underline"
          >
            return to the analysis dashboard
          </button>
          .
        </p>
      </div>
    </div>
  );
};

export default AnalysisProgressTracker;