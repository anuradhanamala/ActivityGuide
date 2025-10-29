import React, { useState } from 'react';
import { Plus, Calendar, MapPin, DollarSign, Users } from 'lucide-react';

interface SubmissionData {
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  location_name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  category: string;
  age_range_min: number | '';
  age_range_max: number | '';
  is_indoor: boolean;
  is_free: boolean;
  price: number | '';
}

const ProviderSubmission: React.FC = () => {
  const [formData, setFormData] = useState<SubmissionData>({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
    location_name: '',
    address: '',
    city: '',
    state: 'MI',
    zip_code: '',
    contact_name: '',
    contact_email: '',
    contact_phone: '',
    category: '',
    age_range_min: '',
    age_range_max: '',
    is_indoor: true,
    is_free: true,
    price: ''
  });

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      // In a real app, this would submit to the backend
      console.log('Submitting event:', formData);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      setSubmitted(true);
    } catch (error) {
      console.error('Error submitting event:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (field: keyof SubmissionData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  if (submitted) {
    return (
      <div className="max-w-2xl mx-auto">
        <div className="bg-green-50 border border-green-200 rounded-lg p-8 text-center">
          <div className="text-green-600 mb-4">
            <Plus className="h-16 w-16 mx-auto" />
          </div>
          <h2 className="text-2xl font-bold text-green-900 mb-4">Thank You!</h2>
          <p className="text-green-800 mb-6">
            Your event submission has been received and is under review. 
            We'll notify you via email once it's been approved.
          </p>
          <button
            onClick={() => setSubmitted(false)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors"
          >
            Submit Another Event
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
          <Plus className="h-6 w-6 text-primary-600 mr-2" />
          Submit Your Event
        </h1>
        
        <p className="text-gray-600 mb-8">
          Help other families discover great activities by submitting your event. 
          All submissions are reviewed before being published.
        </p>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Event Details */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Calendar className="h-5 w-5 text-primary-600 mr-2" />
              Event Details
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Event Title *
                </label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => handleInputChange('title', e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., Storytime at Community Center"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Description *
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  required
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Describe what families can expect from this event..."
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Start Date & Time *
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.start_time}
                    onChange={(e) => handleInputChange('start_time', e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    End Date & Time
                  </label>
                  <input
                    type="datetime-local"
                    value={formData.end_time}
                    onChange={(e) => handleInputChange('end_time', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Location */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <MapPin className="h-5 w-5 text-primary-600 mr-2" />
              Location
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Venue Name *
                </label>
                <input
                  type="text"
                  value={formData.location_name}
                  onChange={(e) => handleInputChange('location_name', e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="e.g., Ann Arbor Community Center"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Address *
                </label>
                <input
                  type="text"
                  value={formData.address}
                  onChange={(e) => handleInputChange('address', e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="123 Main Street"
                />
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    City *
                  </label>
                  <input
                    type="text"
                    value={formData.city}
                    onChange={(e) => handleInputChange('city', e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Ann Arbor"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    State *
                  </label>
                  <input
                    type="text"
                    value={formData.state}
                    onChange={(e) => handleInputChange('state', e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="MI"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    ZIP Code *
                  </label>
                  <input
                    type="text"
                    value={formData.zip_code}
                    onChange={(e) => handleInputChange('zip_code', e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="48104"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Users className="h-5 w-5 text-primary-600 mr-2" />
              Contact Information
            </h2>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contact Name *
                  </label>
                  <input
                    type="text"
                    value={formData.contact_name}
                    onChange={(e) => handleInputChange('contact_name', e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="Your name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Contact Email *
                  </label>
                  <input
                    type="email"
                    value={formData.contact_email}
                    onChange={(e) => handleInputChange('contact_email', e.target.value)}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="your@email.com"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Contact Phone
                </label>
                <input
                  type="tel"
                  value={formData.contact_phone}
                  onChange={(e) => handleInputChange('contact_phone', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="(555) 123-4567"
                />
              </div>
            </div>
          </div>

          {/* Event Details */}
          <div>
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <DollarSign className="h-5 w-5 text-primary-600 mr-2" />
              Event Details
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Category *
                </label>
                <select
                  value={formData.category}
                  onChange={(e) => handleInputChange('category', e.target.value)}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">Select a category</option>
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
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Age
                  </label>
                  <input
                    type="number"
                    value={formData.age_range_min}
                    onChange={(e) => handleInputChange('age_range_min', e.target.value ? parseInt(e.target.value) : '')}
                    min="0"
                    max="18"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="0"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum Age
                  </label>
                  <input
                    type="number"
                    value={formData.age_range_max}
                    onChange={(e) => handleInputChange('age_range_max', e.target.value ? parseInt(e.target.value) : '')}
                    min="0"
                    max="18"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="18"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Location Type
                </label>
                <div className="flex space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      checked={formData.is_indoor}
                      onChange={() => handleInputChange('is_indoor', true)}
                      className="text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-700">Indoor</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      checked={!formData.is_indoor}
                      onChange={() => handleInputChange('is_indoor', false)}
                      className="text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-700">Outdoor</span>
                  </label>
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Pricing
                </label>
                <div className="space-y-3">
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      checked={formData.is_free}
                      onChange={() => handleInputChange('is_free', true)}
                      className="text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-700">Free event</span>
                  </label>
                  <label className="flex items-center space-x-2">
                    <input
                      type="radio"
                      checked={!formData.is_free}
                      onChange={() => handleInputChange('is_free', false)}
                      className="text-primary-600 focus:ring-primary-500"
                    />
                    <span className="text-sm text-gray-700">Paid event</span>
                  </label>
                  
                  {!formData.is_free && (
                    <div>
                      <input
                        type="number"
                        value={formData.price}
                        onChange={(e) => handleInputChange('price', e.target.value ? parseFloat(e.target.value) : '')}
                        min="0"
                        step="0.01"
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                        placeholder="Price per person"
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-3 pt-6 border-t">
            <button
              type="button"
              onClick={() => window.history.back()}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Submitting...' : 'Submit Event'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProviderSubmission;
