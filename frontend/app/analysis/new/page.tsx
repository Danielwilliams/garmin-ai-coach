'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import Button from '@/components/ui/Button';
import { ArrowLeft, Play, Settings, ChevronRight } from 'lucide-react';
import { trainingProfileAPI, analysisAPI } from '@/lib/api';

interface TrainingProfile {
  id: string;
  name: string;
  is_active: boolean;
  competitions_count: number;
  zones_count: number;
  ai_mode: string;
  created_at: string;
  updated_at: string;
}

const NewAnalysisPage: React.FC = () => {
  const [profiles, setProfiles] = useState<TrainingProfile[]>([]);
  const [selectedProfile, setSelectedProfile] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    fetchProfiles();
  }, []);

  const fetchProfiles = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await trainingProfileAPI.getProfiles();
      setProfiles(data);
      
      // Auto-select the active profile if there is one
      const activeProfile = data.find(p => p.is_active);
      if (activeProfile) {
        setSelectedProfile(activeProfile.id);
      }
    } catch (err: any) {
      setError(err.detail || 'Failed to load training profiles');
      console.error('Failed to fetch profiles:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleStartAnalysis = async () => {
    if (!selectedProfile) {
      alert('Please select a training profile first.');
      return;
    }

    try {
      setIsStarting(true);
      
      // Start AI analysis using the new integrated endpoint
      const analysisResponse = await trainingProfileAPI.startAnalysis(selectedProfile);
      
      // Navigate to the analysis progress page
      router.push(`/analysis/${analysisResponse.analysis_id}/progress`);
      
    } catch (err: any) {
      setError(err.detail || 'Failed to start analysis');
      console.error('Failed to start analysis:', err);
    } finally {
      setIsStarting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <button
                onClick={() => router.push('/analysis')}
                className="mr-4 text-gray-400 hover:text-gray-600"
              >
                <ArrowLeft className="w-6 h-6" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Start New Analysis
                </h1>
                <p className="text-gray-600">
                  Select a training profile to analyze your performance
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="text-red-600">{error}</div>
              <Button 
                variant="outline" 
                size="sm" 
                onClick={fetchProfiles}
                className="mt-2"
              >
                Retry
              </Button>
            </div>
          )}

          {profiles.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <div className="mx-auto h-24 w-24 text-gray-400 mb-4">
                <Settings className="w-full h-full" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No training profiles found
              </h3>
              <p className="text-gray-500 mb-6">
                You need to create a training profile before starting an analysis.
              </p>
              <Button onClick={() => router.push('/profile/create')}>
                Create Training Profile
              </Button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Profile Selection */}
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  Select Training Profile
                </h2>
                <p className="text-sm text-gray-600 mb-4">
                  Choose the training profile you want to analyze. The analysis will use your goals, 
                  competitions, and training zones from the selected profile.
                </p>
                
                <div className="space-y-3">
                  {profiles.map((profile) => (
                    <div
                      key={profile.id}
                      className={`relative rounded-lg border p-4 cursor-pointer hover:bg-gray-50 ${
                        selectedProfile === profile.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200'
                      }`}
                      onClick={() => setSelectedProfile(profile.id)}
                    >
                      <div className="flex items-center">
                        <input
                          type="radio"
                          name="profile"
                          value={profile.id}
                          checked={selectedProfile === profile.id}
                          onChange={() => setSelectedProfile(profile.id)}
                          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                        />
                        <div className="ml-3 flex-1">
                          <div className="flex items-center justify-between">
                            <div>
                              <h3 className="text-sm font-medium text-gray-900">
                                {profile.name}
                              </h3>
                              <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                                <span>{profile.competitions_count} competitions</span>
                                <span>{profile.zones_count} training zones</span>
                                <span className="capitalize">{profile.ai_mode} mode</span>
                                {profile.is_active && (
                                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                    Active
                                  </span>
                                )}
                              </div>
                            </div>
                            <ChevronRight className="w-5 h-5 text-gray-400" />
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Analysis Options */}
              <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium text-gray-900 mb-4">
                  Analysis Options
                </h2>
                <div className="space-y-4">
                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id="full_analysis"
                        name="analysis_type"
                        type="radio"
                        defaultChecked
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                    </div>
                    <div className="ml-3">
                      <label htmlFor="full_analysis" className="text-sm font-medium text-gray-900">
                        Full Performance Analysis
                      </label>
                      <p className="text-sm text-gray-500">
                        Comprehensive analysis of your training data, performance trends, and personalized recommendations.
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-start">
                    <div className="flex items-center h-5">
                      <input
                        id="quick_analysis"
                        name="analysis_type"
                        type="radio"
                        disabled
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                      />
                    </div>
                    <div className="ml-3">
                      <label htmlFor="quick_analysis" className="text-sm font-medium text-gray-400">
                        Quick Analysis (Coming Soon)
                      </label>
                      <p className="text-sm text-gray-400">
                        Faster analysis focusing on recent training patterns and upcoming competitions.
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Start Analysis */}
              <div className="bg-white shadow rounded-lg p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      Ready to Start
                    </h3>
                    <p className="text-sm text-gray-500">
                      {selectedProfile 
                        ? `Analysis will be performed using "${profiles.find(p => p.id === selectedProfile)?.name}" training profile.`
                        : 'Please select a training profile to continue.'
                      }
                    </p>
                  </div>
                  <Button
                    onClick={handleStartAnalysis}
                    disabled={!selectedProfile || isStarting}
                    className="flex items-center"
                  >
                    {isStarting ? (
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    ) : (
                      <Play className="w-4 h-4 mr-2" />
                    )}
                    {isStarting ? 'Starting...' : 'Start Analysis'}
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default NewAnalysisPage;