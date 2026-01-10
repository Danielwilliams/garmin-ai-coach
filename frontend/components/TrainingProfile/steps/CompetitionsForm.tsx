import React from 'react';
import { Control, Controller, FieldErrors, UseFormSetValue, UseFormWatch } from 'react-hook-form';
import { Plus, Trash2, Calendar } from 'lucide-react';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { CompleteTrainingProfileFormData } from '@/lib/validations/training';
import { Competition } from '@/types/training';

interface CompetitionsFormProps {
  control: Control<CompleteTrainingProfileFormData>;
  errors: FieldErrors<CompleteTrainingProfileFormData>;
  setValue: UseFormSetValue<CompleteTrainingProfileFormData>;
  watch: UseFormWatch<CompleteTrainingProfileFormData>;
}

const CompetitionsForm: React.FC<CompetitionsFormProps> = ({ 
  control, 
  errors, 
  setValue, 
  watch 
}) => {
  const competitions = watch('competitions') || [];

  const priorityOptions = [
    { value: 'A', label: 'A - Highest Priority (Peak race)' },
    { value: 'B', label: 'B - Medium Priority (Important race)' },
    { value: 'C', label: 'C - Low Priority (Training race)' }
  ];

  const addCompetition = () => {
    const newCompetition: Competition = {
      id: `comp_${Date.now()}`,
      name: '',
      date: '',
      race_type: '',
      priority: 'B',
      target_time: ''
    };
    setValue('competitions', [...competitions, newCompetition]);
  };

  const removeCompetition = (index: number) => {
    const updatedCompetitions = competitions.filter((_, i) => i !== index);
    setValue('competitions', updatedCompetitions);
  };

  const updateCompetition = (index: number, field: keyof Competition, value: string) => {
    const updatedCompetitions = [...competitions];
    updatedCompetitions[index] = {
      ...updatedCompetitions[index],
      [field]: value
    };
    setValue('competitions', updatedCompetitions);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-medium text-gray-900">Target Competitions</h3>
        <button
          type="button"
          onClick={addCompetition}
          className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Competition
        </button>
      </div>

      {competitions.length === 0 && (
        <div className="text-center py-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
          <Calendar className="mx-auto h-12 w-12 text-gray-400" />
          <p className="mt-2 text-sm text-gray-600">
            No competitions added yet. Add your target races to build your training plan.
          </p>
        </div>
      )}

      <div className="space-y-6">
        {competitions.map((competition, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-6 border">
            <div className="flex items-start justify-between mb-4">
              <h4 className="text-md font-medium text-gray-900">
                Competition {index + 1}
              </h4>
              <button
                type="button"
                onClick={() => removeCompetition(index)}
                className="text-red-600 hover:text-red-800 transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
              <Controller
                name={`competitions.${index}.name`}
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="Race Name"
                    placeholder="e.g., Boston Marathon, Ironman Boulder"
                    onChange={(e) => updateCompetition(index, 'name', e.target.value)}
                    error={errors.competitions?.[index]?.name?.message}
                  />
                )}
              />

              <Controller
                name={`competitions.${index}.date`}
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="Date"
                    type="date"
                    onChange={(e) => updateCompetition(index, 'date', e.target.value)}
                    error={errors.competitions?.[index]?.date?.message}
                    helperText="You can also use free text format like 'Mid April 2024'"
                  />
                )}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Controller
                name={`competitions.${index}.race_type`}
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="Race Type"
                    placeholder="e.g., Marathon, 70.3, Olympic Tri"
                    onChange={(e) => updateCompetition(index, 'race_type', e.target.value)}
                    error={errors.competitions?.[index]?.race_type?.message}
                  />
                )}
              />

              <Controller
                name={`competitions.${index}.priority`}
                control={control}
                render={({ field }) => (
                  <Select
                    {...field}
                    label="Priority"
                    options={priorityOptions}
                    onChange={(e) => updateCompetition(index, 'priority', e.target.value as 'A' | 'B' | 'C')}
                    error={errors.competitions?.[index]?.priority?.message}
                  />
                )}
              />

              <Controller
                name={`competitions.${index}.target_time`}
                control={control}
                render={({ field }) => (
                  <Input
                    {...field}
                    label="Target Time (Optional)"
                    placeholder="HH:MM:SS (e.g., 3:15:00)"
                    onChange={(e) => updateCompetition(index, 'target_time', e.target.value)}
                    error={errors.competitions?.[index]?.target_time?.message}
                    helperText="Format: HH:MM:SS"
                  />
                )}
              />
            </div>
          </div>
        ))}
      </div>

      {errors.competitions && typeof errors.competitions.message === 'string' && (
        <p className="text-sm text-red-600">{errors.competitions.message}</p>
      )}

      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-purple-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-purple-800">
              Competition Priority Guide
            </h3>
            <div className="mt-2 text-sm text-purple-700">
              <ul className="list-disc list-inside space-y-1">
                <li><strong>A Priority:</strong> Your most important race(s) - peak performance target</li>
                <li><strong>B Priority:</strong> Important races but not your main focus</li>
                <li><strong>C Priority:</strong> Training races, fun events, or stepping stones</li>
                <li><strong>Planning:</strong> Training will be periodized around A priority races</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompetitionsForm;