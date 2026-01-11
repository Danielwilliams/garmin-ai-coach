'use client';

import React from 'react';
import AnalysisResultsDashboard from '@/components/Analysis/AnalysisResultsDashboard';

interface AnalysisDetailPageProps {
  params: {
    id: string;
  };
}

const AnalysisDetailPage: React.FC<AnalysisDetailPageProps> = ({ params }) => {
  return <AnalysisResultsDashboard analysisId={params.id} />;
};

export default AnalysisDetailPage;