'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import TrainingProfileWizard from '@/components/TrainingProfile/TrainingProfileWizard';
import { CompleteTrainingProfileFormData } from '@/lib/validations/training';
import api from '@/lib/api';

const CreateProfilePage: React.FC = () => {
  const router = useRouter();

  const handleSubmit = async (data: CompleteTrainingProfileFormData) => {
    try {
      // Debug: Check if we have authentication
      const token = document.cookie.split(';')
        .find(row => row.trim().startsWith('access_token='))
        ?.split('=')[1];
      
      if (!token) {
        throw new Error('No authentication token found. Please log in again.');
      }

      console.log('Submitting training profile data:', data);
      console.log('Using token:', token ? 'Token present' : 'No token');
      
      const response = await api.post('/training-profiles/from-wizard', data);
      console.log('Training profile created:', response.data);
      
      // Redirect to dashboard with success message
      router.push('/dashboard?created=true');
    } catch (error: any) {
      console.error('Full error object:', error);
      console.error('Error response:', error.response);
      
      let errorMessage = 'Failed to create training profile';
      
      if (error.response?.status === 401) {
        errorMessage = 'Authentication expired. Please log in again.';
        // Redirect to login
        router.push('/auth/login');
        return;
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      alert(`Error creating profile: ${errorMessage}`);
    }
  };

  const handleCancel = () => {
    router.push('/dashboard');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <TrainingProfileWizard
        onSubmit={handleSubmit}
        onCancel={handleCancel}
      />
    </div>
  );
};

export default CreateProfilePage;