'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/contexts/AuthContext'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function Home() {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const [apiStatus, setApiStatus] = useState<{
    status: string
    data: any
  }>({ status: 'loading', data: null })

  useEffect(() => {
    // If user is already authenticated, redirect to dashboard
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard')
      return
    }

    const checkAPI = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'https://garmin-ai-coach-production.up.railway.app'}/health`
        )
        const data = await response.json()
        setApiStatus({ status: 'connected', data })
      } catch (error) {
        console.error('API connection failed:', error)
        setApiStatus({ status: 'error', data: null })
      }
    }

    checkAPI()
  }, [isAuthenticated, isLoading, router])

  // Show loading spinner while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <main className="min-h-screen p-8 bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            🏃‍♂️ Garmin AI Coach
          </h1>
          <p className="text-xl text-gray-600">
            AI-powered triathlon coaching platform with Garmin Connect integration
          </p>
        </header>

        <div className="grid md:grid-cols-2 gap-8">
          {/* API Status Card */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              🔌 Backend API Status
            </h2>
            <div className="space-y-2">
              {apiStatus.status === 'loading' && (
                <div className="flex items-center space-x-2">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                  <span className="text-gray-600">Connecting...</span>
                </div>
              )}
              {apiStatus.status === 'connected' && (
                <div>
                  <div className="flex items-center space-x-2 mb-3">
                    <span className="w-3 h-3 bg-green-500 rounded-full"></span>
                    <span className="text-green-700 font-medium">Connected</span>
                  </div>
                  <div className="bg-gray-50 rounded p-3 text-sm">
                    <pre>{JSON.stringify(apiStatus.data, null, 2)}</pre>
                  </div>
                </div>
              )}
              {apiStatus.status === 'error' && (
                <div className="flex items-center space-x-2">
                  <span className="w-3 h-3 bg-red-500 rounded-full"></span>
                  <span className="text-red-700 font-medium">Connection Failed</span>
                </div>
              )}
            </div>
          </div>

          {/* Features Card */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-semibold mb-4 text-gray-800">
              🚀 Features Coming Soon
            </h2>
            <ul className="space-y-2 text-gray-600">
              <li className="flex items-center space-x-2">
                <span className="text-blue-500">•</span>
                <span>Garmin Connect Integration</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-blue-500">•</span>
                <span>AI Training Analysis</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-blue-500">•</span>
                <span>Personalized Coaching Plans</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-blue-500">•</span>
                <span>Performance Insights</span>
              </li>
              <li className="flex items-center space-x-2">
                <span className="text-blue-500">•</span>
                <span>Multi-Agent AI System</span>
              </li>
            </ul>
          </div>
        </div>

        <div className="mt-12 text-center">
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h3 className="text-lg font-semibold mb-2 text-gray-800">
              Get Started with Garmin AI Coach
            </h3>
            <p className="text-gray-600 mb-6">
              Ready to optimize your triathlon training with AI-powered insights?
            </p>
            <div className="flex justify-center space-x-4">
              <Link 
                href="/auth/register"
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Create Account
              </Link>
              <Link 
                href="/auth/login"
                className="bg-gray-100 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-200 transition-colors font-medium"
              >
                Sign In
              </Link>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="text-lg font-semibold mb-2 text-gray-800">
              Development Status
            </h3>
            <p className="text-gray-600 mb-4">
              Phase 1: Authentication & User Management - ✅ Complete<br />
              Phase 2: Training Profile Forms - 🔄 Coming Next
            </p>
            <div className="flex justify-center space-x-4">
              <a 
                href={`${process.env.NEXT_PUBLIC_API_URL || 'https://garmin-ai-coach-production.up.railway.app'}/docs`}
                target="_blank"
                rel="noopener noreferrer"
                className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700 transition-colors"
              >
                View API Docs
              </a>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}