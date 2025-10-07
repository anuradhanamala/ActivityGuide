import React, { useState } from 'react';

export interface SearchFilters {
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

interface EventSearchProps {
  onSearch?: (filters: SearchFilters) => void;
}

const EventSearch: React.FC<EventSearchProps> = ({ onSearch }) => {
  const [filters, setFilters] = useState<SearchFilters>({
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

  const [showAdvanced, setShowAdvanced] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(filters);
    }
  };

  const handleFilterChange = (key: keyof SearchFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <span className="text-red-600 mr-2 font-bold">📍</span>
        Find Family Activities
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ZIP Code
            </label>
            <input
              type="text"
              value={filters.zipCode}
              onChange={(e) => handleFilterChange('zipCode', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="48104"
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Start Date
            </label>
            <input
              type="date"
              value={filters.startDate}
              onChange={(e) => handleFilterChange('startDate', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Category
            </label>
            <select
              value={filters.category}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              <option value="family">Family</option>
              <option value="kids">Kids</option>
              <option value="education">Education</option>
              <option value="entertainment">Entertainment</option>
              <option value="sports">Sports</option>
              <option value="arts">Arts</option>
              <option value="music">Music</option>
              <option value="museum">Museum</option>
              <option value="outdoor">Outdoor</option>
              <option value="indoor">Indoor</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Max Age
            </label>
            <select
              value={filters.ageMax}
              onChange={(e) => handleFilterChange('ageMax', e.target.value ? parseInt(e.target.value) : '')}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
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
        
        {showAdvanced && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 pt-4 border-t">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Min Age
              </label>
              <input
                type="number"
                value={filters.ageMin}
                onChange={(e) => handleFilterChange('ageMin', e.target.value ? parseInt(e.target.value) : '')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                min="0"
                max="18"
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
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location Type
              </label>
              <select
                value={filters.isIndoor === null ? '' : filters.isIndoor ? 'indoor' : 'outdoor'}
                onChange={(e) => handleFilterChange('isIndoor', e.target.value === '' ? null : e.target.value === 'indoor')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Any</option>
                <option value="indoor">Indoor</option>
                <option value="outdoor">Outdoor</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Price Range
              </label>
              <select
                value={filters.isFree === null ? '' : filters.isFree ? 'free' : 'paid'}
                onChange={(e) => handleFilterChange('isFree', e.target.value === '' ? null : e.target.value === 'free')}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">Any Price</option>
                <option value="free">Free Only</option>
                <option value="paid">Paid Events</option>
              </select>
            </div>
          </div>
        )}
        
        <div className="flex items-center justify-between pt-4">
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center text-primary-600 hover:text-primary-700 transition-colors"
          >
            <span className="mr-2 text-blue-600 font-bold">⚙</span>
            {showAdvanced ? 'Hide' : 'Show'} Advanced Filters
          </button>
          
          <button
            type="submit"
            className="flex items-center space-x-2 bg-primary-600 text-white px-6 py-3 rounded-lg hover:bg-primary-700 transition-colors"
          >
            <span className="text-white font-bold">SEARCH</span>
            <span>Search Activities</span>
          </button>
        </div>
      </form>
    </div>
  );
};

export default EventSearch;

