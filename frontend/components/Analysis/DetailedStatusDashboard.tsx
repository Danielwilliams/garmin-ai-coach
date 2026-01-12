'use client';

import React, { useState, useEffect } from 'react';
import { 
  Activity, 
  Clock, 
  AlertCircle, 
  CheckCircle, 
  XCircle, 
  Loader,
  RefreshCw,
  Database,
  Brain,
  Server,
  Zap
} from 'lucide-react';
import api from '@/lib/api';

interface ComponentHealth {
  status: 'pending' | 'initializing' | 'running' | 'success' | 'warning' | 'error' | 'timeout' | 'cancelled';
  success_rate: number;
  average_duration_ms: number;
  total_events: number;
  last_updated: string;
  last_error?: string;
}

interface StatusData {
  basic_status: {
    analysis_id: string;
    status: string;
    progress_percentage: number;
    current_node: string;
    start_date: string;
    end_date?: string;
    estimated_cost: string;
    total_tokens: number;
    error_message?: string;
  };
  detailed_status: {
    overall_progress: number;
    component_health: Record<string, ComponentHealth>;
    workflow_progress: Record<string, number>;
    recent_errors: Array<{
      timestamp: string;
      component: string;
      message: string;
      error_details?: string;
    }>;
  };
  has_detailed_tracking: boolean;
}

interface TimelineEvent {
  event_id: string;
  timestamp: string;
  component_type: string;
  component_name: string;
  status: string;
  message: string;
  details?: Record<string, any>;
  duration_ms?: number;
  error_details?: string;
}

interface DetailedStatusDashboardProps {
  analysisId: string;
  onClose?: () => void;
}

const DetailedStatusDashboard: React.FC<DetailedStatusDashboardProps> = ({
  analysisId,
  onClose
}) => {
  const [statusData, setStatusData] = useState<StatusData | null>(null);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [activeTab, setActiveTab] = useState<'overview' | 'timeline' | 'components'>('overview');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStatus = async () => {
    try {
      const [statusRes, timelineRes] = await Promise.all([
        api.get(`/analyses/${analysisId}/status`),
        api.get(`/analyses/${analysisId}/status/timeline`)
      ]);
      
      setStatusData(statusRes.data);
      setTimeline(timelineRes.data.timeline || []);
    } catch (error) {
      console.error('Failed to fetch status:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchStatus();
  };

  useEffect(() => {
    fetchStatus();
    
    // Auto-refresh every 5 seconds for running analyses
    const interval = setInterval(() => {
      if (statusData?.basic_status?.status === 'running') {
        fetchStatus();
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [analysisId, statusData?.basic_status?.status]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'running':
      case 'initializing':
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getComponentIcon = (componentType: string) => {
    switch (componentType) {
      case 'database_operation':
        return <Database className="w-4 h-4" />;
      case 'ai_agent':
        return <Brain className="w-4 h-4" />;
      case 'api_connection':
        return <Server className="w-4 h-4" />;
      case 'data_extraction':
        return <Zap className="w-4 h-4" />;
      default:
        return <Activity className="w-4 h-4" />;
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center">
          <Loader className="w-8 h-8 animate-spin" />
          <span className="ml-2">Loading detailed status...</span>
        </div>
      </div>
    );
  }

  if (!statusData) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="text-center text-red-600">
          Failed to load status data
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {getStatusIcon(statusData.basic_status.status)}
            <div>
              <h3 className="text-lg font-semibold">Analysis Status Dashboard</h3>
              <p className="text-sm text-gray-600">
                Analysis ID: {statusData.basic_status.analysis_id.slice(0, 8)}...
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="text-gray-500 hover:text-gray-700"
              >
                ×
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8 px-6">
          {['overview', 'timeline', 'components'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`py-4 text-sm font-medium capitalize border-b-2 ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab}
            </button>
          ))}
        </nav>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Basic Status */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Status</div>
                <div className="text-lg font-semibold capitalize">
                  {statusData.basic_status.status}
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Progress</div>
                <div className="text-lg font-semibold">
                  {statusData.basic_status.progress_percentage}%
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Current Node</div>
                <div className="text-sm font-medium">
                  {statusData.basic_status.current_node || 'Not specified'}
                </div>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="text-sm text-gray-600">Estimated Cost</div>
                <div className="text-lg font-semibold">
                  {statusData.basic_status.estimated_cost}
                </div>
              </div>
            </div>

            {/* Workflow Progress */}
            {statusData.has_detailed_tracking && statusData.detailed_status?.workflow_progress && (
              <div>
                <h4 className="text-lg font-semibold mb-4">Workflow Progress</h4>
                <div className="space-y-3">
                  {Object.entries(statusData.detailed_status.workflow_progress).map(([agent, progress]) => (
                    <div key={agent} className="flex items-center space-x-3">
                      <div className="w-32 text-sm font-medium capitalize">
                        {agent.replace('_', ' ')}
                      </div>
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                          style={{ width: `${progress}%` }}
                        />
                      </div>
                      <div className="text-sm text-gray-600 w-12">
                        {Math.round(progress)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Recent Errors */}
            {statusData.detailed_status?.recent_errors?.length > 0 && (
              <div>
                <h4 className="text-lg font-semibold mb-4">Recent Errors</h4>
                <div className="space-y-2">
                  {statusData.detailed_status.recent_errors.map((error, index) => (
                    <div key={index} className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div className="flex items-start space-x-2">
                        <XCircle className="w-4 h-4 text-red-500 mt-0.5" />
                        <div className="flex-1">
                          <div className="text-sm font-medium">{error.component}</div>
                          <div className="text-sm text-gray-600">{error.message}</div>
                          <div className="text-xs text-gray-500">
                            {new Date(error.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'timeline' && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Event Timeline</h4>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {timeline.map((event) => (
                <div key={event.event_id} className="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg">
                  <div className="flex-shrink-0 mt-1">
                    {getStatusIcon(event.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2">
                      {getComponentIcon(event.component_type)}
                      <span className="text-sm font-medium">{event.component_name}</span>
                      <span className="text-xs text-gray-500">
                        {new Date(event.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 mt-1">{event.message}</div>
                    {event.duration_ms && (
                      <div className="text-xs text-gray-500 mt-1">
                        Duration: {event.duration_ms}ms
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'components' && statusData.has_detailed_tracking && (
          <div>
            <h4 className="text-lg font-semibold mb-4">Component Health</h4>
            <div className="grid gap-4">
              {Object.entries(statusData.detailed_status.component_health).map(([name, health]) => (
                <div key={name} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      {getStatusIcon(health.status)}
                      <span className="font-medium">{name}</span>
                    </div>
                    <span className="text-sm text-gray-500">
                      Success Rate: {Math.round(health.success_rate)}%
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-600">Events:</span>
                      <span className="ml-1 font-medium">{health.total_events}</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Avg Duration:</span>
                      <span className="ml-1 font-medium">{Math.round(health.average_duration_ms)}ms</span>
                    </div>
                    <div>
                      <span className="text-gray-600">Last Update:</span>
                      <span className="ml-1 font-medium">
                        {new Date(health.last_updated).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                  {health.last_error && (
                    <div className="mt-2 p-2 bg-red-50 rounded text-sm text-red-600">
                      Last Error: {health.last_error}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DetailedStatusDashboard;