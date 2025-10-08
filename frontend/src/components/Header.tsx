import React from 'react';
import { Link } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-gray-900">ActivityGuide</span>
          </Link>
          
          <nav className="hidden md:flex items-center space-x-8">
            <Link to="/" className="text-gray-600 hover:text-blue-600 font-medium transition-colors">
              🔍 Find Activities
            </Link>
            <Link to="/parallel-ai" className="text-gray-600 hover:text-purple-600 transition-colors">
              ⚡ Parallel AI
            </Link>
            <Link to="/submit" className="text-gray-600 hover:text-primary-600 transition-colors">
              Submit Event
            </Link>
            <Link to="/profile" className="text-gray-600 hover:text-primary-600 transition-colors">
              My Profile
            </Link>
          </nav>
          
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

