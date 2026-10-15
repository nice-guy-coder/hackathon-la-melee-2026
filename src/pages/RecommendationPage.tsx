import React, { useState } from 'react'
import LoadingSpinner from '../components/LoadingSpinner'

const RecommendationPage: React.FC = () => {
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

  const recommendations = [
    {
      id: 1,
      title: 'Paris to Lyon',
      description: 'Scenic route through the French countryside with comfortable seating',
      duration: '3h 20m',
      price: '€45',
      image: 'https://images.unsplash.com/photo-1507608610059-7a0d1c1b0f0e?w=400&h=200&fit=crop'
    },
    {
      id: 2,
      title: 'Marseille to Nice',
      description: 'Coastal route with stunning Mediterranean views',
      duration: '2h 45m',
      price: '€38',
      image: 'https://images.unsplash.com/photo-1507608610059-7a0d1c1b0f0e?w=400&h=200&fit=crop'
    },
    {
      id: 3,
      title: 'Bordeaux to Paris',
      description: 'Classic route through historic French towns',
      duration: '4h 10m',
      price: '€52',
      image: 'https://images.unsplash.com/photo-1507608610059-7a0d1c1b0f0e?w=400&h=200&fit=crop'
    },
    {
      id: 4,
      title: 'Toulouse to Marseille',
      description: 'Route through the beautiful Languedoc region',
      duration: '3h 50m',
      price: '€41',
      image: 'https://images.unsplash.com/photo-1507608610059-7a0d1c1b0f0e?w=400&h=200&fit=crop'
    }
  ]

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-900 dark:text-white">Recommended Routes</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {recommendations.map((route) => (
            <div 
              key={route.id} 
              className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
            >
              <img 
                src={route.image} 
                alt={route.title} 
                className="w-full h-48 object-cover"
              />
              <div className="p-6">
                <h2 className="text-xl font-bold mb-2 text-gray-900 dark:text-white">{route.title}</h2>
                <p className="text-gray-600 dark:text-gray-300 mb-4">{route.description}</p>
                <div className="flex justify-between items-center mb-4">
                  <span className="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-full text-sm font-medium">
                    {route.duration}
                  </span>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">{route.price}</span>
                </div>
                <button className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md font-medium transition-colors">
                  View Details
                </button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-12 text-center">
          <button className="bg-white dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 text-blue-600 dark:text-blue-400 px-6 py-3 rounded-md font-medium transition-colors shadow-md">
            Load More Recommendations
          </button>
        </div>
      </div>
    </div>
  )
}

export default RecommendationPage
