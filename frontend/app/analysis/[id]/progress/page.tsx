'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import AnalysisProgressTracker from '@/components/Analysis/AnalysisProgressTracker';

interface AnalysisProgressPageProps {
  params: {
    id: string;
  };
}

const AnalysisProgressPage: React.FC<AnalysisProgressPageProps> = ({ params }) => {
  const router = useRouter();

  const handleAnalysisComplete = (analysis: any) => {
    // Navigate to results when analysis is complete
    setTimeout(() => {
      router.push(`/analysis/${params.id}`);
    }, 2000); // Wait 2 seconds to show completion state
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <AnalysisProgressTracker 
        analysisId={params.id} 
        onComplete={handleAnalysisComplete}
      />
    </div>
  );
};

export default AnalysisProgressPage;