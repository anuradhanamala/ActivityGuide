import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import axios from 'axios';

interface Event {
  id: number;
  title: string;
  description: string;
  summary: string;
  start_time: string;
  end_time?: string;
  location_name: string;
  city: string;
  state: string;
  zip_code: string;
  category: string;
  age_range_min?: number;
  age_range_max?: number;
  is_indoor: boolean;
  is_free: boolean;
  price_min?: number;
  price_max?: number;
  source: string;
  source_url?: string;
  image_url?: string;
  tags?: string[];
}

interface EventSearchFilters {
  zipCode: string;
  startDate: string;
  endDate: string;
  category: string;
  ageMin: number | '';
  ageMax: number | '';
  isIndoor: boolean | null;
  isFree: boolean | null;
  priceMax: number | '';
}

interface EventListProps {
  events?: Event[];
}

const EventList: React.FC<EventListProps> = ({ events: propEvents }) => {
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchSummary, setSearchSummary] = useState('');
  const [totalCount, setTotalCount] = useState(0);

  const loadEvents = useCallback(async (filters: EventSearchFilters) => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      
      if (filters.zipCode) params.append('zip_code', filters.zipCode);
      if (filters.startDate) params.append('start_date', filters.startDate);
      if (filters.endDate) params.append('end_date', filters.endDate);
      if (filters.category) params.append('category', filters.category);
      if (filters.ageMin !== '') params.append('age_min', filters.ageMin.toString());
      if (filters.ageMax !== '') params.append('age_max', filters.ageMax.toString());
      if (filters.isIndoor !== null) params.append('is_indoor', filters.isIndoor.toString());
      if (filters.isFree !== null) params.append('is_free', filters.isFree.toString());
      if (filters.priceMax !== '') params.append('price_max', filters.priceMax.toString());
      
      const response = await axios.get(`http://localhost:8000/api/v1/events/search?${params}`);
      
      setEvents(response.data.events);
      setSearchSummary(response.data.search_summary || '');
      setTotalCount(response.data.total_count);
    } catch (error) {
      console.error('Error loading events:', error);
      // For demo purposes, show mock data
      setEvents(getMockEvents());
      setSearchSummary('Here are some great family activities in your area!');
      setTotalCount(3);
    } finally {
      setLoading(false);
    }
  }, []);

  // Use prop events if provided, otherwise load from API
  useEffect(() => {
    if (propEvents) {
      setEvents(propEvents);
      setTotalCount(propEvents.length);
    } else {
      // Load initial events on component mount
      loadEvents({
        zipCode: '48104',
        startDate: '',
        endDate: '',
        category: '',
        ageMin: '',
        ageMax: '',
        isIndoor: null,
        isFree: null,
        priceMax: ''
      });
    }
  }, [propEvents, loadEvents]);

  const getMockEvents = (): Event[] => [
    {
      id: 1,
      title: "Storytime at Ann Arbor Library",
      description: "Join us for an interactive storytime session with books, songs, and activities perfect for young children.",
      summary: "A delightful storytime experience with engaging books and interactive activities designed for toddlers and preschoolers.",
      start_time: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
      end_time: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 60 * 60 * 1000).toISOString(),
      location_name: "Ann Arbor District Library",
      city: "Ann Arbor",
      state: "MI",
      zip_code: "48104",
      category: "education",
      age_range_min: 2,
      age_range_max: 5,
      is_indoor: true,
      is_free: true,
      source: "community",
      tags: ["reading", "education", "free"]
    },
    {
      id: 2,
      title: "Hands-on Kids Museum Day",
      description: "Explore interactive exhibits designed to spark curiosity and learning through hands-on discovery.",
      summary: "An exciting museum experience with interactive exhibits that make learning fun for children of all ages.",
      start_time: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
      end_time: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000 + 4 * 60 * 60 * 1000).toISOString(),
      location_name: "Hands-On Museum",
      city: "Ann Arbor",
      state: "MI",
      zip_code: "48104",
      category: "education",
      age_range_min: 3,
      age_range_max: 12,
      is_indoor: true,
      is_free: false,
      price_min: 8,
      price_max: 12,
      source: "museum",
      tags: ["museum", "interactive", "learning"]
    },
    {
      id: 3,
      title: "Family Hike at County Park",
      description: "Enjoy a guided nature hike through beautiful trails with activities for the whole family.",
      summary: "A wonderful outdoor adventure with guided nature exploration and family-friendly hiking trails.",
      start_time: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString(),
      end_time: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000 + 2 * 60 * 60 * 1000).toISOString(),
      location_name: "Huron Hills Golf Course",
      city: "Ann Arbor",
      state: "MI",
      zip_code: "48105",
      category: "outdoor",
      age_range_min: 5,
      age_range_max: 18,
      is_indoor: false,
      is_free: true,
      source: "community",
      tags: ["hiking", "nature", "outdoor", "free"]
    }
  ];

  const formatEventTime = (startTime: string, endTime?: string) => {
    const start = new Date(startTime);
    const startFormatted = format(start, 'MMM d, h:mm a');
    
    if (endTime) {
      const end = new Date(endTime);
      const endFormatted = format(end, 'h:mm a');
      return `${startFormatted} - ${endFormatted}`;
    }
    
    return startFormatted;
  };

  const getAgeRangeText = (event: Event) => {
    if (event.age_range_min && event.age_range_max) {
      return `Ages ${event.age_range_min}-${event.age_range_max}`;
    } else if (event.age_range_min) {
      return `Ages ${event.age_range_min}+`;
    } else if (event.age_range_max) {
      return `Ages up to ${event.age_range_max}`;
    }
    return 'All ages';
  };

  const getPriceText = (event: Event) => {
    if (event.is_free) return 'Free';
    if (event.price_min && event.price_max) {
      return `$${event.price_min}-$${event.price_max}`;
    } else if (event.price_min) {
      return `From $${event.price_min}`;
    }
    return 'Paid event';
  };

  return (
    <div>
      {searchSummary && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-primary-900 mb-2">AI-Powered Recommendations</h3>
          <p className="text-primary-800">{searchSummary}</p>
        </div>
      )}

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          <span className="ml-3 text-gray-600">Loading activities...</span>
        </div>
      ) : events.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {events.map((event) => (
            <div key={event.id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
              {event.image_url && (
                <img
                  src={event.image_url}
                  alt={event.title}
                  className="w-full h-48 object-cover rounded-t-lg"
                />
              )}
              
              <div className="p-6">
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
                    {event.title}
                  </h3>
                  <span className="bg-primary-100 text-primary-800 text-xs font-medium px-2 py-1 rounded-full ml-2 flex-shrink-0">
                    {event.category}
                  </span>
                </div>
                
                <p className="text-gray-600 text-sm mb-4 line-clamp-3">
                  {event.summary || event.description}
                </p>
                
                <div className="space-y-2 mb-4">
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="mr-2 text-blue-600 font-bold">📅</span>
                    {formatEventTime(event.start_time, event.end_time)}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="mr-2 text-red-600 font-bold">📍</span>
                    {event.location_name}, {event.city}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="mr-2 text-blue-600 font-bold">👥</span>
                    {getAgeRangeText(event)}
                  </div>
                  
                  <div className="flex items-center text-sm text-gray-600">
                    <span className="mr-2 text-red-600 font-bold">💰</span>
                    {getPriceText(event)}
                  </div>
                </div>
                
                <div className="flex items-center justify-between">
                  <Link
                    to={`/events/${event.id}`}
                    className="text-primary-600 hover:text-primary-700 font-medium text-sm"
                  >
                    View Details
                  </Link>
                  
                  {event.source_url && (
                    <a
                      href={event.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center text-gray-600 hover:text-primary-600 text-sm"
                    >
                      <span className="mr-1 text-blue-600 font-bold">🔗</span>
                      Source
                    </a>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default EventList;

