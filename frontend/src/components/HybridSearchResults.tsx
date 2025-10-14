import React, { useState } from 'react';

interface HybridSearchResultsProps {
  results: any;
  isLoading: boolean;
}

const HybridSearchResults: React.FC<HybridSearchResultsProps> = ({ results, isLoading }) => {
  const [expandedRecommendations, setExpandedRecommendations] = useState(true);

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-12 text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600 text-lg">Searching for perfect activities...</p>
        <p className="text-gray-500 text-sm mt-2">AI is analyzing your query</p>
      </div>
    );
  }

  if (!results) {
    return null;
  }

  const {
    recommendations,
    events_included,
  } = results;

  return (
    <div className="space-y-6">
      {/* AI Recommendations */}
      {recommendations && (
        <div className="bg-white rounded-lg shadow-lg overflow-hidden border border-purple-100">
          <div 
            className="bg-gradient-to-r from-purple-600 to-pink-600 p-4 cursor-pointer flex items-center justify-between"
            onClick={() => setExpandedRecommendations(!expandedRecommendations)}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">🤖</span>
              <h3 className="text-xl font-bold text-white">AI Recommendations</h3>
            </div>
            <button className="text-white text-2xl">
              {expandedRecommendations ? '−' : '+'}
            </button>
          </div>
          
          {expandedRecommendations && (
            <div className="p-6 bg-purple-50">
              <div className="prose max-w-none text-gray-800 whitespace-pre-wrap">
                {recommendations}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Activity Cards */}
      {events_included && events_included.length > 0 && (
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Activities ({events_included.length})
          </h3>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {events_included.map((event: any, index: number) => (
              <ActivityCard key={event.id || index} event={event} />
            ))}
          </div>
        </div>
      )}

      {/* No Results */}
      {(!events_included || events_included.length === 0) && !recommendations && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
          <span className="text-6xl mb-4 block">🔍</span>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">No Activities Found</h3>
          <p className="text-gray-600">
            Try adjusting your search terms or filters to find more activities.
          </p>
        </div>
      )}
    </div>
  );
};

// Activity Card Component
const ActivityCard: React.FC<{ event: any }> = ({ event }) => {
  const [showFullDescription, setShowFullDescription] = useState(false);

  const description = event.description || event.summary || 'No description available';
  const truncatedDescription = description.length > 150 
    ? description.substring(0, 150) + '...' 
    : description;

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-md hover:shadow-xl transition-all overflow-hidden">
      <div className="p-6">
        {/* Header */}
        <div className="mb-3">
          <h4 className="text-lg font-bold text-gray-900 mb-1">
            {event.title}
          </h4>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-blue-100 text-blue-800">
              {event.source?.toUpperCase() || 'UNKNOWN'}
            </span>
            {event.category && (
              <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-800">
                {event.category}
              </span>
            )}
          </div>
        </div>

        {/* Description */}
        <div className="text-gray-700 text-sm mb-4">
          <p>{showFullDescription ? description : truncatedDescription}</p>
          {description.length > 150 && (
            <button
              onClick={() => setShowFullDescription(!showFullDescription)}
              className="text-blue-600 hover:text-blue-800 text-xs mt-1"
            >
              {showFullDescription ? 'Show less' : 'Show more'}
            </button>
          )}
        </div>

        {/* Details */}
        <div className="space-y-2 text-sm text-gray-600">
          {event.city && (
            <p className="flex items-center gap-2">
              <span>📍</span>
              <span>{event.city}, {event.state || 'MI'}</span>
            </p>
          )}
          
          {(event.age_min || event.age_max) && (
            <p className="flex items-center gap-2">
              <span>👶</span>
              <span>Ages: {event.age_min || 0}-{event.age_max || 18}</span>
            </p>
          )}

          {event.is_free !== undefined && (
            <p className="flex items-center gap-2">
              <span>💰</span>
              <span className={event.is_free ? 'text-green-600 font-semibold' : ''}>
                {event.is_free ? 'FREE' : 'Paid'}
              </span>
            </p>
          )}

          {event.is_indoor !== undefined && (
            <p className="flex items-center gap-2">
              <span>{event.is_indoor ? '🏠' : '🌳'}</span>
              <span>{event.is_indoor ? 'Indoor' : 'Outdoor'}</span>
            </p>
          )}
        </div>

        {/* Tags */}
        {event.tags && event.tags.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-1">
            {event.tags.slice(0, 3).map((tag: string, idx: number) => (
              <span
                key={idx}
                className="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default HybridSearchResults;

