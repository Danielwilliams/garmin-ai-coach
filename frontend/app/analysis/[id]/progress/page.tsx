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
    // Don't auto-navigate - let user control when to view results
    // User can click "View Results" button when ready
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <button 
              onClick={() => router.push('/analysis')}
              className="flex items-center text-gray-600 hover:text-gray-900 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Analysis Dashboard
            </button>
            <h1 className="text-lg font-semibold text-gray-900">Analysis Progress</h1>
          </div>
        </div>
      </div>
      
      <AnalysisProgressTracker 
        analysisId={params.id} 
        onComplete={handleAnalysisComplete}
      />
    </div>
  );
};

export default AnalysisProgressPage;