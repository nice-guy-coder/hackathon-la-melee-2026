import React from 'react'
import { Link } from 'react-router-dom'
import { useDarkMode } from '../contexts/DarkModeContext'

const Header: React.FC = () => {
  const { darkMode, toggleDarkMode } = useDarkMode()

  return (
    <header className="bg-white dark:bg-gray-800 shadow-md">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold text-blue-600 dark:text-blue-400">
          SNCF Explorer
        </Link>
        
        <nav className="hidden md:flex space-x-6">
          <Link to="/" className="hover:text-blue-500 transition-colors">Home</Link>
          <Link to="/search" className="hover:text-blue-500 transition-colors">Search</Link>
          <Link to="/recommendations" className="hover:text-blue-500 transition-colors">Recommendations</Link>
          <Link to="/compare" className="hover:text-blue-500 transition-colors">Compare</Link>
          <Link to="/favorites" className="hover:text-blue-500 transition-colors">Favorites</Link>
          <Link to="/dashboard" className="hover:text-blue-500 transition-colors">Dashboard</Link>
        </nav>
        
        <div className="flex items-center space-x-4">
          <button 
            onClick={toggleDarkMode}
            className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>
          
          <Link to="/dashboard" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors">
            Dashboard
          </Link>
        </div>
      </div>
    </header>
  )
}

export default Header
