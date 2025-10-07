import React, { useState } from 'react';
import axios from 'axios';

interface ParsedQuery {
  original_query: string;
  parsed_params: Record<string, any>;
  confidence: number;
  missing_info: string[];
  suggestions: string[];
  needs_clarification: boolean;
  events?: any[];
}

interface NaturalLanguageSearchProps {
  onSearchResults?: (events: any[]) => void;
  onSwitchToTraditional?: () => void;
}

const NaturalLanguageSearch: React.FC<NaturalLanguageSearchProps> = ({ onSearchResults, onSwitchToTraditional }) => {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [parsedResult, setParsedResult] = useState<ParsedQuery | null>(null);


  // These examples are now externalized in the backend configuration
  // and can be fetched from the API if needed
  const exampleQueries = [
    "Basketball classes for 8-10 near me this Saturday",
    "Free art activities for my 5 year old this weekend",
    "Indoor activities near 12345 for toddlers",
    "Swimming lessons for kids aged 6-8",
    "Music classes this Tuesday near me",
    "Outdoor family activities this Sunday"
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/api/v1/nlp/parse-and-search', {
        query: query.trim(),
        user_id: null // You can add user authentication later
      });

      setParsedResult(response.data);
      
      if (response.data.events && onSearchResults) {
        onSearchResults(response.data.events);
      }


    } catch (error) {
      console.error('Error parsing query:', error);
      // Fallback to mock data for demo
      setParsedResult({
        original_query: query,
        parsed_params: { category: 'sports', age_min: 8, age_max: 10 },
        confidence: 0.8,
        missing_info: ['zip_code'],
        suggestions: ['What ZIP code would you like to search in?'],
        needs_clarification: true,
        events: []
      });
    } finally {
      setIsLoading(false);
    }
  };


  const handleExampleClick = (example: string) => {
    setQuery(example);
  };

  return (
    <div className="mb-8">

      {parsedResult && (
        <div className="mb-8 max-w-4xl mx-auto">
          {/* Events Found */}
          {parsedResult.events && parsedResult.events.length > 0 && (
            <div className="bg-white border border-green-200 rounded-2xl p-6 shadow-lg mb-4">
              <div className="flex items-center mb-4">
                <div className="w-3 h-3 bg-green-500 rounded-full mr-3"></div>
                <h4 className="text-lg font-semibold text-green-900">
                  Found {parsedResult.events.length} activities!
                </h4>
              </div>
              <p className="text-green-800">
                Check the results below for activities that match your request.
              </p>
            </div>
          )}

          {/* No Events Found */}
          {parsedResult.events && parsedResult.events.length === 0 && (
            <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-lg mb-4">
              <div className="flex items-center mb-4">
                <div className="w-3 h-3 bg-gray-400 rounded-full mr-3"></div>
                <h4 className="text-lg font-semibold text-gray-900">No activities found</h4>
              </div>
              <p className="text-gray-700">
                Try adjusting your search criteria or check back later for new events.
              </p>
            </div>
          )}

      </div>
      )}

      {/* Search Box */}
      <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-2xl shadow-lg border border-blue-200 p-8">
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-3">Find Perfect Activities</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto mb-4">
          </p>
          {onSwitchToTraditional && (
            <div className="mt-4">
              <button
                onClick={onSwitchToTraditional}
                className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700 transition-colors"
              >
                Prefer traditional search
              </button>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="relative">
          <textarea
            value={query}
            onChange={(e) => setQuery(e.target.value)}
              placeholder="Try: 'Basketball classes for 8-10 year olds in Troy' or 'Free art activities for my 5 year old'"
              className="w-full px-6 py-4 pr-16 text-lg border-2 border-gray-200 rounded-2xl focus:ring-4 focus:ring-blue-500 focus:border-blue-500 resize-none shadow-sm transition-all duration-200"
            rows={3}
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={isLoading || !query.trim()}
              className="absolute right-3 top-3 p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-xl"
          >
            {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
                <span className="text-white font-bold">→</span>
            )}
          </button>
        </div>
      </form>

        {/* Example Queries */}
        <div className="mt-8 max-w-4xl mx-auto">
          <h3 className="text-center text-sm font-semibold text-gray-600 mb-4 uppercase tracking-wide">Popular Searches</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {exampleQueries.slice(0, 6).map((example, index) => (
              <button
                key={index}
                onClick={() => handleExampleClick(example)}
                className="text-sm bg-white text-gray-700 px-4 py-3 rounded-xl hover:bg-blue-50 hover:text-blue-700 hover:border-blue-200 border border-gray-200 transition-all duration-200 text-left shadow-sm hover:shadow-md"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NaturalLanguageSearch;
