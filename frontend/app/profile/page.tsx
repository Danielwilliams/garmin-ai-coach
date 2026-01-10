'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import Button from '@/components/ui/Button';
import { Plus, Settings, Play, Trash2 } from 'lucide-react';
import { trainingProfileAPI } from '@/lib/api';

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

const ProfilesPage: React.FC = () => {
  const [profiles, setProfiles] = useState<TrainingProfile[]>([]);
  const [isLoading, setIsLoading] = useState(true);
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
    } catch (err: any) {
      setError(err.detail || 'Failed to load training profiles');
      console.error('Failed to fetch profiles:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateProfile = () => {
    router.push('/profile/create');
  };

  const handleEditProfile = (profileId: string) => {
    router.push(`/profile/edit/${profileId}`);
  };

  const handleActivateProfile = async (profileId: string) => {
    try {
      // TODO: Implement activate API endpoint
      console.log('Activating profile:', profileId);
      // For now, just refresh the profiles list
      await fetchProfiles();
    } catch (err: any) {
      setError(err.detail || 'Failed to activate profile');
    }
  };

  const handleDeleteProfile = async (profileId: string) => {
    if (!confirm('Are you sure you want to delete this training profile? This action cannot be undone.')) {
      return;
    }
    
    try {
      // TODO: Implement delete API endpoint
      console.log('Deleting profile:', profileId);
      // For now, remove from local state
      setProfiles(profiles.filter(p => p.id !== profileId));
    } catch (err: any) {
      setError(err.detail || 'Failed to delete profile');
      // Refresh profiles on error to ensure state consistency
      await fetchProfiles();
    }
  };

  const handleStartAnalysis = (profileId: string) => {
    router.push(`/analysis?profile=${profileId}`);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <header className="bg-white shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center py-6">
              <div className="flex items-center">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="mr-4 text-gray-400 hover:text-gray-600"
                >
                  ←
                </button>
                <h1 className="text-2xl font-bold text-gray-900">
                  Training Profiles
                </h1>
              </div>
            </div>
          </div>
        </header>
        
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            <div className="text-center py-12">
              <div className="text-red-600 mb-4">{error}</div>
              <Button variant="outline" onClick={fetchProfiles}>
                Retry
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
                onClick={() => router.push('/dashboard')}
                className="mr-4 text-gray-400 hover:text-gray-600"
              >
                ←
              </button>
              <h1 className="text-2xl font-bold text-gray-900">
                Training Profiles
              </h1>
            </div>
            <Button onClick={handleCreateProfile} className="flex items-center">
              <Plus className="w-4 h-4 mr-2" />
              Create Profile
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          {profiles.length === 0 ? (
            /* Empty State */
            <div className="text-center py-12">
              <div className="mx-auto h-24 w-24 text-gray-400">
                <svg fill="none" stroke="currentColor" viewBox="0 0 48 48" className="w-full h-full">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M34 40h10v-4a6 6 0 00-10.712-3.714M34 40H14m20 0v-4a9.971 9.971 0 00-.712-3.714M14 40H4v-4a6 6 0 0110.712-3.714M14 40v-4a9.971 9.971 0 01.712-3.714m0 0A9.971 9.971 0 0118 32a9.971 9.971 0 013.288.713M30 20a6 6 0 11-12 0 6 6 0 0112 0zm8 12a4 4 0 11-8 0 4 4 0 018 0zm-8 0a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <h2 className="mt-6 text-xl font-medium text-gray-900">
                No training profiles yet
              </h2>
              <p className="mt-2 text-gray-500">
                Get started by creating your first training profile with your goals, competitions, and training zones.
              </p>
              <div className="mt-6">
                <Button onClick={handleCreateProfile} className="flex items-center mx-auto">
                  <Plus className="w-4 h-4 mr-2" />
                  Create Your First Profile
                </Button>
              </div>
            </div>
          ) : (
            /* Profiles List */
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {profiles.map((profile) => (
                  <li key={profile.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-3">
                          <h3 className="text-lg font-medium text-gray-900 truncate">
                            {profile.name}
                          </h3>
                          {profile.is_active && (
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Active
                            </span>
                          )}
                        </div>
                        <div className="mt-1 flex items-center text-sm text-gray-500 space-x-4">
                          <span>{profile.competitions_count} competitions</span>
                          <span>{profile.zones_count} training zones</span>
                          <span className="capitalize">{profile.ai_mode} mode</span>
                          <span>Created {new Date(profile.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleStartAnalysis(profile.id)}
                          className="flex items-center"
                        >
                          <Play className="w-4 h-4 mr-1" />
                          Analyze
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEditProfile(profile.id)}
                          className="flex items-center"
                        >
                          <Settings className="w-4 h-4 mr-1" />
                          Edit
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteProfile(profile.id)}
                          className="flex items-center text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </main>
    </div>
  );
};

export default ProfilesPage;