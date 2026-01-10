// Analysis Types - Matching backend database schema

export interface Analysis {
  id: string;
  user_id: string;
  training_config_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  analysis_type: string;
  workflow_id?: string;
  current_node?: string;
  progress_percentage: number;
  summary?: string;
  recommendations?: string;
  weekly_plan?: any; // JSON object
  start_date?: string;
  end_date?: string;
  data_summary?: any; // JSON object
  total_tokens: number;
  estimated_cost?: string;
  error_message?: string;
  retry_count: number;
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult {
  id: string;
  analysis_id: string;
  node_name: string;
  result_type: 'summary' | 'plan' | 'plot' | 'recommendation' | 'data';
  title: string;
  content?: string;
  data?: any; // JSON object
  file_path?: string;
  tokens_used: number;
  processing_time?: number;
  created_at: string;
  updated_at: string;
}

export interface AnalysisFile {
  id: string;
  analysis_id: string;
  filename: string;
  file_type: 'plot' | 'report' | 'data' | 'export';
  mime_type: string;
  file_size: number;
  file_path: string;
  is_public: boolean;
  download_count: number;
  created_at: string;
  updated_at: string;
}

export interface AnalysisWithResults extends Analysis {
  results: AnalysisResult[];
  files: AnalysisFile[];
  training_config_name: string;
}

export interface AnalysisSummary {
  id: string;
  status: Analysis['status'];
  analysis_type: string;
  progress_percentage: number;
  training_config_name: string;
  total_tokens: number;
  estimated_cost?: string;
  created_at: string;
  has_summary: boolean;
  has_recommendations: boolean;
  has_weekly_plan: boolean;
  files_count: number;
}

export interface CreateAnalysisRequest {
  training_config_id: string;
  analysis_type?: string;
}