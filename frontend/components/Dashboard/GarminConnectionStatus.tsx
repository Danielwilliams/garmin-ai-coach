'use client';

import React, { useState, useEffect } from 'react';
import { 
  Shield, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Settings, 
  RefreshCw,
  Activity,
  Clock
} from 'lucide-react';
import { trainingProfileAPI } from '@/lib/api';

interface GarminConnection {
  email: string;
  isConnected: boolean;
  lastSync?: string;
  userDisplayName?: string;
  activityLevel?: string;
  syncError?: string;
  totalActivities?: number;
}

interface GarminConnectionStatusProps {
  onConfigureClick: () => void;
  className?: string;
}

const GarminConnectionStatus: React.FC<GarminConnectionStatusProps> = ({
  onConfigureClick,
  className = ''
}) => {
  const [connections, setConnections] = useState<GarminConnection[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const loadConnections = async () => {
    try {
      // Get all training profiles to check for Garmin connections
      const profiles = await trainingProfileAPI.getProfiles();
      
      const garminConnections: GarminConnection[] = profiles
        .filter((profile: any) => profile.garmin_email)
        .map((profile: any) => ({
          email: profile.garmin_email,
          isConnected: profile.garmin_is_connected || false,
          lastSync: profile.last_sync_date,
          userDisplayName: profile.athlete_name,
          activityLevel: profile.activity_level,
          syncError: profile.sync_error,
          totalActivities: profile.total_activities
        }));

      setConnections(garminConnections);
    } catch (error) {
      console.error('Failed to load Garmin connections:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadConnections();
  };

  useEffect(() => {
    loadConnections();
  }, []);

  const getConnectionIcon = (connection: GarminConnection) => {
    if (connection.isConnected) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    } else if (connection.syncError) {
      return <XCircle className="w-5 h-5 text-red-500" />;
    } else {
      return <AlertTriangle className="w-5 h-5 text-yellow-500" />;
    }
  };

  const getConnectionStatus = (connection: GarminConnection) => {
    if (connection.isConnected) {
      return {
        text: 'Connected',
        color: 'text-green-700',
        bgColor: 'bg-green-50'
      };
    } else if (connection.syncError) {
      return {
        text: 'Connection Error',
        color: 'text-red-700',
        bgColor: 'bg-red-50'
      };
    } else {
      return {
        text: 'Not Connected',
        color: 'text-yellow-700',
        bgColor: 'bg-yellow-50'
      };
    }
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
        <div className="flex items-center space-x-3">
          <Shield className="w-6 h-6 text-gray-400" />
          <div>
            <h3 className="text-lg font-semibold">Garmin Connect</h3>
            <p className="text-sm text-gray-600">Loading connection status...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm border border-gray-200 ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Shield className="w-6 h-6 text-blue-600" />
            <div>
              <h3 className="text-lg font-semibold">Garmin Connect</h3>
              <p className="text-sm text-gray-600">Training data synchronization</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={handleRefresh}
              disabled={refreshing}
              className="p-2 text-gray-500 hover:text-gray-700 disabled:opacity-50 rounded-lg hover:bg-gray-100"
              title="Refresh connection status"
            >
              <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onConfigureClick}
              className="flex items-center space-x-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Settings className="w-4 h-4" />
              <span>Configure</span>
            </button>
          </div>
        </div>
      </div>

      {/* Connection List */}
      <div className="p-6">
        {connections.length === 0 ? (
          <div className="text-center py-8">
            <Shield className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-gray-900 mb-2">No Garmin Connections</h4>
            <p className="text-gray-600 mb-4">
              Connect your Garmin account to sync training data and get personalized analysis.
            </p>
            <button
              onClick={onConfigureClick}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              <Shield className="w-4 h-4" />
              <span>Connect Garmin</span>
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {connections.map((connection, index) => {
              const status = getConnectionStatus(connection);
              
              return (
                <div key={index} className={`p-4 rounded-lg border ${
                  connection.isConnected 
                    ? 'border-green-200 bg-green-50' 
                    : connection.syncError
                    ? 'border-red-200 bg-red-50'
                    : 'border-yellow-200 bg-yellow-50'
                }`}>
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-3">
                      {getConnectionIcon(connection)}
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-1">
                          <h4 className="font-medium text-gray-900">{connection.email}</h4>
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${status.bgColor} ${status.color}`}>
                            {status.text}
                          </span>
                        </div>
                        
                        {connection.userDisplayName && (
                          <p className="text-sm text-gray-600 mb-1">
                            Account: {connection.userDisplayName}
                          </p>
                        )}
                        
                        {connection.activityLevel && (
                          <div className="flex items-center space-x-1 text-sm text-gray-600 mb-1">
                            <Activity className="w-3 h-3" />
                            <span>Activity Level: {connection.activityLevel}</span>
                          </div>
                        )}
                        
                        {connection.lastSync && (
                          <div className="flex items-center space-x-1 text-sm text-gray-600 mb-1">
                            <Clock className="w-3 h-3" />
                            <span>Last sync: {new Date(connection.lastSync).toLocaleDateString()}</span>
                          </div>
                        )}
                        
                        {connection.totalActivities !== undefined && (
                          <p className="text-sm text-gray-600">
                            Activities synced: {connection.totalActivities}
                          </p>
                        )}
                        
                        {connection.syncError && (
                          <p className="text-sm text-red-600 mt-2">
                            Error: {connection.syncError}
                          </p>
                        )}
                      </div>
                    </div>
                    
                    <button
                      onClick={onConfigureClick}
                      className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                    >
                      Manage
                    </button>
                  </div>
                </div>
              );
            })}
            
            {/* Add Another Connection */}
            <button
              onClick={onConfigureClick}
              className="w-full p-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:text-gray-700 hover:border-gray-400 transition-colors"
            >
              <div className="flex items-center justify-center space-x-2">
                <Shield className="w-5 h-5" />
                <span>Add Another Garmin Account</span>
              </div>
            </button>
          </div>
        )}
      </div>

      {/* Quick Stats */}
      {connections.length > 0 && (
        <div className="bg-gray-50 px-6 py-4 border-t border-gray-200">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-green-600">
                {connections.filter(c => c.isConnected).length}
              </div>
              <div className="text-sm text-gray-600">Connected</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-600">
                {connections.filter(c => c.syncError).length}
              </div>
              <div className="text-sm text-gray-600">Errors</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {connections.reduce((total, c) => total + (c.totalActivities || 0), 0)}
              </div>
              <div className="text-sm text-gray-600">Total Activities</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GarminConnectionStatus;