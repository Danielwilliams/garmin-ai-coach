// Training Profile Types - Matching CLI Configuration Structure

export interface AthleteInfo {
  name: string;
  email: string;
}

export interface TrainingContext {
  analysis: string;
  planning: string;
}

export interface TrainingZone {
  discipline: 'Running' | 'Cycling' | 'Swimming';
  metric: string;
  value: string;
}

export interface Competition {
  id?: string; // For UI management
  name: string;
  date: string; // YYYY-MM-DD format or free text
  race_type: string;
  priority: 'A' | 'B' | 'C';
  target_time?: string; // HH:MM:SS format
}

export interface BikeRegEvent {
  id?: string; // For UI management  
  bikereg_id: number;
  priority: 'A' | 'B' | 'C';
  target_time?: string; // HH:MM:SS format
}

export interface RunRegEvent {
  id?: string; // For UI management
  url: string;
  priority: 'A' | 'B' | 'C';
  target_time?: string; // HH:MM:SS format
}

export interface ExternalRaceIntegration {
  bikereg?: BikeRegEvent[];
  runreg?: RunRegEvent[];
}

export interface DataExtraction {
  activities_days: number;
  metrics_days: number;
  ai_mode: 'development' | 'standard' | 'cost_effective';
  enable_plotting?: boolean;
  hitl_enabled: boolean;
  skip_synthesis?: boolean;
}

export interface OutputSettings {
  directory: string;
}

export interface GarminCredentials {
  email: string;
  password: string;
  is_connected?: boolean;
  last_sync?: string;
}

export interface TrainingProfile {
  id?: string;
  name: string;
  athlete: AthleteInfo;
  context: TrainingContext;
  training_zones: TrainingZone[];
  competitions: Competition[];
  outside?: ExternalRaceIntegration;
  extraction: DataExtraction;
  output: OutputSettings;
  garmin_credentials?: GarminCredentials;
  created_at?: string;
  updated_at?: string;
  is_active?: boolean;
}

// Form-specific types for multi-step wizard
export interface TrainingProfileFormStep {
  step: number;
  title: string;
  description: string;
  isComplete: boolean;
  isValid: boolean;
}

export interface TrainingProfileFormData {
  // Step 1: Athlete Information
  athlete_name: string;
  athlete_email: string;
  
  // Step 2: Training Context
  analysis_context: string;
  planning_context: string;
  training_needs: string;
  session_constraints: string;
  training_preferences: string;
  
  // Step 3: Training Zones
  zones: TrainingZone[];
  
  // Step 4: Competitions
  competitions: Competition[];
  
  // Step 5: External Race Integration (Optional)
  bikereg_events: BikeRegEvent[];
  runreg_events: RunRegEvent[];
  
  // Step 6: Analysis Settings
  activities_days: number;
  metrics_days: number;
  ai_mode: 'development' | 'standard' | 'cost_effective';
  enable_plotting: boolean;
  hitl_enabled: boolean;
  skip_synthesis: boolean;
  
  // Step 7: Output & Garmin Settings
  output_directory: string;
  garmin_email: string;
  garmin_password: string;
}

// API response types
export interface TrainingProfileResponse extends TrainingProfile {
  user_id: string;
}

export interface TrainingAnalysisSession {
  id: string;
  profile_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress: number;
  current_node?: string;
  started_at: string;
  completed_at?: string;
  cost_usd?: number;
  total_tokens?: number;
  results?: {
    analysis_html?: string;
    planning_html?: string;
    season_plan?: string;
    weekly_plan?: string;
    plots?: string[];
  };
  error_message?: string;
}