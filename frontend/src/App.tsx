import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import EventDetail from './components/EventDetail';
import UserProfile from './components/UserProfile';
import ProviderSubmission from './components/ProviderSubmission';
import FindActivities from './pages/FindActivities';
// import ParallelAIEvents from './pages/ParallelAIEvents'; // Hidden from UI
import SmartSearch from './pages/SmartSearch';
import './App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            {/* Default landing page - Activity Explorer */}
            <Route path="/" element={<SmartSearch />} />
            
            {/* Find Activities - Browse page */}
            <Route path="/browse" element={<FindActivities />} />
            
            {/* Parallel AI Events page - Hidden from UI */}
            {/* <Route path="/parallel-ai" element={<ParallelAIEvents />} /> */}
            
            {/* Other routes */}
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