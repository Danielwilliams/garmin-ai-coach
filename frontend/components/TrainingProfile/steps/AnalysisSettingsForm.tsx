import React from 'react';
import { Control, Controller, FieldErrors } from 'react-hook-form';
import { Settings, Database, Brain, BarChart } from 'lucide-react';
import Input from '@/components/ui/Input';
import Select from '@/components/ui/Select';
import { CompleteTrainingProfileFormData } from '@/lib/validations/training';

interface AnalysisSettingsFormProps {
  control: Control<CompleteTrainingProfileFormData>;
  errors: FieldErrors<CompleteTrainingProfileFormData>;
}

const AnalysisSettingsForm: React.FC<AnalysisSettingsFormProps> = ({ control, errors }) => {
  const aiModeOptions = [
    { value: 'development', label: 'Development - Most comprehensive analysis' },
    { value: 'standard', label: 'Standard - Balanced analysis and cost' },
    { value: 'cost_effective', label: 'Cost Effective - Budget-friendly analysis' }
  ];

  return (
    <div className="space-y-8">
      <div className="bg-indigo-50 border border-indigo-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Settings className="h-5 w-5 text-indigo-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-indigo-800">
              Analysis Configuration
            </h3>
            <div className="mt-2 text-sm text-indigo-700">
              <p>
                Configure how much data to analyze and the AI processing settings for your training insights.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Data Extraction Settings */}
      <div className="space-y-6">
        <div className="flex items-center mb-4">
          <Database className="w-5 h-5 text-gray-600 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">Data Extraction</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Controller
            name="activities_days"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                label="Activities Days"
                type="number"
                min="1"
                max="365"
                placeholder="21"
                error={errors.activities_days?.message}
                helperText="Number of days of activity data to analyze (1-365)"
                onChange={(e) => field.onChange(parseInt(e.target.value) || 21)}
                value={field.value || ''}
              />
            )}
          />

          <Controller
            name="metrics_days"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                label="Metrics Days"
                type="number"
                min="1"
                max="365"
                placeholder="56"
                error={errors.metrics_days?.message}
                helperText="Number of days of health metrics to analyze (1-365)"
                onChange={(e) => field.onChange(parseInt(e.target.value) || 56)}
                value={field.value || ''}
              />
            )}
          />
        </div>
      </div>

      {/* AI Analysis Settings */}
      <div className="space-y-6">
        <div className="flex items-center mb-4">
          <Brain className="w-5 h-5 text-gray-600 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">AI Analysis Settings</h3>
        </div>

        <Controller
          name="ai_mode"
          control={control}
          render={({ field }) => (
            <Select
              {...field}
              label="AI Analysis Mode"
              options={aiModeOptions}
              error={errors.ai_mode?.message}
              helperText="Choose the depth of AI analysis vs cost trade-off"
            />
          )}
        />

        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">AI Mode Details</h4>
          <div className="text-sm text-gray-600 space-y-2">
            <div><strong>Development:</strong> Most comprehensive analysis with detailed insights (highest cost)</div>
            <div><strong>Standard:</strong> Balanced analysis with good insights for most users</div>
            <div><strong>Cost Effective:</strong> Basic analysis optimized for budget-conscious users</div>
          </div>
        </div>
      </div>

      {/* Processing Options */}
      <div className="space-y-6">
        <div className="flex items-center mb-4">
          <BarChart className="w-5 h-5 text-gray-600 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">Processing Options</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <Controller
              name="enable_plotting"
              control={control}
              render={({ field }) => (
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="enable_plotting"
                      type="checkbox"
                      checked={field.value || false}
                      onChange={field.onChange}
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                  </div>
                  <div className="ml-3 text-sm">
                    <label htmlFor="enable_plotting" className="font-medium text-gray-700">
                      Enable Plotting
                    </label>
                    <p className="text-gray-500">
                      Generate visual charts and graphs for analysis results
                    </p>
                  </div>
                </div>
              )}
            />

            <Controller
              name="hitl_enabled"
              control={control}
              render={({ field }) => (
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="hitl_enabled"
                      type="checkbox"
                      checked={field.value}
                      onChange={field.onChange}
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                  </div>
                  <div className="ml-3 text-sm">
                    <label htmlFor="hitl_enabled" className="font-medium text-gray-700">
                      Human-in-the-Loop (HITL)
                    </label>
                    <p className="text-gray-500">
                      Enable human review and feedback during AI analysis
                    </p>
                  </div>
                </div>
              )}
            />
          </div>

          <div className="space-y-4">
            <Controller
              name="skip_synthesis"
              control={control}
              render={({ field }) => (
                <div className="flex items-start">
                  <div className="flex items-center h-5">
                    <input
                      id="skip_synthesis"
                      type="checkbox"
                      checked={field.value || false}
                      onChange={field.onChange}
                      className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                    />
                  </div>
                  <div className="ml-3 text-sm">
                    <label htmlFor="skip_synthesis" className="font-medium text-gray-700">
                      Skip Synthesis
                    </label>
                    <p className="text-gray-500">
                      Skip final synthesis step to save time and cost
                    </p>
                  </div>
                </div>
              )}
            />
          </div>
        </div>
      </div>

      <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-emerald-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-emerald-800">
              Recommended Settings
            </h3>
            <div className="mt-2 text-sm text-emerald-700">
              <ul className="list-disc list-inside space-y-1">
                <li><strong>First-time users:</strong> 21 activity days, 56 metrics days, Standard AI mode</li>
                <li><strong>Detailed analysis:</strong> 45-90 activity days, Development mode, Enable plotting</li>
                <li><strong>Budget-conscious:</strong> 14 activity days, 28 metrics days, Cost effective mode</li>
                <li><strong>HITL:</strong> Recommended for important race preparation periods</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisSettingsForm;