'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import TrainingProfileWizard from '@/components/TrainingProfile/TrainingProfileWizard';
import { trainingProfileAPI } from '@/lib/api';
import Button from '@/components/ui/Button';

const EditProfilePage: React.FC = () => {
  const [initialData, setInitialData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { user } = useAuth();
  const router = useRouter();
  const params = useParams();
  const profileId = params.id as string;

  useEffect(() => {
    if (profileId) {
      fetchProfileData();
    }
  }, [profileId]);

  const fetchProfileData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const profileData = await trainingProfileAPI.getProfile(profileId);
      
      // Transform backend data to wizard format
      const wizardData = {
        athleteInfo: {
          name: profileData.name,
          // Add other athlete info fields as needed
        },
        trainingContext: {
          analysisContext: profileData.analysis_context || '',
          planningContext: profileData.planning_context || '',
          activitiesDays: profileData.activities_days || 14,
          metricsDays: profileData.metrics_days || 90,
        },
        competitions: profileData.competitions || [],
        trainingZones: profileData.training_zones || [],
        analysisSettings: {
          aiMode: profileData.ai_mode || 'coach',
          enablePlotting: profileData.enable_plotting || false,
          hitlEnabled: profileData.hitl_enabled || false,
          skipSynthesis: profileData.skip_synthesis || false,
        },
        outputSettings: {
          outputDirectory: profileData.output_directory || '',
        },
        garminSettings: {
          email: '',
          password: '',
        }
      };
      
      setInitialData(wizardData);
    } catch (err: any) {
      setError(err.detail || 'Failed to load training profile');
      console.error('Failed to fetch profile:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveProfile = async (formData: any) => {
    try {
      // TODO: Implement update API endpoint
      console.log('Saving updated profile:', formData);
      
      // For now, navigate back to profiles page
      router.push('/profile');
    } catch (error: any) {
      console.error('Failed to update profile:', error);
      throw new Error(error.detail || 'Failed to update training profile');
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !initialData) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center">
                <button
                  onClick={() => router.push('/profile')}
                  className="mr-4 text-gray-400 hover:text-gray-600"
                >
                  ←
                </button>
                <h1 className="text-2xl font-bold text-gray-900">
                  Edit Training Profile
                </h1>
              </div>
            </div>
          </div>
        </header>
        
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="text-center py-12">
              <div className="text-red-600 mb-4">{error || 'Profile not found'}</div>
              <Button variant="outline" onClick={() => router.push('/profile')}>
                Back to Profiles
              </Button>
            </div>
          </div>
        </main>
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
                onClick={() => router.push('/profile')}
                className="mr-4 text-gray-400 hover:text-gray-600"
              >
                ←
              </button>
              <h1 className="text-2xl font-bold text-gray-900">
                Edit Training Profile
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <TrainingProfileWizard
            initialData={initialData}
            onSubmit={handleSaveProfile}
            isEditMode={true}
          />
        </div>
      </main>
    </div>
  );
};

export default EditProfilePage;