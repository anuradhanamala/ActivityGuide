import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import NaturalLanguageSearch from '../components/NaturalLanguageSearch';
import UnifiedEventSearch, { UnifiedSearchFilters } from '../components/UnifiedEventSearch';
import UnifiedEventList from '../components/UnifiedEventList';

const FindActivities: React.FC = () => {
  const [searchMode, setSearchMode] = useState<'natural' | 'advanced'>('natural');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [unifiedFilters, setUnifiedFilters] = useState<UnifiedSearchFilters | undefined>(undefined);

  const handleNaturalSearchResults = (events: any[]) => {
    setSearchResults(events);
  };

  const handleUnifiedSearch = (filters: UnifiedSearchFilters) => {
    setUnifiedFilters(filters);
  };

  const handleSwitchToAdvanced = () => {
    setSearchMode('advanced');
  };

  const handleSwitchToNatural = () => {
    setSearchMode('natural');
  };

  return (
    <div>
      {/* Page Header */}
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">
          Discover Family Activities
        </h1>
        <p className="text-lg text-gray-600 max-w-2xl mx-auto">
          Find perfect activities for your kids from multiple sources: Yelp, Eventbrite, Google Places, and more!
        </p>
      </div>

      {/* Mode Toggle */}
      <div className="mb-6 flex justify-center gap-4 flex-wrap">
        <button
          onClick={handleSwitchToNatural}
          className={`px-6 py-3 rounded-lg font-medium transition-all ${
            searchMode === 'natural'
              ? 'bg-blue-600 text-white shadow-lg'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          🤖 AI-Powered Search
        </button>
        <button
          onClick={handleSwitchToAdvanced}
          className={`px-6 py-3 rounded-lg font-medium transition-all ${
            searchMode === 'advanced'
              ? 'bg-blue-600 text-white shadow-lg'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          🔧 Advanced Filters
        </button>
        <Link
          to="/"
          className="px-6 py-3 rounded-lg font-medium bg-gradient-to-r from-purple-600 to-pink-600 text-white hover:from-purple-700 hover:to-pink-700 transition-all shadow-lg"
        >
          🎯 Activity Explorer
        </Link>
      </div>

      {/* Search Components */}
      {searchMode === 'natural' ? (
        <div>
          <NaturalLanguageSearch 
            onSearchResults={handleNaturalSearchResults} 
            onSwitchToTraditional={handleSwitchToAdvanced}
          />
          
          {/* Show NLP results if using natural search */}
          {searchResults.length > 0 && (
            <div className="mt-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                Search Results ({searchResults.length})
              </h3>
              <div className="space-y-4">
                {searchResults.map((event: any, index: number) => (
                  <div key={index} className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow">
                    <h4 className="text-lg font-semibold text-gray-900 mb-2">
                      {event.title}
                    </h4>
                    {event.description && (
                      <p className="text-gray-700 mb-3">{event.description}</p>
                    )}
                    <div className="text-sm text-gray-600">
                      <p>📍 {event.city}, {event.state}</p>
                      {event.category && <p>🏷️ {event.category}</p>}
                      {event.is_free && <p className="text-green-600 font-semibold">💰 FREE</p>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        <div>
          <UnifiedEventSearch onSearch={handleUnifiedSearch} />
          <UnifiedEventList filters={unifiedFilters} />
        </div>
      )}

      {/* Info Section */}
      <div className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-8 border border-blue-200">
        <h3 className="text-2xl font-bold text-gray-900 mb-4">
          🌟 Comprehensive Activity Discovery
        </h3>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Data Sources:</h4>
            <ul className="space-y-1 text-gray-700">
              <li>✅ Yelp - Local businesses & venues ({searchMode === 'advanced' ? '78 venues' : 'Museums, gyms, parks'})</li>
              <li>✅ Eventbrite - Events & classes</li>
              <li>✅ Google Places - Parks & facilities</li>
              <li>✅ Meetup - Community events</li>
              <li>✅ Recreation.gov - National parks</li>
              <li>✅ OpenStreetMap - Playgrounds</li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-gray-900 mb-2">Search Features:</h4>
            <ul className="space-y-1 text-gray-700">
              <li>🎯 Filter by age range</li>
              <li>📍 Location-based search</li>
              <li>🏷️ Category filtering</li>
              <li>💰 Free vs paid options</li>
              <li>🏠 Indoor/outdoor selection</li>
              <li>🤖 AI-powered natural language</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FindActivities;
