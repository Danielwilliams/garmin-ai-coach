import React from 'react';
import { Control, Controller, FieldErrors, UseFormSetValue, UseFormWatch } from 'react-hook-form';
import { Plus, Trash2, ExternalLink, Info } from 'lucide-react';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { CompleteTrainingProfileFormData } from '@/lib/validations/training';
import { BikeRegEvent, RunRegEvent } from '@/types/training';

interface ExternalRacesFormProps {
  control: Control<CompleteTrainingProfileFormData>;
  errors: FieldErrors<CompleteTrainingProfileFormData>;
  setValue: UseFormSetValue<CompleteTrainingProfileFormData>;
  watch: UseFormWatch<CompleteTrainingProfileFormData>;
}

const ExternalRacesForm: React.FC<ExternalRacesFormProps> = ({ 
  control, 
  errors, 
  setValue, 
  watch 
}) => {
  const bikeregEvents = watch('bikereg_events') || [];
  const runregEvents = watch('runreg_events') || [];

  const priorityOptions = [
    { value: 'A', label: 'A - Highest Priority' },
    { value: 'B', label: 'B - Medium Priority' },
    { value: 'C', label: 'C - Low Priority' }
  ];

  const addBikeRegEvent = () => {
    const newEvent: BikeRegEvent = {
      id: `bikereg_${Date.now()}`,
      bikereg_id: 0,
      priority: 'B',
      target_time: ''
    };
    setValue('bikereg_events', [...bikeregEvents, newEvent]);
  };

  const removeBikeRegEvent = (index: number) => {
    const updatedEvents = bikeregEvents.filter((_, i) => i !== index);
    setValue('bikereg_events', updatedEvents);
  };

  const updateBikeRegEvent = (index: number, field: keyof BikeRegEvent, value: string | number) => {
    const updatedEvents = [...bikeregEvents];
    updatedEvents[index] = {
      ...updatedEvents[index],
      [field]: value
    };
    setValue('bikereg_events', updatedEvents);
  };

  const addRunRegEvent = () => {
    const newEvent: RunRegEvent = {
      id: `runreg_${Date.now()}`,
      url: '',
      priority: 'B',
      target_time: ''
    };
    setValue('runreg_events', [...runregEvents, newEvent]);
  };

  const removeRunRegEvent = (index: number) => {
    const updatedEvents = runregEvents.filter((_, i) => i !== index);
    setValue('runreg_events', updatedEvents);
  };

  const updateRunRegEvent = (index: number, field: keyof RunRegEvent, value: string) => {
    const updatedEvents = [...runregEvents];
    updatedEvents[index] = {
      ...updatedEvents[index],
      [field]: value
    };
    setValue('runreg_events', updatedEvents);
  };

  return (
    <div className="space-y-8">
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Info className="h-5 w-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-blue-800">
              External Race Integration (Optional)
            </h3>
            <div className="mt-2 text-sm text-blue-700">
              <p>
                Connect races from BikeReg and RunReg platforms for automatic race data import. 
                This is optional - you can skip this step if you don't use these platforms.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* BikeReg Events */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <ExternalLink className="w-5 h-5 mr-2" />
              BikeReg Events
            </h3>
            <p className="text-sm text-gray-600">Import cycling races from BikeReg.com</p>
          </div>
          <button
            type="button"
            onClick={addBikeRegEvent}
            className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add BikeReg Event
          </button>
        </div>

        {bikeregEvents.length === 0 && (
          <div className="text-center py-6 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <p className="text-sm text-gray-600">
              No BikeReg events added. Add events to import race data automatically.
            </p>
          </div>
        )}

        <div className="space-y-4">
          {bikeregEvents.map((event, index) => (
            <div key={index} className="bg-gray-50 rounded-lg p-4 border">
              <div className="flex items-start justify-between mb-4">
                <h4 className="text-md font-medium text-gray-900">
                  BikeReg Event {index + 1}
                </h4>
                <button
                  type="button"
                  onClick={() => removeBikeRegEvent(index)}
                  className="text-red-600 hover:text-red-800 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Controller
                  name={`bikereg_events.${index}.bikereg_id`}
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      label="BikeReg Event ID"
                      type="number"
                      placeholder="e.g., 12345"
                      onChange={(e) => updateBikeRegEvent(index, 'bikereg_id', parseInt(e.target.value) || 0)}
                      error={errors.bikereg_events?.[index]?.bikereg_id?.message}
                      helperText="Find ID in the BikeReg URL"
                    />
                  )}
                />

                <Controller
                  name={`bikereg_events.${index}.priority`}
                  control={control}
                  render={({ field }) => (
                    <Select
                      {...field}
                      label="Priority"
                      options={priorityOptions}
                      onChange={(e) => updateBikeRegEvent(index, 'priority', e.target.value as 'A' | 'B' | 'C')}
                      error={errors.bikereg_events?.[index]?.priority?.message}
                    />
                  )}
                />

                <Controller
                  name={`bikereg_events.${index}.target_time`}
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      label="Target Time (Optional)"
                      placeholder="HH:MM:SS"
                      onChange={(e) => updateBikeRegEvent(index, 'target_time', e.target.value)}
                      error={errors.bikereg_events?.[index]?.target_time?.message}
                    />
                  )}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* RunReg Events */}
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div>
            <h3 className="text-lg font-medium text-gray-900 flex items-center">
              <ExternalLink className="w-5 h-5 mr-2" />
              RunReg Events
            </h3>
            <p className="text-sm text-gray-600">Import running races from RunReg.com</p>
          </div>
          <button
            type="button"
            onClick={addRunRegEvent}
            className="flex items-center px-3 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            Add RunReg Event
          </button>
        </div>

        {runregEvents.length === 0 && (
          <div className="text-center py-6 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
            <p className="text-sm text-gray-600">
              No RunReg events added. Add events to import race data automatically.
            </p>
          </div>
        )}

        <div className="space-y-4">
          {runregEvents.map((event, index) => (
            <div key={index} className="bg-gray-50 rounded-lg p-4 border">
              <div className="flex items-start justify-between mb-4">
                <h4 className="text-md font-medium text-gray-900">
                  RunReg Event {index + 1}
                </h4>
                <button
                  type="button"
                  onClick={() => removeRunRegEvent(index)}
                  className="text-red-600 hover:text-red-800 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Controller
                  name={`runreg_events.${index}.url`}
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      label="RunReg Event URL"
                      placeholder="https://runreg.com/event-name"
                      onChange={(e) => updateRunRegEvent(index, 'url', e.target.value)}
                      error={errors.runreg_events?.[index]?.url?.message}
                      className="md:col-span-1"
                    />
                  )}
                />

                <Controller
                  name={`runreg_events.${index}.priority`}
                  control={control}
                  render={({ field }) => (
                    <Select
                      {...field}
                      label="Priority"
                      options={priorityOptions}
                      onChange={(e) => updateRunRegEvent(index, 'priority', e.target.value as 'A' | 'B' | 'C')}
                      error={errors.runreg_events?.[index]?.priority?.message}
                    />
                  )}
                />

                <Controller
                  name={`runreg_events.${index}.target_time`}
                  control={control}
                  render={({ field }) => (
                    <Input
                      {...field}
                      label="Target Time (Optional)"
                      placeholder="HH:MM:SS"
                      onChange={(e) => updateRunRegEvent(index, 'target_time', e.target.value)}
                      error={errors.runreg_events?.[index]?.target_time?.message}
                    />
                  )}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-yellow-800">
              Finding Race IDs and URLs
            </h3>
            <div className="mt-2 text-sm text-yellow-700">
              <ul className="list-disc list-inside space-y-1">
                <li><strong>BikeReg ID:</strong> Found in the URL - bikereg.com/[event-name]/[ID]</li>
                <li><strong>RunReg URL:</strong> Copy the full event page URL from your browser</li>
                <li>These integrations will automatically pull race details and results when available</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExternalRacesForm;