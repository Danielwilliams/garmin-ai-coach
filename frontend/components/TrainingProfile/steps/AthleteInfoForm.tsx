import React from 'react';
import { Control, Controller, FieldErrors } from 'react-hook-form';
import Input from '@/components/ui/Input';
import { CompleteTrainingProfileFormData } from '@/lib/validations/training';

interface AthleteInfoFormProps {
  control: Control<CompleteTrainingProfileFormData>;
  errors: FieldErrors<CompleteTrainingProfileFormData>;
}

const AthleteInfoForm: React.FC<AthleteInfoFormProps> = ({ control, errors }) => {
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Controller
          name="athlete_name"
          control={control}
          render={({ field }) => (
            <Input
              {...field}
              label="Athlete Name"
              placeholder="Enter full name"
              error={errors.athlete_name?.message}
              helperText="Your full name as it appears in training records"
            />
          )}
        />

        <Controller
          name="athlete_email"
          control={control}
          render={({ field }) => (
            <Input
              {...field}
              label="Email Address"
              type="email"
              placeholder="athlete@example.com"
              error={errors.athlete_email?.message}
              helperText="Primary email for training communications"
            />
          )}
        />
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-blue-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              About Athlete Information
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                This information will be used to personalize your training analysis and reports. 
                Your email will be used for notifications about training insights and plan updates.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AthleteInfoForm;