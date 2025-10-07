import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import EventList from './components/EventList';
import EventDetail from './components/EventDetail';
import UserProfile from './components/UserProfile';
import ProviderSubmission from './components/ProviderSubmission';
import NaturalLanguageSearch from './components/NaturalLanguageSearch';
import EventSearch, { SearchFilters } from './components/EventSearch';
import './App.css';

function App() {
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [searchMode, setSearchMode] = useState<'natural' | 'traditional'>('natural');

  const handleSearchResults = (events: any[]) => {
    setSearchResults(events);
  };

  const handleTraditionalSearch = (filters: SearchFilters) => {
    // For now, we'll just clear results since the traditional search
    // doesn't have a backend implementation yet
    // TODO: Implement traditional search API call
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
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={
              <div>
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
                      <span className="mr-2 text-blue-600 font-bold">AI</span>
                      Try natural language search instead
                    </button>
                  </div>
                )}

                {/* Results */}
                <EventList events={searchResults} />
              </div>
            } />
            <Route path="/events/:id" element={<EventDetail />} />
            <Route path="/profile" element={<UserProfile />} />
            <Route path="/submit" element={<ProviderSubmission />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;