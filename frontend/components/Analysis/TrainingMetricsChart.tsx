'use client';

import React from 'react';
import { 
  BarChart, 
  TrendingUp, 
  Activity, 
  Heart,
  Clock,
  Target
} from 'lucide-react';

interface MetricData {
  label: string;
  value: string | number;
  change?: string;
  trend?: 'up' | 'down' | 'stable';
}

interface TrainingMetricsChartProps {
  data?: any; // Training metrics data from analysis
  className?: string;
}

const TrainingMetricsChart: React.FC<TrainingMetricsChartProps> = ({ 
  data, 
  className = '' 
}) => {
  // Mock data for demonstration - in real app, this would come from analysis data
  const mockMetrics: MetricData[] = [
    { label: 'Weekly Volume', value: '12.5 hrs', change: '+2.3 hrs', trend: 'up' },
    { label: 'Training Load', value: '485', change: '+45', trend: 'up' },
    { label: 'Recovery Score', value: '72%', change: '-5%', trend: 'down' },
    { label: 'VO₂ Max', value: '58.4', change: '+1.2', trend: 'up' },
    { label: 'Resting HR', value: '48 bpm', change: '-2 bpm', trend: 'down' },
    { label: 'Sleep Quality', value: '78%', change: '+8%', trend: 'up' }
  ];

  const metrics = data?.metrics || mockMetrics;

  const getTrendIcon = (trend?: string) => {
    switch (trend) {
      case 'up':
        return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'down':
        return <TrendingUp className="w-4 h-4 text-red-500 rotate-180" />;
      default:
        return <Target className="w-4 h-4 text-gray-400" />;
    }
  };

  const getTrendColor = (trend?: string) => {
    switch (trend) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getMetricIcon = (label: string) => {
    if (label.toLowerCase().includes('volume') || label.toLowerCase().includes('load')) {
      return <BarChart className="w-5 h-5 text-blue-600" />;
    }
    if (label.toLowerCase().includes('recovery') || label.toLowerCase().includes('sleep')) {
      return <Heart className="w-5 h-5 text-red-600" />;
    }
    if (label.toLowerCase().includes('vo2') || label.toLowerCase().includes('hr')) {
      return <Activity className="w-5 h-5 text-green-600" />;
    }
    return <Clock className="w-5 h-5 text-gray-600" />;
  };

  return (
    <div className={`bg-white rounded-lg border p-6 ${className}`}>
      <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <BarChart className="w-5 h-5 mr-2 text-blue-600" />
        Key Training Metrics
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map((metric: MetricData, index: number) => (
          <div key={index} className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center">
                {getMetricIcon(metric.label)}
                <span className="text-sm font-medium text-gray-700 ml-2">
                  {metric.label}
                </span>
              </div>
              {metric.trend && getTrendIcon(metric.trend)}
            </div>
            
            <div className="flex items-end justify-between">
              <div className="text-2xl font-bold text-gray-900">
                {metric.value}
              </div>
              
              {metric.change && (
                <div className={`text-sm font-medium flex items-center ${getTrendColor(metric.trend)}`}>
                  {metric.change}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Simple weekly trend visualization */}
      <div className="mt-6 pt-6 border-t">
        <h4 className="text-md font-medium text-gray-900 mb-3">Weekly Training Load Trend</h4>
        <div className="flex items-end space-x-2 h-24">
          {[65, 72, 68, 85, 79, 92, 88].map((value, index) => (
            <div key={index} className="flex-1 flex flex-col items-center">
              <div 
                className="w-full bg-blue-500 rounded-t"
                style={{ height: `${(value / 100) * 100}%` }}
              />
              <span className="text-xs text-gray-500 mt-1">
                {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][index]}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TrainingMetricsChart;