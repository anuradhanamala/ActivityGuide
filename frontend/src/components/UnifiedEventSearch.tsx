import React, { useState } from 'react';

export interface UnifiedSearchFilters {
  zipCode: string;
  city: string;
  startDate: string;
  endDate: string;
  categories: string[];
  ageMin: number | '';
  ageMax: number | '';
  isIndoor: boolean | null;
  isFree: boolean | null;
  eventType: string;
  sources: string[];
}

interface UnifiedEventSearchProps {
  onSearch?: (filters: UnifiedSearchFilters) => void;
}

const UnifiedEventSearch: React.FC<UnifiedEventSearchProps> = ({ onSearch }) => {
  const [filters, setFilters] = useState<UnifiedSearchFilters>({
    zipCode: '',
    city: 'Troy',
    startDate: '',
    endDate: '',
    categories: [],
    ageMin: '',
    ageMax: '',
    isIndoor: null,
    isFree: null,
    eventType: '',
    sources: []
  });

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(filters);
    }
  };

  const handleFilterChange = (key: keyof UnifiedSearchFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const toggleCategory = (category: string) => {
    setFilters(prev => ({
      ...prev,
      categories: prev.categories.includes(category)
        ? prev.categories.filter(c => c !== category)
        : [...prev.categories, category]
    }));
  };

  const toggleSource = (source: string) => {
    setFilters(prev => ({
      ...prev,
      sources: prev.sources.includes(source)
        ? prev.sources.filter(s => s !== source)
        : [...prev.sources, source]
    }));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <span className="text-blue-600 mr-2 font-bold">🔍</span>
        Find Activities (All Sources)
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Primary Search Fields */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              City
            </label>
            <input
              type="text"
              value={filters.city}
              onChange={(e) => handleFilterChange('city', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Troy"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ZIP Code (Optional)
            </label>
            <input
              type="text"
              value={filters.zipCode}
              onChange={(e) => handleFilterChange('zipCode', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="48083"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Min Age
            </label>
            <select
              value={filters.ageMin}
              onChange={(e) => handleFilterChange('ageMin', e.target.value ? parseInt(e.target.value) : '')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Any Age</option>
              <option value="0">0 years</option>
              <option value="2">2 years</option>
              <option value="5">5 years</option>
              <option value="8">8 years</option>
              <option value="12">12 years</option>
              <option value="16">16 years</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Age
            </label>
            <select
              value={filters.ageMax}
              onChange={(e) => handleFilterChange('ageMax', e.target.value ? parseInt(e.target.value) : '')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">Any Age</option>
              <option value="2">2 years</option>
              <option value="5">5 years</option>
              <option value="8">8 years</option>
              <option value="12">12 years</option>
              <option value="16">16 years</option>
              <option value="18">18 years</option>
            </select>
          </div>
        </div>

        {/* Category Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Categories (Select Multiple)
          </label>
          <div className="flex flex-wrap gap-2">
            {['family', 'sports', 'arts', 'music', 'dance', 'education', 'stem', 'outdoor', 'playgrounds'].map(cat => (
              <button
                key={cat}
                type="button"
                onClick={() => toggleCategory(cat)}
                className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                  filters.categories.includes(cat)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </button>
            ))}
          </div>
        </div>
        
        {showAdvanced && (
          <div className="space-y-4 pt-4 border-t">
            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Start Date
                </label>
                <input
                  type="date"
                  value={filters.startDate}
                  onChange={(e) => handleFilterChange('startDate', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  End Date
                </label>
                <input
                  type="date"
                  value={filters.endDate}
                  onChange={(e) => handleFilterChange('endDate', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* Location & Price Filters */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location Type
                </label>
                <select
                  value={filters.isIndoor === null ? '' : filters.isIndoor ? 'indoor' : 'outdoor'}
                  onChange={(e) => handleFilterChange('isIndoor', e.target.value === '' ? null : e.target.value === 'indoor')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Any Location</option>
                  <option value="indoor">Indoor</option>
                  <option value="outdoor">Outdoor</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Price
                </label>
                <select
                  value={filters.isFree === null ? '' : filters.isFree ? 'free' : 'paid'}
                  onChange={(e) => handleFilterChange('isFree', e.target.value === '' ? null : e.target.value === 'free')}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Any Price</option>
                  <option value="free">Free Only</option>
                  <option value="paid">Paid Events</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Event Type
                </label>
                <select
                  value={filters.eventType}
                  onChange={(e) => handleFilterChange('eventType', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All Types</option>
                  <option value="event">Events</option>
                  <option value="venue">Venues</option>
                  <option value="class">Classes</option>
                  <option value="program">Programs</option>
                </select>
              </div>
            </div>

            {/* Data Source Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data Sources (Leave empty for all)
              </label>
              <div className="flex flex-wrap gap-2">
                {['yelp', 'eventbrite', 'google_places', 'meetup', 'recreation_gov', 'openstreetmap'].map(source => (
                  <button
                    key={source}
                    type="button"
                    onClick={() => toggleSource(source)}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      filters.sources.includes(source)
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                    }`}
                  >
                    {source.replace('_', ' ').toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
        
        <div className="flex items-center justify-between pt-4">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-blue-600 hover:text-blue-700 transition-colors"
          >
            <span className="mr-2 font-bold">⚙️</span>
            {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
          </button>
          
          <button
            type="submit"
            className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors shadow-md hover:shadow-lg"
          >
            <span className="font-bold">🔍</span>
            <span>Search All Sources</span>
          </button>
        </div>
      </form>

      {/* Info Banner */}
      <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Searching across:</strong> Yelp, Eventbrite, Google Places, Meetup, Recreation.gov, and more!
        </p>
      </div>
    </div>
  );
};

export default UnifiedEventSearch;
