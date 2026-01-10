'use client';

import React, { useState, useCallback } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { 
  completeTrainingProfileSchema, 
  defaultTrainingProfileData,
  type CompleteTrainingProfileFormData 
} from '@/lib/validations/training';
import { TrainingProfileFormStep } from '@/types/training';
import AthleteInfoForm from './steps/AthleteInfoForm';
import TrainingContextForm from './steps/TrainingContextForm';
import TrainingZonesForm from './steps/TrainingZonesForm';
import CompetitionsForm from './steps/CompetitionsForm';
import ExternalRacesForm from './steps/ExternalRacesForm';
import AnalysisSettingsForm from './steps/AnalysisSettingsForm';
import OutputGarminForm from './steps/OutputGarminForm';

interface TrainingProfileWizardProps {
  onSubmit: (data: CompleteTrainingProfileFormData) => Promise<void>;
  onCancel?: () => void;
  initialData?: Partial<CompleteTrainingProfileFormData>;
}

const TrainingProfileWizard: React.FC<TrainingProfileWizardProps> = ({
  onSubmit,
  onCancel,
  initialData
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const form = useForm<CompleteTrainingProfileFormData>({
    resolver: zodResolver(completeTrainingProfileSchema),
    defaultValues: { ...defaultTrainingProfileData, ...initialData },
    mode: 'onChange'
  });

  const { handleSubmit, trigger, getValues, formState: { errors, isValid } } = form;

  const steps: TrainingProfileFormStep[] = [
    {
      step: 0,
      title: 'Athlete Information',
      description: 'Basic athlete details and contact information',
      isComplete: false,
      isValid: false
    },
    {
      step: 1,
      title: 'Training Context',
      description: 'Analysis and planning context for training',
      isComplete: false,
      isValid: false
    },
    {
      step: 2,
      title: 'Training Zones',
      description: 'Performance zones for different disciplines',
      isComplete: false,
      isValid: false
    },
    {
      step: 3,
      title: 'Competitions',
      description: 'Target races and events with priorities',
      isComplete: false,
      isValid: false
    },
    {
      step: 4,
      title: 'External Races',
      description: 'BikeReg and RunReg race integrations (optional)',
      isComplete: false,
      isValid: false
    },
    {
      step: 5,
      title: 'Analysis Settings',
      description: 'Data extraction and AI analysis configuration',
      isComplete: false,
      isValid: false
    },
    {
      step: 6,
      title: 'Output & Garmin',
      description: 'Output settings and Garmin Connect credentials',
      isComplete: false,
      isValid: false
    }
  ];

  const validateCurrentStep = useCallback(async () => {
    const stepFields: Record<number, string[]> = {
      0: ['athlete_name', 'athlete_email'],
      1: ['analysis_context', 'planning_context'],
      2: ['zones'],
      3: ['competitions'],
      4: ['bikereg_events', 'runreg_events'],
      5: ['activities_days', 'metrics_days', 'ai_mode', 'enable_plotting', 'hitl_enabled', 'skip_synthesis'],
      6: ['output_directory', 'garmin_email', 'garmin_password']
    };

    const fieldsToValidate = stepFields[currentStep];
    if (fieldsToValidate) {
      return await trigger(fieldsToValidate as any);
    }
    return true;
  }, [currentStep, trigger]);

  const handleNext = async () => {
    const isStepValid = await validateCurrentStep();
    if (isStepValid && currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleStepClick = async (stepIndex: number) => {
    if (stepIndex < currentStep) {
      setCurrentStep(stepIndex);
    } else if (stepIndex === currentStep + 1) {
      const isStepValid = await validateCurrentStep();
      if (isStepValid) {
        setCurrentStep(stepIndex);
      }
    }
  };

  const onFormSubmit = async (data: CompleteTrainingProfileFormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
    } catch (error) {
      console.error('Error submitting training profile:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return <AthleteInfoForm control={form.control} errors={errors} />;
      case 1:
        return <TrainingContextForm control={form.control} errors={errors} />;
      case 2:
        return <TrainingZonesForm control={form.control} errors={errors} setValue={form.setValue} watch={form.watch} />;
      case 3:
        return <CompetitionsForm control={form.control} errors={errors} setValue={form.setValue} watch={form.watch} />;
      case 4:
        return <ExternalRacesForm control={form.control} errors={errors} setValue={form.setValue} watch={form.watch} />;
      case 5:
        return <AnalysisSettingsForm control={form.control} errors={errors} />;
      case 6:
        return <OutputGarminForm control={form.control} errors={errors} />;
      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Create Training Profile
        </h1>
        <p className="text-gray-600">
          Configure your training profile for AI-powered analysis and planning
        </p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => (
            <div 
              key={step.step}
              className={`flex flex-col items-center cursor-pointer ${
                index <= currentStep ? 'text-blue-600' : 'text-gray-400'
              }`}
              onClick={() => handleStepClick(index)}
            >
              <div
                className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium mb-2 ${
                  index < currentStep
                    ? 'bg-blue-600 text-white'
                    : index === currentStep
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-400'
                }`}
              >
                {index < currentStep ? '✓' : index + 1}
              </div>
              <div className="text-xs text-center max-w-20">
                <div className="font-medium">{step.title}</div>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`h-1 w-full mt-2 ${
                    index < currentStep ? 'bg-blue-600' : 'bg-gray-200'
                  }`}
                  style={{ minWidth: '60px' }}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Current Step Content */}
      <form onSubmit={handleSubmit(onFormSubmit)}>
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              {steps[currentStep].title}
            </h2>
            <p className="text-gray-600">
              {steps[currentStep].description}
            </p>
          </div>

          {renderStepContent()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <button
            type="button"
            onClick={onCancel}
            className="px-6 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Cancel
          </button>
          
          <div className="flex space-x-4">
            {currentStep > 0 && (
              <button
                type="button"
                onClick={handlePrevious}
                className="px-6 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
              >
                Previous
              </button>
            )}
            
            {currentStep < steps.length - 1 ? (
              <button
                type="button"
                onClick={handleNext}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                Next
              </button>
            ) : (
              <button
                type="submit"
                disabled={isSubmitting || !isValid}
                className={`px-6 py-2 rounded-md transition-colors ${
                  isSubmitting || !isValid
                    ? 'bg-gray-400 text-gray-200 cursor-not-allowed'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {isSubmitting ? 'Creating Profile...' : 'Create Profile'}
              </button>
            )}
          </div>
        </div>
      </form>
    </div>
  );
};

export default TrainingProfileWizard;