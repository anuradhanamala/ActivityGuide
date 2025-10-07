import React, { useState } from 'react';

interface UserProfileData {
  id: number;
  email: string;
  name: string;
  default_zip_code: string;
  max_distance_miles: number;
  children_ages: number[];
  preferred_categories: string[];
  preferred_activity_types: string[];
  email_notifications: boolean;
  weekly_digest: boolean;
}

const UserProfile: React.FC = () => {
  const [profile, setProfile] = useState<UserProfileData>({
    id: 1,
    email: 'parent@example.com',
    name: 'Sarah Johnson',
    default_zip_code: '48104',
    max_distance_miles: 25,
    children_ages: [4, 7],
    preferred_categories: ['education', 'outdoor', 'family'],
    preferred_activity_types: ['indoor', 'outdoor'],
    email_notifications: true,
    weekly_digest: true
  });

  const [isEditing, setIsEditing] = useState(false);

  const handleSave = () => {
    // In a real app, this would save to the backend
    console.log('Saving profile:', profile);
    setIsEditing(false);
  };

  const addChildAge = () => {
    setProfile(prev => ({
      ...prev,
      children_ages: [...prev.children_ages, 5]
    }));
  };

  const removeChildAge = (index: number) => {
    setProfile(prev => ({
      ...prev,
      children_ages: prev.children_ages.filter((_, i) => i !== index)
    }));
  };

  const updateChildAge = (index: number, age: number) => {
    setProfile(prev => ({
      ...prev,
      children_ages: prev.children_ages.map((a, i) => i === index ? age : a)
    }));
  };

  const toggleCategory = (category: string) => {
    setProfile(prev => ({
      ...prev,
      preferred_categories: prev.preferred_categories.includes(category)
        ? prev.preferred_categories.filter(c => c !== category)
        : [...prev.preferred_categories, category]
    }));
  };

  const toggleActivityType = (type: string) => {
    setProfile(prev => ({
      ...prev,
      preferred_activity_types: prev.preferred_activity_types.includes(type)
        ? prev.preferred_activity_types.filter(t => t !== type)
        : [...prev.preferred_activity_types, type]
    }));
  };

  const categories = [
    'family', 'kids', 'education', 'entertainment', 'sports', 
    'arts', 'music', 'museum', 'outdoor', 'indoor'
  ];

  const activityTypes = ['indoor', 'outdoor'];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900 flex items-center">
            <span className="text-blue-600 mr-2 font-bold">👤</span>
            My Profile
          </h1>
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
          >
            {isEditing ? 'Cancel' : 'Edit Profile'}
          </button>
        </div>

        <div className="space-y-6">
          {/* Basic Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Name
                </label>
                <input
                  type="text"
                  value={profile.name}
                  onChange={(e) => setProfile(prev => ({ ...prev, name: e.target.value }))}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-50"
                />
              </div>
            </div>
          </div>

          {/* Location Preferences */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span className="text-red-600 mr-2 font-bold">📍</span>
              Location Preferences
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Default ZIP Code
                </label>
                <input
                  type="text"
                  value={profile.default_zip_code}
                  onChange={(e) => setProfile(prev => ({ ...prev, default_zip_code: e.target.value }))}
                  disabled={!isEditing}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-50"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Distance (miles)
                </label>
                <input
                  type="number"
                  value={profile.max_distance_miles}
                  onChange={(e) => setProfile(prev => ({ ...prev, max_distance_miles: parseInt(e.target.value) }))}
                  disabled={!isEditing}
                  min="1"
                  max="100"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-50"
                />
              </div>
            </div>
          </div>

          {/* Children Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span className="text-blue-600 mr-2 font-bold">👥</span>
              Children's Ages
            </h2>
            <div className="space-y-3">
              {profile.children_ages.map((age, index) => (
                <div key={index} className="flex items-center space-x-3">
                  <input
                    type="number"
                    value={age}
                    onChange={(e) => updateChildAge(index, parseInt(e.target.value))}
                    disabled={!isEditing}
                    min="0"
                    max="18"
                    className="w-20 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-gray-50"
                  />
                  <span className="text-gray-600">years old</span>
                  {isEditing && (
                    <button
                      onClick={() => removeChildAge(index)}
                      className="text-red-600 hover:text-red-700"
                    >
                      Remove
                    </button>
                  )}
                </div>
              ))}
              {isEditing && (
                <button
                  onClick={addChildAge}
                  className="text-primary-600 hover:text-primary-700 font-medium"
                >
                  + Add Child
                </button>
              )}
            </div>
          </div>

          {/* Category Preferences */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Preferred Categories</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
              {categories.map((category) => (
                <label key={category} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={profile.preferred_categories.includes(category)}
                    onChange={() => toggleCategory(category)}
                    disabled={!isEditing}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700 capitalize">{category}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Activity Type Preferences */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Activity Type Preferences</h2>
            <div className="space-y-2">
              {activityTypes.map((type) => (
                <label key={type} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={profile.preferred_activity_types.includes(type)}
                    onChange={() => toggleActivityType(type)}
                    disabled={!isEditing}
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="text-sm text-gray-700 capitalize">{type}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Notification Preferences */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <span className="text-red-600 mr-2 font-bold">🔔</span>
              Notification Preferences
            </h2>
            <div className="space-y-3">
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={profile.email_notifications}
                  onChange={(e) => setProfile(prev => ({ ...prev, email_notifications: e.target.checked }))}
                  disabled={!isEditing}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Email notifications for new activities</span>
              </label>
              <label className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={profile.weekly_digest}
                  onChange={(e) => setProfile(prev => ({ ...prev, weekly_digest: e.target.checked }))}
                  disabled={!isEditing}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700">Weekly digest of top weekend picks</span>
              </label>
            </div>
          </div>
        </div>

        {isEditing && (
          <div className="flex justify-end space-x-3 mt-8 pt-6 border-t">
            <button
              onClick={() => setIsEditing(false)}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
            >
              Save Changes
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default UserProfile;

