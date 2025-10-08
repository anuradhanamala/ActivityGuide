import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import NaturalLanguageSearch from '../components/NaturalLanguageSearch';
import EventSearch, { SearchFilters } from '../components/EventSearch';
import EventList from '../components/EventList';

const ParallelAIEvents: React.FC = () => {
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchMode, setSearchMode] = useState<'natural' | 'traditional'>('natural');

  const handleSearchResults = (events: any[]) => {
    setSearchResults(events);
  };

  const handleTraditionalSearch = (filters: SearchFilters) => {
    console.log('Traditional search filters:', filters);
    setSearchResults([]);
  };

  const handleSwitchToTraditional = () => {
    setSearchMode('traditional');
  };

  const handleSwitchToNatural = () => {
    setSearchMode('natural');
  };

  return (
    <div>
      {/* Page Header */}
      <div className="mb-8">
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-lg p-8 text-white mb-6">
          <h1 className="text-4xl font-bold mb-3">
            ⚡ Parallel AI Event Discovery
          </h1>
          <p className="text-lg opacity-90 max-w-2xl">
            Powered by advanced AI search across multiple activity categories
          </p>
        </div>

        {/* Navigation */}
        <div className="flex gap-4 mb-6">
          <Link
            to="/"
            className="px-6 py-3 rounded-lg font-medium bg-blue-600 text-white hover:bg-blue-700 transition-all"
          >
            ← Back to Unified Search
          </Link>
        </div>
      </div>

      {/* Search Component */}
      {searchMode === 'natural' ? (
        <NaturalLanguageSearch 
          onSearchResults={handleSearchResults} 
          onSwitchToTraditional={handleSwitchToTraditional}
        />
      ) : (
        <EventSearch 
          onSearch={handleTraditionalSearch}
        />
      )}

      {/* Switch back to natural language search */}
      {searchMode === 'traditional' && (
        <div className="text-center mb-6">
          <button
            onClick={handleSwitchToNatural}
            className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700 transition-colors"
          >
            <span className="mr-2 text-blue-600 font-bold">🤖</span>
            Try natural language search instead
          </button>
        </div>
      )}

      {/* Results */}
      <EventList events={searchResults} />

      {/* Info Banner */}
      <div className="mt-12 bg-indigo-50 border border-indigo-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-indigo-900 mb-2">
          About Parallel AI Search
        </h3>
        <p className="text-indigo-800">
          This page searches the <strong>events</strong> table containing 2,670 activities
          discovered through Parallel AI's comprehensive search across multiple categories
          including sports, music, arts, dance, education, and STEM activities.
        </p>
        <p className="text-indigo-800 mt-2">
          For broader coverage including Yelp businesses, use the{' '}
          <Link to="/" className="font-semibold underline">Unified Search</Link> on the home page.
        </p>
      </div>
    </div>
  );
};

export default ParallelAIEvents;
