import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
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
  address: string;
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

const EventDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);

  const loadEvent = useCallback(async (eventId: number) => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/events/${eventId}`);
      setEvent(response.data);
    } catch (error) {
      console.error('Error loading event:', error);
      // For demo purposes, show mock data
      setEvent(getMockEvent(eventId));
    } finally {
      setLoading(false);
    }
  }, []);

  const getMockEvent = (eventId: number): Event => ({
    id: eventId,
    title: "Storytime at Ann Arbor Library",
    description: "Join us for an interactive storytime session with books, songs, and activities perfect for young children. This weekly program features carefully selected books that promote early literacy skills, interactive songs that encourage movement and participation, and hands-on activities that spark creativity and imagination. Our experienced children's librarians create a welcoming environment where both children and caregivers can engage with stories and each other.",
    summary: "A delightful storytime experience with engaging books and interactive activities designed for toddlers and preschoolers.",
    start_time: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(),
    end_time: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000 + 60 * 60 * 1000).toISOString(),
    location_name: "Ann Arbor District Library",
    address: "343 S Fifth Ave",
    city: "Ann Arbor",
    state: "MI",
    zip_code: "48104",
    category: "education",
    age_range_min: 2,
    age_range_max: 5,
    is_indoor: true,
    is_free: true,
    source: "community",
    tags: ["reading", "education", "free", "library"]
  });

  useEffect(() => {
    if (id) {
      loadEvent(parseInt(id));
    }
  }, [id, loadEvent]);

  const formatEventTime = (startTime: string, endTime?: string) => {
    const start = new Date(startTime);
    const startFormatted = format(start, 'EEEE, MMMM d, yyyy \'at\' h:mm a');
    
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        <span className="ml-3 text-gray-600">Loading event details...</span>
      </div>
    );
  }

  if (!event) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Event Not Found</h2>
        <p className="text-gray-600 mb-6">The event you're looking for doesn't exist or has been removed.</p>
        <a
          href="/"
          className="inline-flex items-center text-primary-600 hover:text-primary-700 font-medium"
        >
          <span className="mr-2 text-blue-600 font-bold">←</span>
          Back to Activities
        </a>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <a
          href="/"
          className="inline-flex items-center text-primary-600 hover:text-primary-700 font-medium mb-4"
        >
          <span className="mr-2 text-blue-600 font-bold">←</span>
          Back to Activities
        </a>
      </div>

      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        {event.image_url && (
          <img
            src={event.image_url}
            alt={event.title}
            className="w-full h-64 md:h-80 object-cover"
          />
        )}
        
        <div className="p-6 md:p-8">
          <div className="flex items-start justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900">{event.title}</h1>
            <span className="bg-primary-100 text-primary-800 text-sm font-medium px-3 py-1 rounded-full ml-4 flex-shrink-0">
              {event.category}
            </span>
          </div>
          
          {event.summary && (
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-4 mb-6">
              <h3 className="text-lg font-semibold text-primary-900 mb-2">AI Summary</h3>
              <p className="text-primary-800">{event.summary}</p>
            </div>
          )}
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="space-y-4">
              <div className="flex items-start">
                <span className="text-blue-600 mr-3 mt-0.5 font-bold">📅</span>
                <div>
                  <h3 className="font-semibold text-gray-900">Date & Time</h3>
                  <p className="text-gray-600">{formatEventTime(event.start_time, event.end_time)}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <span className="text-red-600 mr-3 mt-0.5 font-bold">📍</span>
                <div>
                  <h3 className="font-semibold text-gray-900">Location</h3>
                  <p className="text-gray-600">
                    {event.location_name}
                    {event.address && <><br />{event.address}</>}
                    <br />{event.city}, {event.state} {event.zip_code}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-start">
                <span className="text-blue-600 mr-3 mt-0.5 font-bold">👥</span>
                <div>
                  <h3 className="font-semibold text-gray-900">Age Range</h3>
                  <p className="text-gray-600">{getAgeRangeText(event)}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <span className="text-red-600 mr-3 mt-0.5 font-bold">💰</span>
                <div>
                  <h3 className="font-semibold text-gray-900">Cost</h3>
                  <p className="text-gray-600">{getPriceText(event)}</p>
                </div>
              </div>
              
              <div className="flex items-start">
                <span className="text-blue-600 mr-3 mt-0.5 font-bold">🕐</span>
                <div>
                  <h3 className="font-semibold text-gray-900">Location Type</h3>
                  <p className="text-gray-600">{event.is_indoor ? 'Indoor' : 'Outdoor'}</p>
                </div>
              </div>
            </div>
          </div>
          
          {event.description && (
            <div className="mb-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">About This Event</h3>
              <div className="prose prose-gray max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-line">
                  {event.description}
                </p>
              </div>
            </div>
          )}
          
          {event.tags && event.tags.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold text-gray-900 mb-3">Tags</h3>
              <div className="flex flex-wrap gap-2">
                {event.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="bg-gray-100 text-gray-700 text-sm px-3 py-1 rounded-full"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          <div className="flex items-center justify-between pt-6 border-t">
            <div className="text-sm text-gray-500">
              Source: {event.source}
            </div>
            
            {event.source_url && (
              <a
                href={event.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
              >
                <span className="mr-2 text-blue-600 font-bold">🔗</span>
                Visit Event Page
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EventDetail;

