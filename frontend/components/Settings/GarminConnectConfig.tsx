'use client';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { 
  Shield, 
  Eye, 
  EyeOff, 
  CheckCircle, 
  XCircle, 
  Loader, 
  AlertTriangle,
  Info,
  ArrowLeft,
  RefreshCw
} from 'lucide-react';
import { trainingProfileAPI } from '@/lib/api';
import Input from '@/components/ui/Input';

const garminConfigSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(1, 'Password is required')
});

type GarminConfigForm = z.infer<typeof garminConfigSchema>;

interface GarminConnectConfigProps {
  profileId?: string;
  onBack?: () => void;
  onConnectionSuccess?: (userInfo: any) => void;
}

interface ConnectionStatus {
  status: 'idle' | 'testing' | 'success' | 'error';
  message: string;
  userDisplayName?: string;
  activityLevel?: string;
}

const GarminConnectConfig: React.FC<GarminConnectConfigProps> = ({
  profileId,
  onBack,
  onConnectionSuccess
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    status: 'idle',
    message: ''
  });
  const [existingConnection, setExistingConnection] = useState<any>(null);
  const [loadingExisting, setLoadingExisting] = useState(false);

  const form = useForm<GarminConfigForm>({
    resolver: zodResolver(garminConfigSchema),
    defaultValues: {
      email: '',
      password: ''
    }
  });

  const { handleSubmit, formState: { errors, isValid } } = form;

  // Load existing connection status if profileId is provided
  useEffect(() => {
    if (profileId) {
      loadExistingConnection();
    }
  }, [profileId]);

  const loadExistingConnection = async () => {
    if (!profileId) return;
    
    setLoadingExisting(true);
    try {
      const profile = await trainingProfileAPI.getProfile(profileId);
      if (profile.garmin_email) {
        setExistingConnection({
          email: profile.garmin_email,
          isConnected: profile.garmin_is_connected,
          lastSync: profile.last_sync_date
        });
        
        // Pre-fill email
        form.setValue('email', profile.garmin_email);
        
        if (profile.garmin_is_connected) {
          setConnectionStatus({
            status: 'success',
            message: 'Connected successfully',
            userDisplayName: 'Existing Connection'
          });
        }
      }
    } catch (error: any) {
      console.error('Failed to load existing connection:', error);
    } finally {
      setLoadingExisting(false);
    }
  };

  const testConnection = async (data: GarminConfigForm) => {
    setConnectionStatus({ status: 'testing', message: 'Testing connection...' });

    try {
      let result;
      
      if (profileId) {
        // Test with profile-specific endpoint
        result = await trainingProfileAPI.testGarminConnection(profileId);
      } else {
        // Test with standalone endpoint
        result = await trainingProfileAPI.testGarminCredentials(data.email, data.password);
      }
      
      if (result.status === 'success') {
        setConnectionStatus({
          status: 'success',
          message: result.message,
          userDisplayName: result.user_display_name,
          activityLevel: result.activity_level
        });
        
        // Save credentials to user's default profile
        try {
          await trainingProfileAPI.saveGarminCredentials(data.email, data.password);
          console.log('Garmin credentials saved to default profile');
        } catch (saveError: any) {
          console.error('Failed to save Garmin credentials:', saveError);
          // Don't fail the connection test if saving fails
        }
        
        if (onConnectionSuccess) {
          onConnectionSuccess({
            email: data.email,
            userDisplayName: result.user_display_name,
            activityLevel: result.activity_level
          });
        }
      } else {
        setConnectionStatus({
          status: 'error',
          message: result.message || 'Connection failed. Please check your credentials.'
        });
      }
    } catch (error: any) {
      setConnectionStatus({
        status: 'error',
        message: error.detail || 'Connection failed. Please check your credentials.'
      });
    }
  };

  const retestConnection = async () => {
    if (!profileId || !existingConnection?.email) return;
    
    setConnectionStatus({ status: 'testing', message: 'Retesting connection...' });
    
    try {
      const result = await trainingProfileAPI.testGarminConnection(profileId);
      
      if (result.status === 'success') {
        setConnectionStatus({
          status: 'success',
          message: 'Connection restored successfully',
          userDisplayName: result.user_display_name,
          activityLevel: result.activity_level
        });
        
        setExistingConnection(prev => ({ ...prev, isConnected: true }));
      } else {
        setConnectionStatus({
          status: 'error',
          message: result.message || 'Connection test failed'
        });
      }
    } catch (error: any) {
      setConnectionStatus({
        status: 'error',
        message: error.detail || 'Connection test failed'
      });
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            {onBack && (
              <button 
                onClick={onBack}
                className="p-1 hover:bg-blue-500 rounded"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
            )}
            <Shield className="w-8 h-8" />
            <div>
              <h1 className="text-2xl font-bold">Garmin Connect Configuration</h1>
              <p className="text-blue-100">Connect your Garmin account for real training data</p>
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Loading existing connection */}
        {loadingExisting && (
          <div className="flex items-center justify-center py-8">
            <Loader className="w-6 h-6 animate-spin mr-2" />
            <span>Loading existing connection...</span>
          </div>
        )}

        {/* Existing connection status */}
        {!loadingExisting && existingConnection && (
          <div className={`p-4 rounded-lg border ${
            existingConnection.isConnected 
              ? 'bg-green-50 border-green-200' 
              : 'bg-yellow-50 border-yellow-200'
          }`}>
            <div className="flex items-start justify-between">
              <div className="flex items-center space-x-2">
                {existingConnection.isConnected ? (
                  <CheckCircle className="w-5 h-5 text-green-500" />
                ) : (
                  <AlertTriangle className="w-5 h-5 text-yellow-500" />
                )}
                <div>
                  <h3 className="font-medium">
                    {existingConnection.isConnected ? 'Connected Account' : 'Existing Configuration'}
                  </h3>
                  <p className="text-sm text-gray-600">
                    Email: {existingConnection.email}
                  </p>
                  {existingConnection.lastSync && (
                    <p className="text-xs text-gray-500">
                      Last sync: {new Date(existingConnection.lastSync).toLocaleString()}
                    </p>
                  )}
                </div>
              </div>
              {!existingConnection.isConnected && (
                <button
                  onClick={retestConnection}
                  disabled={connectionStatus.status === 'testing'}
                  className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                >
                  <RefreshCw className={`w-4 h-4 ${connectionStatus.status === 'testing' ? 'animate-spin' : ''}`} />
                  <span>Test</span>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Info Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <Info className="w-5 h-5 text-blue-500 mt-0.5" />
            <div className="text-sm">
              <h4 className="font-medium text-blue-900">Why Connect Garmin?</h4>
              <ul className="mt-2 space-y-1 text-blue-800">
                <li>• Access your real training history and performance data</li>
                <li>• Get personalized AI analysis based on your actual workouts</li>
                <li>• Receive training plans tailored to your fitness level</li>
                <li>• Track progress with accurate metrics and recovery data</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Configuration Form */}
        <form onSubmit={handleSubmit(testConnection)} className="space-y-4">
          <h3 className="text-lg font-semibold">Garmin Connect Credentials</h3>
          
          <div className="grid grid-cols-1 gap-4">
            <Input
              label="Garmin Connect Email"
              type="email"
              placeholder="your-email@example.com"
              error={errors.email?.message}
              {...form.register('email')}
            />

            <div className="relative">
              <Input
                label="Garmin Connect Password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Your Garmin Connect password"
                error={errors.password?.message}
                {...form.register('password')}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-8 text-gray-400 hover:text-gray-600"
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          </div>

          {/* Test Connection Button */}
          <button
            type="submit"
            disabled={!isValid || connectionStatus.status === 'testing'}
            className={`w-full py-3 px-4 rounded-lg font-medium flex items-center justify-center space-x-2 ${
              !isValid || connectionStatus.status === 'testing'
                ? 'bg-gray-200 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700'
            }`}
          >
            {connectionStatus.status === 'testing' ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                <span>Testing Connection...</span>
              </>
            ) : (
              <>
                <Shield className="w-5 h-5" />
                <span>Test Connection</span>
              </>
            )}
          </button>
        </form>

        {/* Connection Result */}
        {connectionStatus.status !== 'idle' && connectionStatus.status !== 'testing' && (
          <div className={`p-4 rounded-lg border ${
            connectionStatus.status === 'success' 
              ? 'bg-green-50 border-green-200' 
              : 'bg-red-50 border-red-200'
          }`}>
            <div className="flex items-start space-x-2">
              {connectionStatus.status === 'success' ? (
                <CheckCircle className="w-5 h-5 text-green-500" />
              ) : (
                <XCircle className="w-5 h-5 text-red-500" />
              )}
              <div className="flex-1">
                <h4 className={`font-medium ${
                  connectionStatus.status === 'success' ? 'text-green-800' : 'text-red-800'
                }`}>
                  {connectionStatus.status === 'success' ? 'Connection Successful!' : 'Connection Failed'}
                </h4>
                <p className={`text-sm mt-1 ${
                  connectionStatus.status === 'success' ? 'text-green-700' : 'text-red-700'
                }`}>
                  {connectionStatus.message}
                </p>
                {connectionStatus.userDisplayName && (
                  <div className="mt-2 text-sm text-green-700">
                    <p><strong>Welcome:</strong> {connectionStatus.userDisplayName}</p>
                    {connectionStatus.activityLevel && (
                      <p><strong>Activity Level:</strong> {connectionStatus.activityLevel}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Security Notice */}
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <Shield className="w-5 h-5 text-gray-500 mt-0.5" />
            <div className="text-sm text-gray-700">
              <h4 className="font-medium">Security & Privacy</h4>
              <ul className="mt-2 space-y-1">
                <li>• Your credentials are encrypted and stored securely</li>
                <li>• We only access your training data for analysis</li>
                <li>• You can revoke access at any time</li>
                <li>• Your data is never shared with third parties</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Requirements */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-start space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500 mt-0.5" />
            <div className="text-sm text-yellow-800">
              <h4 className="font-medium">Important Requirements</h4>
              <ul className="mt-2 space-y-1">
                <li>• Use your regular Garmin Connect credentials (not app passwords)</li>
                <li>• Two-factor authentication should be disabled for API access</li>
                <li>• Ensure your account has recent activity data</li>
                <li>• Connection may take 30-60 seconds to establish</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GarminConnectConfig;