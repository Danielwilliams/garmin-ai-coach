'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import GarminConnectConfig from '@/components/Settings/GarminConnectConfig';

const GarminSettingsPage: React.FC = () => {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const handleBack = () => {
    router.back();
  };

  const handleSuccess = (userInfo: any) => {
    // Navigate back to dashboard or show success message
    router.push('/dashboard');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <GarminConnectConfig
          onBack={handleBack}
          onConnectionSuccess={handleSuccess}
        />
      </div>
    </div>
  );
};

export default GarminSettingsPage;