'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import TrainingProfileWizard from '@/components/TrainingProfile/TrainingProfileWizard';
import { CompleteTrainingProfileFormData } from '@/lib/validations/training';

const CreateProfilePage: React.FC = () => {
  const router = useRouter();

  const handleSubmit = async (data: CompleteTrainingProfileFormData) => {
    try {
      // TODO: Call the backend API to create the training profile
      console.log('Training profile data:', data);
      
      // Simulate API call for now
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Redirect to dashboard or profile list on success
      router.push('/dashboard?created=true');
    } catch (error) {
      console.error('Error creating training profile:', error);
      // Handle error (show toast, etc.)
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