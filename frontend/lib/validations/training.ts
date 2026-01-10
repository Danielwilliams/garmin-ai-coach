import { z } from 'zod';

// Helper schemas
const timeRegex = /^([0-1]?\d|2[0-3]):([0-5]\d):([0-5]\d)$/;

export const trainingZoneSchema = z.object({
  discipline: z.enum(['Running', 'Cycling', 'Swimming']),
  metric: z.string().min(1, 'Metric description is required'),
  value: z.string().min(1, 'Zone value is required'),
});

export const competitionSchema = z.object({
  name: z.string().min(1, 'Competition name is required').max(100),
  date: z.string().min(1, 'Date is required'),
  race_type: z.string().min(1, 'Race type is required').max(50),
  priority: z.enum(['A', 'B', 'C']),
  target_time: z.string().regex(timeRegex, 'Time must be in HH:MM:SS format').optional().or(z.literal('')),
});

export const bikeregEventSchema = z.object({
  bikereg_id: z.number().int().positive('BikeReg ID must be a positive integer'),
  priority: z.enum(['A', 'B', 'C']),
  target_time: z.string().regex(timeRegex, 'Time must be in HH:MM:SS format').optional().or(z.literal('')),
});

export const runregEventSchema = z.object({
  url: z.string().url('Must be a valid URL'),
  priority: z.enum(['A', 'B', 'C']),
  target_time: z.string().regex(timeRegex, 'Time must be in HH:MM:SS format').optional().or(z.literal('')),
});

// Step 1: Athlete Information
export const athleteInfoSchema = z.object({
  athlete_name: z.string().min(2, 'Name must be at least 2 characters').max(100),
  athlete_email: z.string().email('Valid email address required'),
});

// Step 2: Training Context
export const trainingContextSchema = z.object({
  analysis_context: z.string().min(10, 'Please provide at least 10 characters of analysis context'),
  planning_context: z.string().min(10, 'Please provide at least 10 characters of planning context'),
  training_needs: z.string().optional(),
  session_constraints: z.string().optional(),
  training_preferences: z.string().optional(),
});

// Step 3: Training Zones
export const trainingZonesSchema = z.object({
  zones: z.array(trainingZoneSchema).min(1, 'At least one training zone is required'),
});

// Step 4: Competitions
export const competitionsSchema = z.object({
  competitions: z.array(competitionSchema).min(1, 'At least one competition is required'),
});

// Step 5: External Race Integration (Optional)
export const externalRacesSchema = z.object({
  bikereg_events: z.array(bikeregEventSchema).optional().default([]),
  runreg_events: z.array(runregEventSchema).optional().default([]),
});

// Step 6: Analysis Settings
export const analysisSettingsSchema = z.object({
  activities_days: z.number().int().min(1, 'Must be at least 1 day').max(365, 'Cannot exceed 365 days'),
  metrics_days: z.number().int().min(1, 'Must be at least 1 day').max(365, 'Cannot exceed 365 days'),
  ai_mode: z.enum(['development', 'standard', 'cost_effective']),
  enable_plotting: z.boolean(),
  hitl_enabled: z.boolean(),
  skip_synthesis: z.boolean(),
});

// Step 7: Output & Garmin Settings
export const outputGarminSchema = z.object({
  output_directory: z.string().min(1, 'Output directory is required'),
  garmin_email: z.string().email('Valid Garmin Connect email required'),
  garmin_password: z.string().min(6, 'Garmin password must be at least 6 characters'),
});

// Complete training profile schema
export const completeTrainingProfileSchema = athleteInfoSchema
  .merge(trainingContextSchema)
  .merge(trainingZonesSchema)
  .merge(competitionsSchema)
  .merge(externalRacesSchema)
  .merge(analysisSettingsSchema)
  .merge(outputGarminSchema);

// Type inference
export type AthleteInfoFormData = z.infer<typeof athleteInfoSchema>;
export type TrainingContextFormData = z.infer<typeof trainingContextSchema>;
export type TrainingZonesFormData = z.infer<typeof trainingZonesSchema>;
export type CompetitionsFormData = z.infer<typeof competitionsSchema>;
export type ExternalRacesFormData = z.infer<typeof externalRacesSchema>;
export type AnalysisSettingsFormData = z.infer<typeof analysisSettingsSchema>;
export type OutputGarminFormData = z.infer<typeof outputGarminSchema>;
export type CompleteTrainingProfileFormData = z.infer<typeof completeTrainingProfileSchema>;

// Default values for forms
export const defaultTrainingProfileData: Partial<CompleteTrainingProfileFormData> = {
  athlete_name: '',
  athlete_email: '',
  analysis_context: '',
  planning_context: '',
  training_needs: '',
  session_constraints: '',
  training_preferences: '',
  zones: [
    {
      discipline: 'Running',
      metric: 'LTHR ≈ 171 bpm / 4:35 min/km',
      value: '171 bpm',
    },
    {
      discipline: 'Cycling', 
      metric: 'FTP ≈ 213W',
      value: '213W',
    },
  ],
  competitions: [],
  bikereg_events: [],
  runreg_events: [],
  activities_days: 21,
  metrics_days: 56,
  ai_mode: 'development',
  enable_plotting: false,
  hitl_enabled: true,
  skip_synthesis: false,
  output_directory: './data',
  garmin_email: '',
  garmin_password: '',
};