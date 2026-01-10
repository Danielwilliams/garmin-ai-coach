'use client';

import React from 'react';
import AnalysisDetailView from '@/components/Analysis/AnalysisDetailView';

interface AnalysisDetailPageProps {
  params: {
    id: string;
  };
}

const AnalysisDetailPage: React.FC<AnalysisDetailPageProps> = ({ params }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      <AnalysisDetailView analysisId={params.id} />
    </div>
  );
};

export default AnalysisDetailPage;