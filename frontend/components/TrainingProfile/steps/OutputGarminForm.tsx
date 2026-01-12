import React, { useState } from 'react';
import { Control, Controller, FieldErrors, useWatch } from 'react-hook-form';
import { FolderOpen, Shield, Eye, EyeOff, CheckCircle, XCircle, Loader } from 'lucide-react';
import Input from '@/components/ui/Input';
import { CompleteTrainingProfileFormData } from '@/lib/validations/training';

interface OutputGarminFormProps {
  control: Control<CompleteTrainingProfileFormData>;
  errors: FieldErrors<CompleteTrainingProfileFormData>;
}

const OutputGarminForm: React.FC<OutputGarminFormProps> = ({ control, errors }) => {
  const [showPassword, setShowPassword] = useState(false);
  const [testingConnection, setTestingConnection] = useState(false);
  const [connectionResult, setConnectionResult] = useState<{
    status: 'success' | 'error' | null;
    message: string;
    userDisplayName?: string;
  }>({ status: null, message: '' });

  // Watch Garmin credentials to enable/disable test button
  const garminEmail = useWatch({ control, name: 'garmin_email' });
  const garminPassword = useWatch({ control, name: 'garmin_password' });

  const handleTestConnection = async () => {
    if (!garminEmail || !garminPassword) {
      setConnectionResult({
        status: 'error',
        message: 'Please enter both email and password before testing.'
      });
      return;
    }

    setTestingConnection(true);
    setConnectionResult({ status: null, message: '' });

    // Simulate connection test (replace with actual API call)
    try {
      await new Promise(resolve => setTimeout(resolve, 2000)); // Simulate network delay
      
      // Mock successful connection
      setConnectionResult({
        status: 'success',
        message: 'Connection successful! Ready to sync data.',
        userDisplayName: 'Test User'
      });
    } catch (error) {
      setConnectionResult({
        status: 'error',
        message: 'Connection failed. Please check your credentials.'
      });
    } finally {
      setTestingConnection(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="bg-green-50 border border-green-200 rounded-lg p-4">
        <div className="flex">
          <div className="flex-shrink-0">
            <Shield className="h-5 w-5 text-green-400" />
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-green-800">
              Final Configuration
            </h3>
            <div className="mt-2 text-sm text-green-700">
              <p>
                Configure output settings and Garmin Connect credentials to complete your training profile setup.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Output Settings */}
      <div className="space-y-6">
        <div className="flex items-center mb-4">
          <FolderOpen className="w-5 h-5 text-gray-600 mr-2" />
          <h3 className="text-lg font-medium text-gray-900">Output Settings</h3>
        </div>

        <div className="bg-gray-50 rounded-lg p-4 border">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Output Directory</h4>
          <p className="text-sm text-gray-600 mb-3">
            Analysis results will be saved to: <code className="bg-gray-200 px-1 rounded">./data/{'{'}profile-name{'}'}</code>
          </p>
          <Controller
            name="output_directory"
            control={control}
            render={({ field }) => (
              <input
                {...field}
                type="hidden"
                value="./data"
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
              <h4 className="text-sm font-medium text-blue-800">
                Output Directory Info
              </h4>
              <div className="mt-2 text-sm text-blue-700">
                <p>
                  Analysis results will include HTML reports, training plans, performance plots, 
                  and raw data exports. Choose a directory that's easy to access and has sufficient storage space.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Garmin Connect Integration */}
      <div className="space-y-6">
        <div className="flex items-center mb-4">
          <svg className="w-5 h-5 text-gray-600 mr-2" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
          <h3 className="text-lg font-medium text-gray-900">Garmin Connect Credentials</h3>
        </div>

        <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 mb-6">
          <div className="flex">
            <div className="flex-shrink-0">
              <Shield className="h-5 w-5 text-amber-400" />
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-amber-800">
                Security Notice
              </h4>
              <div className="mt-2 text-sm text-amber-700">
                <p>
                  Your Garmin Connect credentials are encrypted and stored securely. They're used only 
                  to download your training data for analysis. You can revoke access at any time.
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Controller
            name="garmin_email"
            control={control}
            render={({ field }) => (
              <Input
                {...field}
                label="Garmin Connect Email"
                type="email"
                placeholder="your-email@example.com"
                error={errors.garmin_email?.message}
                helperText="Your Garmin Connect login email address"
              />
            )}
          />

          <Controller
            name="garmin_password"
            control={control}
            render={({ field }) => (
              <div className="relative">
                <Input
                  {...field}
                  label="Garmin Connect Password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Your Garmin Connect password"
                  error={errors.garmin_password?.message}
                  helperText="Your Garmin Connect login password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-8 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            )}
          />
        </div>

        {/* Test Connection */}
        <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border">
          <div>
            <h4 className="text-sm font-medium text-gray-900">Test Connection</h4>
            <p className="text-sm text-gray-600">Verify your Garmin Connect credentials</p>
          </div>
          <button
            type="button"
            onClick={handleTestConnection}
            disabled={!garminEmail || !garminPassword || testingConnection}
            className={`px-4 py-2 rounded-md text-sm font-medium flex items-center gap-2 ${
              !garminEmail || !garminPassword || testingConnection
                ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {testingConnection ? (
              <>
                <Loader className="w-4 h-4 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <Shield className="w-4 h-4" />
                Test Connection
              </>
            )}
          </button>
        </div>

        {/* Connection Result */}
        {connectionResult.status && (
          <div className={`p-4 rounded-lg border ${
            connectionResult.status === 'success' 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-start">
              <div className="flex-shrink-0">
                {connectionResult.status === 'success' ? (
                  <CheckCircle className="h-5 w-5 text-green-400" />
                ) : (
                  <XCircle className="h-5 w-5 text-red-400" />
                )}
              </div>
              <div className="ml-3">
                <h4 className={`text-sm font-medium ${
                  connectionResult.status === 'success' ? 'text-green-800' : 'text-red-800'
                }`}>
                  {connectionResult.status === 'success' ? 'Connection Successful' : 'Connection Failed'}
                </h4>
                <p className={`text-sm mt-1 ${
                  connectionResult.status === 'success' ? 'text-green-700' : 'text-red-700'
                }`}>
                  {connectionResult.message}
                  {connectionResult.userDisplayName && (
                    <span className="block mt-1">
                      Welcome, <strong>{connectionResult.userDisplayName}</strong>!
                    </span>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-red-800">
                Important Requirements
              </h4>
              <div className="mt-2 text-sm text-red-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>Use your regular Garmin Connect credentials (not app-specific passwords)</li>
                  <li>Ensure two-factor authentication is disabled or properly configured</li>
                  <li>Your account must have activity data available for analysis</li>
                  <li>We recommend testing the connection before running full analysis</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-6 border">
        <h4 className="text-lg font-medium text-gray-900 mb-4">What Happens Next?</h4>
        <div className="space-y-3 text-sm text-gray-600">
          <div className="flex items-start">
            <div className="flex-shrink-0 mt-1">
              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
            </div>
            <div className="ml-3">
              <p><strong>Profile Creation:</strong> Your training profile will be saved and validated</p>
            </div>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0 mt-1">
              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
            </div>
            <div className="ml-3">
              <p><strong>Data Connection:</strong> We'll test your Garmin Connect credentials</p>
            </div>
          </div>
          <div className="flex items-start">
            <div className="flex-shrink-0 mt-1">
              <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
            </div>
            <div className="ml-3">
              <p><strong>Ready to Analyze:</strong> Your profile will be ready for AI training analysis</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OutputGarminForm;