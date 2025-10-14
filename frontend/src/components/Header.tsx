import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <div className="flex items-center gap-2">
              <span className="text-3xl font-extrabold text-gray-900 tracking-tight">Activity Explorer</span>
              <span className="text-xs font-medium text-purple-600 bg-purple-50 px-2 py-1 rounded-full border border-purple-200">
                powered by AI
              </span>
            </div>
          </Link>
          
          <div className="flex items-center space-x-4">
            <Link 
              to="/submit" 
              className="flex items-center space-x-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
            >
              <span className="text-blue-600 font-bold">+</span>
              <span className="hidden sm:inline">Submit Event</span>
            </Link>
            <Link 
              to="/profile" 
              className="p-2 text-gray-600 hover:text-primary-600 transition-colors"
            >
              <span className="text-blue-600 font-bold">👤</span>
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;

