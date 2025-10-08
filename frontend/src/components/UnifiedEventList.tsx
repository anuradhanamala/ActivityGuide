import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { UnifiedSearchFilters } from './UnifiedEventSearch';

interface UnifiedEvent {
  id: string;
  external_id: string;
  source: string;
  event_type: string;
  title: string;
  description?: string;
  summary?: string;
  location_name?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  primary_category?: string;
  tags?: string[];
  age_range_min?: number;
  age_range_max?: number;
  is_free?: boolean;
  is_indoor?: boolean;
  start_time?: string;
  start_date?: string;
  image_url?: string;
  source_url?: string;
  booking_url?: string;
}

interface UnifiedEventListProps {
  filters?: UnifiedSearchFilters;
}

const UnifiedEventList: React.FC<UnifiedEventListProps> = ({ filters }) => {
  const [events, setEvents] = useState<UnifiedEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchSummary, setSearchSummary] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (filters) {
      searchEvents(filters);
    }
  }, [filters]);

  const searchEvents = async (searchFilters: UnifiedSearchFilters) => {
    setLoading(true);
    setError('');
    
    try {
      const params = new URLSearchParams();
      
      // Add all filters
      if (searchFilters.city) params.append('city', searchFilters.city);
      if (searchFilters.zipCode) params.append('zip_code', searchFilters.zipCode);
      if (searchFilters.ageMin !== '') params.append('age_min', searchFilters.ageMin.toString());
      if (searchFilters.ageMax !== '') params.append('age_max', searchFilters.ageMax.toString());
      if (searchFilters.isIndoor !== null) params.append('is_indoor', searchFilters.isIndoor.toString());
      if (searchFilters.isFree !== null) params.append('is_free', searchFilters.isFree.toString());
      if (searchFilters.startDate) params.append('start_date', searchFilters.startDate);
      if (searchFilters.endDate) params.append('end_date', searchFilters.endDate);
      if (searchFilters.eventType) params.append('event_type', searchFilters.eventType);
      
      // Add categories
      searchFilters.categories.forEach(cat => params.append('categories', cat));
      
      // Add sources
      searchFilters.sources.forEach(src => params.append('sources', src));
      
      // Always set a limit
      params.append('limit', '100');
      
      const response = await axios.get(`http://localhost:8000/api/v1/unified/search?${params}`);
      
      setEvents(response.data.events || []);
      setSearchSummary(response.data.search_summary || '');
      
    } catch (error: any) {
      console.error('Error searching events:', error);
      setError(error.response?.data?.detail || 'Failed to search events');
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const getSourceBadgeColor = (source: string) => {
    const colors: Record<string, string> = {
      'yelp': 'bg-red-100 text-red-800',
      'eventbrite': 'bg-orange-100 text-orange-800',
      'google_places': 'bg-blue-100 text-blue-800',
      'meetup': 'bg-purple-100 text-purple-800',
      'recreation_gov': 'bg-green-100 text-green-800',
      'openstreetmap': 'bg-teal-100 text-teal-800',
      'agentic_parallel_ai': 'bg-indigo-100 text-indigo-800'
    };
    return colors[source] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Searching across all data sources...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 mb-8">
        <h3 className="text-lg font-semibold text-red-900 mb-2">Search Error</h3>
        <p className="text-red-700">{error}</p>
      </div>
    );
  }

  if (events.length === 0 && !filters) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <p className="text-blue-800">Use the search form above to find activities</p>
      </div>
    );
  }

  return (
    <div>
      {searchSummary && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 font-medium">{searchSummary}</p>
        </div>
      )}

      {events.length === 0 ? (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-600 text-lg">No activities found matching your criteria</p>
          <p className="text-gray-500 text-sm mt-2">Try adjusting your search filters</p>
        </div>
      ) : (
        <div className="space-y-4">
          <h3 className="text-xl font-semibold text-gray-900">
            Found {events.length} Activities
          </h3>
          
          {events.map((event) => (
            <div key={event.id} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
              <div className="flex justify-between items-start mb-3">
                <h4 className="text-lg font-semibold text-gray-900 flex-1">
                  {event.title}
                </h4>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${getSourceBadgeColor(event.source)}`}>
                  {event.source.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              
              {event.description && (
                <p className="text-gray-700 mb-3">{event.description}</p>
              )}
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-4">
                {event.location_name && (
                  <div>
                    <span className="font-medium">📍 Location:</span>
                    <p>{event.location_name}</p>
                  </div>
                )}
                
                {event.city && (
                  <div>
                    <span className="font-medium">🏙️ City:</span>
                    <p>{event.city}, {event.state}</p>
                  </div>
                )}
                
                {event.primary_category && (
                  <div>
                    <span className="font-medium">🏷️ Category:</span>
                    <p className="capitalize">{event.primary_category.replace('_', ' ')}</p>
                  </div>
                )}
                
                {event.is_free !== undefined && (
                  <div>
                    <span className="font-medium">💰 Price:</span>
                    <p className={event.is_free ? 'text-green-600 font-semibold' : 'text-gray-600'}>
                      {event.is_free ? 'FREE' : 'Paid'}
                    </p>
                  </div>
                )}
              </div>

              {event.tags && event.tags.length > 0 && (
                <div className="mb-3">
                  <div className="flex flex-wrap gap-1">
                    {event.tags.slice(0, 5).map((tag, idx) => (
                      <span key={idx} className="px-2 py-1 bg-gray-100 text-gray-600 rounded text-xs">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              <div className="flex gap-2">
                {event.source_url && (
                  <a
                    href={event.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                  >
                    View Details →
                  </a>
                )}
                {event.booking_url && (
                  <a
                    href={event.booking_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm"
                  >
                    Book Now
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UnifiedEventList;
