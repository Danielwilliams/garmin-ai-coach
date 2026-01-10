import React from 'react';
import { Control, Controller, FieldErrors, UseFormSetValue, UseFormWatch } from 'react-hook-form';
import { Plus, Trash2 } from 'lucide-react';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { CompleteTrainingProfileFormData } from '@/lib/validations/training';
import { TrainingZone } from '@/types/training';

interface TrainingZonesFormProps {
  control: Control<CompleteTrainingProfileFormData>;
  errors: FieldErrors<CompleteTrainingProfileFormData>;
  setValue: UseFormSetValue<CompleteTrainingProfileFormData>;
  watch: UseFormWatch<CompleteTrainingProfileFormData>;
}

const TrainingZonesForm: React.FC<TrainingZonesFormProps> = ({ 
  control, 
  errors, 
  setValue, 
  watch 
}) => {
  const zones = watch('zones') || [];

  const disciplineOptions = [
    { value: 'Running', label: 'Running' },
    { value: 'Cycling', label: 'Cycling' },
    { value: 'Swimming', label: 'Swimming' }
  ];

  const addZone = () => {
    const newZone: TrainingZone = {
      discipline: 'Running',
      metric: '',
      value: ''
    };
    setValue('zones', [...zones, newZone]);
  };

  const removeZone = (index: number) => {
    const updatedZones = zones.filter((_, i) => i !== index);
    setValue('zones', updatedZones);
  };

  const updateZone = (index: number, field: keyof TrainingZone, value: string) => {
    const updatedZones = [...zones];
    updatedZones[index] = {
      ...updatedZones[index],
      [field]: value
    };
    setValue('zones', updatedZones);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Training Zones</h3>
        <button
          type="button"
          onClick={addZone}
          className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Zone
        </button>
      </div>

      {zones.length === 0 && (
        <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 48 48">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10h20.553a2 2 0 011.84 1.21l1.336 2.676A1 1 0 0137 15H11a1 1 0 00-.729 1.686l1.336-2.676A2 2 0 0113.447 10H14z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 23h30l-2 14H11l-2-14z" />
          </svg>
          <p className="mt-2 text-sm text-gray-600">
            No training zones defined yet. Add your first zone to get started.
          </p>
        </div>
      )}

      <div className="space-y-4">
        {zones.map((zone, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-4 border">
            <div className="flex items-start justify-between mb-4">
              <h4 className="text-md font-medium text-gray-900">
                Zone {index + 1}
              </h4>
              {zones.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeZone(index)}
                  className="text-red-600 hover:text-red-800 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Controller
                name={`zones.${index}.discipline`}
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    label="Discipline"
                    options={disciplineOptions}
                    placeholder="Select discipline"
                    onChange={(e) => updateZone(index, 'discipline', e.target.value as 'Running' | 'Cycling' | 'Swimming')}
                    error={errors.zones?.[index]?.discipline?.message}
                  />
                )}
              />

              <Controller
                name={`zones.${index}.metric`}
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="Metric Description"
                    placeholder="e.g., LTHR ≈ 171 bpm / 4:35 min/km"
                    onChange={(e) => updateZone(index, 'metric', e.target.value)}
                    error={errors.zones?.[index]?.metric?.message}
                  />
                )}
              />

              <Controller
                name={`zones.${index}.value`}
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="Zone Value"
                    placeholder="e.g., 171 bpm, 213W, 1:30/100m"
                    onChange={(e) => updateZone(index, 'value', e.target.value)}
                    error={errors.zones?.[index]?.value?.message}
                  />
                )}
              />
            </div>
          </div>
        ))}
      </div>

      {errors.zones && typeof errors.zones.message === 'string' && (
        <p className="text-sm text-red-600">{errors.zones.message}</p>
      )}

      <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-amber-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-amber-800">
              Training Zone Examples
            </h3>
            <div className="mt-2 text-sm text-amber-700">
              <ul className="list-disc list-inside space-y-1">
                <li><strong>Running:</strong> LTHR ≈ 171 bpm / 4:35 min/km → 171 bpm</li>
                <li><strong>Cycling:</strong> FTP ≈ 213W → 213W</li>
                <li><strong>Swimming:</strong> T-Pace ≈ 1:30/100m → 1:30/100m</li>
                <li><strong>Multiple zones:</strong> Add separate entries for different intensity zones</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TrainingZonesForm;