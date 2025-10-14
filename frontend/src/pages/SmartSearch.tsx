import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import HybridSearchBox from '../components/HybridSearchBox';
import HybridSearchResults from '../components/HybridSearchResults';

const SmartSearch: React.FC = () => {
  const [searchResults, setSearchResults] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSearch = (results: any) => {
    setSearchResults(results);
  };

  const handleLoading = (loading: boolean) => {
    setIsLoading(loading);
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Search Box */}
      <HybridSearchBox onSearch={handleSearch} onLoading={handleLoading} />

      {/* Search Results */}
      <HybridSearchResults results={searchResults} isLoading={isLoading} />
    </div>
  );
};

export default SmartSearch;

