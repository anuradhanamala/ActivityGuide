import React, { useState } from 'react';

interface HybridSearchBoxProps {
  onSearch: (results: any) => void;
  onLoading: (loading: boolean) => void;
}

const HybridSearchBox: React.FC<HybridSearchBoxProps> = ({ onSearch, onLoading }) => {
  const [query, setQuery] = useState('');
  const [city, setCity] = useState('');
  const [ageMin, setAgeMin] = useState<number | ''>('');
  const [ageMax, setAgeMax] = useState<number | ''>('');
  const [isFree, setIsFree] = useState<boolean | undefined>(undefined);
  const [category, setCategory] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setError(null);
    onLoading(true);

    try {
      // Build query parameters
      const params = new URLSearchParams({
        query: query.trim(),
      });

      if (city) params.append('city', city);
      if (ageMin !== '') params.append('age_min', ageMin.toString());
      if (ageMax !== '') params.append('age_max', ageMax.toString());
      if (category) params.append('category', category);
      if (isFree !== undefined) params.append('is_free', isFree.toString());

      const response = await fetch(
        `http://localhost:8000/api/v1/rag/hybrid-recommend?${params}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`Search failed: ${response.statusText}`);
      }

      const data = await response.json();
      onSearch(data);
    } catch (err) {
      console.error('Hybrid search error:', err);
      setError(err instanceof Error ? err.message : 'Search failed. Please try again.');
      onSearch(null);
    } finally {
      onLoading(false);
    }
  };

  const exampleQueries = [
    'confidence building activities for shy kids',
    'basketball programs for 8 year olds',
    'educational entertainment for children',
    'things to burn energy on rainy days',
    'martial arts for beginners',
    'creative activities for artistic kids',
  ];

  const handleExampleClick = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <form onSubmit={handleSearch} className="space-y-4">
        {/* Main Search Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            What are you looking for?
          </label>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., confidence building activities, basketball for kids, educational fun..."
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Filters Row */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* City */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              City (optional)
            </label>
            <input
              type="text"
              value={city}
              onChange={(e) => setCity(e.target.value)}
              placeholder="e.g., Detroit, Troy, Birmingham..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Age Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Age Min
            </label>
            <input
              type="number"
              value={ageMin}
              onChange={(e) => setAgeMin(e.target.value ? parseInt(e.target.value) : '')}
              placeholder="e.g., 6"
              min="0"
              max="18"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Age Max
            </label>
            <input
              type="number"
              value={ageMax}
              onChange={(e) => setAgeMax(e.target.value ? parseInt(e.target.value) : '')}
              placeholder="e.g., 10"
              min="0"
              max="18"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Category */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Category (optional)
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Categories</option>
              <option value="sports">Sports</option>
              <option value="arts">Arts & Crafts</option>
              <option value="education">Educational</option>
              <option value="outdoor">Outdoor</option>
              <option value="music">Music</option>
              <option value="STEM">STEM</option>
              <option value="martial_arts">Martial Arts</option>
            </select>
          </div>
        </div>

        {/* Price Filter */}
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Price:</label>
          <div className="flex gap-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="price"
                checked={isFree === undefined}
                onChange={() => setIsFree(undefined)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">All</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="price"
                checked={isFree === true}
                onChange={() => setIsFree(true)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Free Only</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="price"
                checked={isFree === false}
                onChange={() => setIsFree(false)}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Paid</span>
            </label>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-semibold py-3 px-6 rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl"
        >
          🔍 Search Activities
        </button>
      </form>
    </div>
  );
};

export default HybridSearchBox;

