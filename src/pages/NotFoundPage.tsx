import React from 'react'
import { Link } from 'react-router-dom'

const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
      <div className="max-w-md p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg text-center">
        <h1 className="text-6xl font-bold text-blue-600 dark:text-blue-400 mb-4">404</h1>
        <h2 className="text-2xl font-bold mb-4 text-gray-900 dark:text-white">Page Not Found</h2>
        <p className="text-gray-600 dark:text-gray-300 mb-8">
          Sorry, the page you're looking for doesn't exist or has been moved.
        </p>
        <div className="space-y-4">
          <Link 
            to="/" 
            className="block bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium transition-colors shadow-md"
          >
            Go Home
          </Link>
          <button 
            onClick={() => window.history.back()}
            className="block w-full bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 px-6 py-3 rounded-md font-medium transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    </div>
  )
}

export default NotFoundPage
