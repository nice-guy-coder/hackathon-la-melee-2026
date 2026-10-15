import React from 'react'

interface ReusableCardProps {
  title: string
  description: string
  imageUrl?: string
  onClick?: () => void
  className?: string
}

const ReusableCard: React.FC<ReusableCardProps> = ({ 
  title, 
  description, 
  imageUrl,
  onClick,
  className = ''
}) => {
  return (
    <div 
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer ${className}`}
      onClick={onClick}
    >
      {imageUrl && (
        <img 
          src={imageUrl} 
          alt={title} 
          className="w-full h-48 object-cover"
        />
      )}
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-2">{title}</h3>
        <p className="text-gray-600 dark:text-gray-300 text-sm">{description}</p>
      </div>
    </div>
  )
}

export default ReusableCard
