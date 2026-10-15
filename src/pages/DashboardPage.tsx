import React, { useState } from 'react'
import { Link } from 'react-router-dom'

const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview')
  
  // Mock data
  const recentSearches = [
    { id: 1, origin: 'Paris', destination: 'Lyon', date: '2023-06-15' },
    { id: 2, origin: 'Marseille', destination: 'Nice', date: '2023-06-10' },
    { id: 3, origin: 'Bordeaux', destination: 'Paris', date: '2023-06-05' }
  ]
  
  const favoriteRoutes = [
    { id: 1, title: 'Paris to Lyon', duration: '3h 20m', price: '€45' },
    { id: 2, title: 'Marseille to Nice', duration: '2h 45m', price: '€38' }
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8 text-gray-900 dark:text-white">Dashboard</h1>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="flex space-x-8 px-6">
              {['overview', 'searches', 'favorites'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
                  }`}
                >
                  {tab.charAt(0).toUpperCase() + tab.slice(1)}
                </button>
              ))}
            </nav>
          </div>
          
          <div className="p-6">
            {activeTab === 'overview' && (
              <div>
                <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Your Travel Overview</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-blue-50 dark:bg-blue-900 rounded-lg p-6">
                    <p className="text-sm text-blue-800 dark:text-blue-200">Total Searches</p>
                    <p className="text-3xl font-bold text-blue-600 dark:text-blue-400">12</p>
                  </div>
                  
                  <div className="bg-green-50 dark:bg-green-900 rounded-lg p-6">
                    <p className="text-sm text-green-800 dark:text-green-200">Favorite Routes</p>
                    <p className="text-3xl font-bold text-green-600 dark:text-green-400">5</p>
                  </div>
                  
                  <div className="bg-purple-50 dark:bg-purple-900 rounded-lg p-6">
                    <p className="text-sm text-purple-800 dark:text-purple-200">Saved Trips</p>
                    <p className="text-3xl font-bold text-purple-600 dark:text-purple-400">3</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  <div>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Recent Searches</h3>
                    <ul className="space-y-3">
                      {recentSearches.map((search) => (
                        <li key={search.id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                          <div>
                            <p className="font-medium text-gray-900 dark:text-white">{search.origin} → {search.destination}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-300">{search.date}</p>
                          </div>
                          <button className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                            View Details
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Favorite Routes</h3>
                    <ul className="space-y-3">
                      {favoriteRoutes.map((route) => (
                        <li key={route.id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                          <div>
                            <p className="font-medium text-gray-900 dark:text-white">{route.title}</p>
                            <p className="text-sm text-gray-600 dark:text-gray-300">{route.duration} • {route.price}</p>
                          </div>
                          <button className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                            View Details
                          </button>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}
            
            {activeTab === 'searches' && (
              <div>
                <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Your Search History</h2>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead className="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Origin</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Destination</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                      {recentSearches.map((search) => (
                        <tr key={search.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{search.origin}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{search.destination}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-300">{search.date}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm">
                            <button className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 mr-3">
                              View Details
                            </button>
                            <button className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-300">
                              Re-search
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            
            {activeTab === 'favorites' && (
              <div>
                <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Favorite Routes</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {favoriteRoutes.map((route) => (
                    <div key={route.id} className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6">
                      <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">{route.title}</h3>
                      <p className="text-gray-600 dark:text-gray-300 mb-4">{route.duration} • {route.price}</p>
                      <div className="flex space-x-3">
                        <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors">
                          Book Now
                        </button>
                        <button className="bg-gray-200 hover:bg-gray-300 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-800 dark:text-gray-200 px-4 py-2 rounded-md text-sm font-medium transition-colors">
                          Remove
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
        
        <div className="text-center">
          <Link 
            to="/search" 
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium transition-colors shadow-md"
          >
            Start New Search
          </Link>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
