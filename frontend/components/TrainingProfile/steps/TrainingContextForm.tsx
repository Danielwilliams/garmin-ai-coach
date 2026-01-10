import React from 'react';
import { Control, Controller, FieldErrors } from 'react-hook-form';
import TextArea from '@/components/ui/TextArea';
import { CompleteTrainingProfileFormData } from '@/lib/validations/training';

interface TrainingContextFormProps {
  control: Control<CompleteTrainingProfileFormData>;
  errors: FieldErrors<CompleteTrainingProfileFormData>;
}

const TrainingContextForm: React.FC<TrainingContextFormProps> = ({ control, errors }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-6">
        <Controller
          name="analysis_context"
          control={control}
          render={({ field }) => (
            <TextArea
              {...field}
              label="Analysis Context"
              placeholder="Describe your current training situation, recent performances, and what you want the AI to focus on in analysis..."
              rows={4}
              error={errors.analysis_context?.message}
              helperText="Provide context for AI analysis of your training data (minimum 10 characters)"
            />
          )}
        />

        <Controller
          name="planning_context"
          control={control}
          render={({ field }) => (
            <TextArea
              {...field}
              label="Planning Context"
              placeholder="Describe your training goals, upcoming events, and any specific considerations for training planning..."
              rows={4}
              error={errors.planning_context?.message}
              helperText="Provide context for AI training plan development (minimum 10 characters)"
            />
          )}
        />

        <Controller
          name="training_needs"
          control={control}
          render={({ field }) => (
            <TextArea
              {...field}
              label="Training Needs (Optional)"
              placeholder="Specific areas you want to improve (e.g., endurance, speed, climbing, technique)..."
              rows={3}
              error={errors.training_needs?.message}
              helperText="Optional: Describe specific training needs or weaknesses to address"
            />
          )}
        />

        <Controller
          name="session_constraints"
          control={control}
          render={({ field }) => (
            <TextArea
              {...field}
              label="Session Constraints (Optional)"
              placeholder="Time limitations, available training days, equipment constraints, location restrictions..."
              rows={3}
              error={errors.session_constraints?.message}
              helperText="Optional: Describe any constraints on your training sessions"
            />
          )}
        />

        <Controller
          name="training_preferences"
          control={control}
          render={({ field }) => (
            <TextArea
              {...field}
              label="Training Preferences (Optional)"
              placeholder="Preferred training methods, workout types you enjoy, training philosophy..."
              rows={3}
              error={errors.training_preferences?.message}
              helperText="Optional: Describe your training preferences and philosophy"
            />
          )}
        />
      </div>

      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-green-800">
              Context Tips
            </h3>
            <div className="mt-2 text-sm text-green-700">
              <ul className="list-disc list-inside space-y-1">
                <li><strong>Analysis Context:</strong> Current fitness level, recent races, injury history, data patterns you've noticed</li>
                <li><strong>Planning Context:</strong> Season goals, priority events, training time availability, past successful approaches</li>
                <li><strong>Be specific:</strong> The more detailed context you provide, the better the AI can tailor analysis and planning to your needs</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainingContextForm;