import React, { useState } from 'react'
import LoadingSpinner from '../components/LoadingSpinner'

const ComparePage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(true)
  
  // Simulate loading data
  React.useEffect(() => {
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 1500)
    
    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <LoadingSpinner />
      </div>
    )
  }

  const routes = [
    {
      id: 1,
      title: 'Paris to Lyon',
      duration: '3h 20m',
      price: '€45',
      departure: '08:30',
      arrival: '11:50',
      stops: 2,
      image: 'https://images.unsplash.com/photo-1507608610059-7a0d1c1b0f0e?w=400&h=200&fit=crop'
    },
    {
      id: 2,
      title: 'Paris to Lyon',
      duration: '3h 45m',
      price: '€38',
      departure: '10:15',
      arrival: '14:00',
      stops: 1,
      image: 'https://images.unsplash.com/photo-1507608610059-7a0d1c1b0f0e?w=400&h=200&fit=crop'
    },
    {
      id: 3,
      title: 'Paris to Lyon',
      duration: '4h 10m',
      price: '€52',
      departure: '14:30',
      arrival: '18:40',
      stops: 3,
      image: 'https://images.unsplash.com/photo-1507608610059-7a0d1c1b0f0e?w=400&h=200&fit=crop'
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-900 dark:text-white">Compare Routes</h1>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 p-6 border-b border-gray-200 dark:border-gray-700">
            {routes.map((route) => (
              <div key={route.id} className="text-center">
                <h3 className="font-bold text-lg mb-2 text-gray-900 dark:text-white">{route.title}</h3>
                <img 
                  src={route.image} 
                  alt={route.title} 
                  className="w-full h-32 object-cover rounded-md mb-4"
                />
                <div className="space-y-2">
                  <p className="text-gray-600 dark:text-gray-300">
                    <span className="font-medium">Departure:</span> {route.departure}
                  </p>
                  <p className="text-gray-600 dark:text-gray-300">
                    <span className="font-medium">Arrival:</span> {route.arrival}
                  </p>
                  <p className="text-gray-600 dark:text-gray-300">
                    <span className="font-medium">Duration:</span> {route.duration}
                  </p>
                  <p className="text-gray-600 dark:text-gray-300">
                    <span className="font-medium">Stops:</span> {route.stops}
                  </p>
                  <p className="text-xl font-bold text-blue-600 dark:text-blue-400">{route.price}</p>
                </div>
              </div>
            ))}
          </div>
          
          <div className="p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Route Comparison</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Feature</th>
                    {routes.map((route) => (
                      <th key={route.id} className="px-6 py-3 text-center text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Route {route.id}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">Duration</td>
                    {routes.map((route) => (
                      <td key={route.id} className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500 dark:text-gray-300">
                        {route.duration}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">Price</td>
                    {routes.map((route) => (
                      <td key={route.id} className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500 dark:text-gray-300">
                        {route.price}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">Stops</td>
                    {routes.map((route) => (
                      <td key={route.id} className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500 dark:text-gray-300">
                        {route.stops}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">Departure Time</td>
                    {routes.map((route) => (
                      <td key={route.id} className="px-6 py-4 whitespace-nowrap text-sm text-center text-gray-500 dark:text-gray-300">
                        {route.departure}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        
        <div className="text-center">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium transition-colors shadow-md">
            Book Selected Route
          </button>
        </div>
      </div>
    </div>
  )
}

export default ComparePage
