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
      const response = await api.post('/training-profiles/from-wizard', data);
      console.log('Training profile created:', response.data);
      
      // Redirect to dashboard with success message
      router.push('/dashboard?created=true');
    } catch (error: any) {
      console.error('Error creating training profile:', error);
      
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to create training profile';
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