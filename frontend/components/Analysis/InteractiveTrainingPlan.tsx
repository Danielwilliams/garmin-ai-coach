'use client';

import React, { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  Target,
  Activity,
  Heart,
  Zap,
  Download,
  CheckCircle,
  Circle,
  AlertTriangle,
  Info,
  ChevronDown,
  ChevronRight,
  MapPin,
  Timer
} from 'lucide-react';

interface TrainingSession {
  id: string;
  day: string;
  date: string;
  title: string;
  type: 'endurance' | 'recovery' | 'threshold' | 'vo2max' | 'strength' | 'rest';
  duration: string;
  intensity: string;
  tss: number;
  description: string;
  objectives: string[];
  notes?: string;
  adaptationNote?: string;
  completed?: boolean;
}

interface TrainingWeek {
  weekNumber: number;
  weekTitle: string;
  dateRange: string;
  focus: string;
  totalTss: string;
  sessions: TrainingSession[];
}

interface TrainingPhase {
  phase: string;
  weeks: string;
  focus: string;
  description: string;
}

interface InteractiveTrainingPlanProps {
  weeklyPlan: any;
  analysisId: string;
}

const InteractiveTrainingPlan: React.FC<InteractiveTrainingPlanProps> = ({ 
  weeklyPlan, 
  analysisId 
}) => {
  const [selectedWeek, setSelectedWeek] = useState<number>(1);
  const [completedSessions, setCompletedSessions] = useState<Set<string>>(new Set());
  const [expandedSession, setExpandedSession] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'weeks' | 'phases'>('overview');

  // Parse the weekly plan data (this would come from AI-generated structured data)
  const trainingData = parseTrainingPlan(weeklyPlan);

  const handleSessionComplete = (sessionId: string) => {
    const newCompleted = new Set(completedSessions);
    if (newCompleted.has(sessionId)) {
      newCompleted.delete(sessionId);
    } else {
      newCompleted.add(sessionId);
    }
    setCompletedSessions(newCompleted);
  };

  const getIntensityColor = (type: string) => {
    const colors = {
      endurance: 'bg-blue-100 text-blue-800',
      recovery: 'bg-green-100 text-green-800',
      threshold: 'bg-orange-100 text-orange-800',
      vo2max: 'bg-red-100 text-red-800',
      strength: 'bg-purple-100 text-purple-800',
      rest: 'bg-gray-100 text-gray-800'
    };
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const getZoneColor = (zone: string) => {
    const zoneColors = {
      'Z1': 'bg-green-100 text-green-700',
      'Z2': 'bg-blue-100 text-blue-700',
      'Z3': 'bg-yellow-100 text-yellow-700',
      'Z4': 'bg-orange-100 text-orange-700',
      'Z5': 'bg-red-100 text-red-700'
    };
    return zoneColors[zone as keyof typeof zoneColors] || 'bg-gray-100 text-gray-700';
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg p-6">
        <h1 className="text-2xl font-bold mb-2">Interactive Training Plan</h1>
        <p className="text-purple-100">Your personalized AI-generated training program with interactive tracking</p>
      </div>

      {/* Tabs */}
      <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
        {[
          { id: 'overview', name: 'Plan Overview', icon: Target },
          { id: 'weeks', name: 'Weekly Breakdown', icon: Calendar },
          { id: 'phases', name: 'Training Phases', icon: Activity }
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 flex items-center justify-center px-4 py-2 rounded-md font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-white text-purple-600 shadow-sm'
                  : 'text-gray-600 hover:text-purple-600'
              }`}
            >
              <Icon className="w-4 h-4 mr-2" />
              {tab.name}
            </button>
          );
        })}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Plan Summary */}
          <div className="lg:col-span-2 bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">Plan Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">4</div>
                <div className="text-sm text-gray-600">Weeks</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">24</div>
                <div className="text-sm text-gray-600">Sessions</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">1,200</div>
                <div className="text-sm text-gray-600">Total TSS</div>
              </div>
              <div className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">15h</div>
                <div className="text-sm text-gray-600">Avg/Week</div>
              </div>
            </div>
          </div>

          {/* Training Zones */}
          <div className="bg-white rounded-lg border p-6">
            <h3 className="text-lg font-semibold mb-4">Training Zones</h3>
            <div className="space-y-2">
              {[
                { zone: 'Z1', name: 'Recovery', range: '<55% FTP', color: 'green' },
                { zone: 'Z2', name: 'Endurance', range: '56-75% FTP', color: 'blue' },
                { zone: 'Z3', name: 'Tempo', range: '76-90% FTP', color: 'yellow' },
                { zone: 'Z4', name: 'Threshold', range: '91-105% FTP', color: 'orange' },
                { zone: 'Z5', name: 'VO2max', range: '106-120% FTP', color: 'red' }
              ].map((zone) => (
                <div key={zone.zone} className="flex items-center justify-between p-2 rounded">
                  <div className="flex items-center">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getZoneColor(zone.zone)}`}>
                      {zone.zone}
                    </span>
                    <span className="ml-2 font-medium">{zone.name}</span>
                  </div>
                  <span className="text-sm text-gray-600">{zone.range}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Weekly Breakdown Tab */}
      {activeTab === 'weeks' && (
        <div>
          {/* Week Selector */}
          <div className="flex space-x-2 mb-6 overflow-x-auto pb-2">
            {trainingData.weeks.map((week) => (
              <button
                key={week.weekNumber}
                onClick={() => setSelectedWeek(week.weekNumber)}
                className={`flex-shrink-0 px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedWeek === week.weekNumber
                    ? 'bg-purple-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Week {week.weekNumber}
              </button>
            ))}
          </div>

          {/* Selected Week Content */}
          {trainingData.weeks.map((week) => 
            week.weekNumber === selectedWeek && (
              <div key={week.weekNumber} className="space-y-6">
                {/* Week Header */}
                <div className="bg-white rounded-lg border p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-xl font-bold">{week.weekTitle}</h2>
                      <p className="text-gray-600">{week.dateRange}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-sm text-gray-600">Total Load</div>
                      <div className="text-lg font-semibold text-purple-600">{week.totalTss}</div>
                    </div>
                  </div>
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <div className="flex items-center">
                      <Target className="w-5 h-5 text-yellow-600 mr-2" />
                      <span className="font-medium text-yellow-800">Week Focus: {week.focus}</span>
                    </div>
                  </div>
                </div>

                {/* Training Sessions */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {week.sessions.map((session) => (
                    <div 
                      key={session.id} 
                      className={`bg-white rounded-lg border transition-all duration-200 hover:shadow-md ${
                        completedSessions.has(session.id) ? 'bg-green-50 border-green-200' : ''
                      }`}
                    >
                      {/* Session Header */}
                      <div className="p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center">
                            <button
                              onClick={() => handleSessionComplete(session.id)}
                              className={`mr-3 p-1 rounded-full transition-colors ${
                                completedSessions.has(session.id)
                                  ? 'text-green-600 hover:text-green-700'
                                  : 'text-gray-400 hover:text-green-600'
                              }`}
                            >
                              {completedSessions.has(session.id) ? 
                                <CheckCircle className="w-5 h-5" /> : 
                                <Circle className="w-5 h-5" />
                              }
                            </button>
                            <div>
                              <div className="font-medium">{session.day}, {session.date}</div>
                              <div className="text-sm text-gray-600">{session.title}</div>
                            </div>
                          </div>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getIntensityColor(session.type)}`}>
                            {session.type}
                          </span>
                        </div>

                        {/* Session Details */}
                        <div className="space-y-2 mb-3">
                          <div className="flex items-center text-sm text-gray-600">
                            <Clock className="w-4 h-4 mr-1" />
                            {session.duration}
                          </div>
                          <div className="flex items-center text-sm text-gray-600">
                            <Zap className="w-4 h-4 mr-1" />
                            {session.intensity}
                          </div>
                          <div className="flex items-center text-sm text-gray-600">
                            <Activity className="w-4 h-4 mr-1" />
                            {session.tss} TSS
                          </div>
                        </div>

                        <p className="text-sm text-gray-700 mb-3">{session.description}</p>

                        {/* Expandable Details */}
                        <button
                          onClick={() => setExpandedSession(
                            expandedSession === session.id ? null : session.id
                          )}
                          className="flex items-center text-sm text-purple-600 hover:text-purple-700"
                        >
                          {expandedSession === session.id ? 
                            <ChevronDown className="w-4 h-4 mr-1" /> : 
                            <ChevronRight className="w-4 h-4 mr-1" />
                          }
                          {expandedSession === session.id ? 'Hide' : 'Show'} Details
                        </button>

                        {/* Expanded Content */}
                        {expandedSession === session.id && (
                          <div className="mt-3 pt-3 border-t space-y-3">
                            <div>
                              <h4 className="font-medium text-gray-900 mb-2">Objectives:</h4>
                              <ul className="list-disc list-inside text-sm text-gray-700 space-y-1">
                                {session.objectives.map((objective, idx) => (
                                  <li key={idx}>{objective}</li>
                                ))}
                              </ul>
                            </div>
                            
                            {session.adaptationNote && (
                              <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                                <div className="flex items-start">
                                  <AlertTriangle className="w-4 h-4 text-yellow-600 mr-2 mt-0.5 flex-shrink-0" />
                                  <div>
                                    <h4 className="font-medium text-yellow-800 mb-1">Adaptation Note:</h4>
                                    <p className="text-sm text-yellow-700">{session.adaptationNote}</p>
                                  </div>
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )
          )}
        </div>
      )}

      {/* Training Phases Tab */}
      {activeTab === 'phases' && (
        <div className="space-y-6">
          {trainingData.phases.map((phase, index) => (
            <div key={index} className="bg-white rounded-lg border p-6">
              <div className="flex items-center mb-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white font-bold mr-3 ${
                  index === 0 ? 'bg-green-600' : 
                  index === 1 ? 'bg-blue-600' : 
                  index === 2 ? 'bg-orange-600' : 'bg-purple-600'
                }`}>
                  {index + 1}
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{phase.phase}</h3>
                  <p className="text-gray-600">{phase.weeks}</p>
                </div>
              </div>
              <p className="text-gray-700 mb-2"><strong>Focus:</strong> {phase.focus}</p>
              <p className="text-gray-700">{phase.description}</p>
            </div>
          ))}
        </div>
      )}

      {/* Progress Summary */}
      <div className="bg-white rounded-lg border p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Training Progress</h3>
          <div className="text-sm text-gray-600">
            {completedSessions.size} of {trainingData.weeks.reduce((total, week) => total + week.sessions.length, 0)} sessions completed
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-green-600 h-2 rounded-full transition-all duration-300"
            style={{ 
              width: `${(completedSessions.size / trainingData.weeks.reduce((total, week) => total + week.sessions.length, 0)) * 100}%` 
            }}
          />
        </div>
      </div>
    </div>
  );
};

// Helper function to parse training plan data
function parseTrainingPlan(weeklyPlan: any) {
  // This would parse the AI-generated training plan into structured data
  // For now, returning mock structured data that demonstrates the format
  
  return {
    phases: [
      {
        phase: "Phase 1: Stabilization",
        weeks: "Weeks 1-4 | Jan 7 – Feb 3",
        focus: "Build consistency floor (4-5 days/week), eliminate training gaps",
        description: "Build consistency floor (4-5 days/week), eliminate training gaps, target chronic load 270→320. Sleep prioritization: >6.5h avg, zero-REM elimination."
      },
      {
        phase: "Phase 2: Aerobic Base", 
        weeks: "Weeks 5-9 | Feb 4 – Mar 10",
        focus: "Expand aerobic capacity, extend rides to 3.5-4hr",
        description: "Expand aerobic capacity, extend rides to 3.5-4hr, address VO2max plateau. Chronic load: 320→380 with 3:1 recovery cycles."
      },
      {
        phase: "Phase 3: Build",
        weeks: "Weeks 10-13 | Mar 11 – Apr 8", 
        focus: "Race-specific intensity for Sprint Series + Sasquatch",
        description: "Race-specific intensity for Sprint Series + Sasquatch. VO2max intervals 2x/week, peak chronic load 380-400."
      }
    ],
    weeks: [
      {
        weekNumber: 1,
        weekTitle: "Stabilization + Recovery Consolidation",
        dateRange: "Jan 7-13",
        focus: "ACWR Reduction & Sleep Quality",
        totalTss: "220-280 TSS",
        sessions: [
          {
            id: "w1-wed",
            day: "WED",
            date: "Jan 7",
            title: "Active Recovery",
            type: "recovery" as const,
            duration: "45min",
            intensity: "Z1-Z2 (HR <140)",
            tss: 25,
            description: "45min outdoor easy spin, Z1-Z2 cap (HR <140)",
            objectives: ["Flush residual fatigue from Jan 6", "Maintain movement patterns"],
            adaptationNote: "If sleep <6h → reduce to 30min or rest. If RHR >52 → complete rest."
          },
          {
            id: "w1-thu", 
            day: "THU",
            date: "Jan 8",
            title: "Endurance Foundation",
            type: "endurance" as const,
            duration: "90min",
            intensity: "Z2 steady (IF 0.68-0.72)",
            tss: 75,
            description: "90min outdoor MTB, Z2 steady with technical skills",
            objectives: ["Re-establish weekly long ride rhythm", "Technical skills practice", "Aerobic base maintenance"],
            adaptationNote: "If fatigued → reduce to 75min, stay Z2. If sleep score <60 → postpone to Friday."
          },
          {
            id: "w1-fri",
            day: "FRI", 
            date: "Jan 9",
            title: "Rest / Mobility",
            type: "rest" as const,
            duration: "20min",
            intensity: "Easy spin + stretching",
            tss: 10,
            description: "OFF or 20min easy spin + stretching",
            objectives: ["Protect adaptation", "Prioritize sleep quality"],
            adaptationNote: "If restless sleep (>80 movements) → add 10min cold plunge."
          },
          {
            id: "w1-sat",
            day: "SAT",
            date: "Jan 10", 
            title: "Long Endurance",
            type: "endurance" as const,
            duration: "2.5-3hr",
            intensity: "Z2-low Z3 (IF 0.70-0.75)",
            tss: 170,
            description: "2.5-3hr outdoor MTB, Z2-low Z3 with climbing",
            objectives: ["Aerobic base expansion", "Duration tolerance for Royal Gorge", "Climbing practice"],
            adaptationNote: "If RHR >51 → cap at 2hr, strict Z2. Hydrate 0.75L (mandatory log)."
          },
          {
            id: "w1-sun",
            day: "SUN",
            date: "Jan 11",
            title: "Active Recovery", 
            type: "recovery" as const,
            duration: "60min",
            intensity: "Z1 only (HR <130)",
            tss: 30,
            description: "60min outdoor easy spin, Z1 only",
            objectives: ["Facilitate recovery", "Maintain consistency habit"],
            adaptationNote: "If legs heavy → reduce to 40min or 15min walk."
          },
          {
            id: "w1-tue",
            day: "TUE",
            date: "Jan 13",
            title: "Threshold Block",
            type: "threshold" as const, 
            duration: "75min",
            intensity: "Z4 @ IF 0.88-0.92",
            tss: 95,
            description: "75min: 15' WU → 3x(12' Z4 @ IF 0.88-0.92, 5' easy) → 10' CD",
            objectives: ["Quality intensity within recovery window", "Threshold maintenance", "Power consistency"],
            adaptationNote: "If sleep <6h or RHR >52 → convert to 60min Z2. Hydrate 0.5L."
          }
        ]
      }
      // Additional weeks would follow the same pattern...
    ]
  };
}

export default InteractiveTrainingPlan;