import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'

const DestinationDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>()
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

  // Mock data for destination details
  const destination = {
    id: id || '1',
    name: 'Paris',
    description: 'The City of Light, Paris is known for its art, fashion, gastronomy, and culture. It is one of the world\'s most visited cities.',
    image: 'https://images.unsplash.com/photo-1502602898657-3e9179b08d30?w=800&h=400&fit=crop',
    attractions: [
      'Eiffel Tower',
      'Louvre Museum',
      'Notre-Dame Cathedral',
      'Champs-Élysées'
    ],
    weather: {
      temperature: '18°C',
      condition: 'Partly Cloudy'
    },
    travelTips: [
      'Visit the Louvre early in the morning to avoid crowds',
      'Take the metro for easy transportation around the city',
      'Try local cuisine at a traditional bistro',
      'Don\'t miss the Seine River cruise'
    ]
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-12">
      <div className="container mx-auto px-4">
        <button 
          onClick={() => window.history.back()}
          className="mb-6 flex items-center text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
          </svg>
          Back to search results
        </button>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden mb-8">
          <img 
            src={destination.image} 
            alt={destination.name} 
            className="w-full h-64 object-cover"
          />
          <div className="p-6">
            <h1 className="text-3xl font-bold mb-4 text-gray-900 dark:text-white">{destination.name}</h1>
            <p className="text-gray-700 dark:text-gray-300 mb-6">{destination.description}</p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Top Attractions</h2>
                <ul className="space-y-2">
                  {destination.attractions.map((attraction, index) => (
                    <li key={index} className="flex items-start">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600 dark:text-blue-400 mr-2 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                      </svg>
                      <span className="text-gray-700 dark:text-gray-300">{attraction}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Travel Information</h2>
                <div className="space-y-4">
                  <div className="flex justify-between items-center p-3 bg-blue-50 dark:bg-blue-900 rounded-md">
                    <span className="text-gray-700 dark:text-gray-300">Weather</span>
                    <span className="font-medium text-gray-900 dark:text-white">{destination.weather.temperature} • {destination.weather.condition}</span>
                  </div>
                  
                  <div className="flex justify-between items-center p-3 bg-green-50 dark:bg-green-900 rounded-md">
                    <span className="text-gray-700 dark:text-gray-300">Best Time to Visit</span>
                    <span className="font-medium text-gray-900 dark:text-white">Spring & Summer</span>
                  </div>
                  
                  <div className="flex justify-between items-center p-3 bg-purple-50 dark:bg-purple-900 rounded-md">
                    <span className="text-gray-700 dark:text-gray-300">Recommended Duration</span>
                    <span className="font-medium text-gray-900 dark:text-white">3-4 days</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="mt-8">
              <h2 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Travel Tips</h2>
              <ul className="space-y-3">
                {destination.travelTips.map((tip, index) => (
                  <li key={index} className="flex items-start p-3 bg-gray-50 dark:bg-gray-700 rounded-md">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-blue-600 dark:text-blue-400 mr-2 mt-0.5" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                      <path fillRule="evenodd" d="M.458 10C1.732 5.943 6.615 3 12 3c5.385 0 10.268 2.943 11.542 7-1.274 4.057-6.157 7-11.542 7-5.385 0-10.268-2.943-11.542-7z" clipRule="evenodd" />
                    </svg>
                    <span className="text-gray-700 dark:text-gray-300">{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
        
        <div className="text-center">
          <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-md font-medium transition-colors shadow-md">
            Book This Destination
          </button>
        </div>
      </div>
    </div>
  )
}

export default DestinationDetailsPage
