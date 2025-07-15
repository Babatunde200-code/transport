import React, { useState } from 'react';
import axios from 'axios';
import { getAuthToken } from '../services/auth';

const BookingForm = () => {
  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    travel_date: '',
  });
  const [message, setMessage] = useState('');

  const handleChange = e => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      await axios.post('http://127.0.0.1:8000/api/booking/book/', formData, {
        headers: {
          Authorization: `Bearer ${getAuthToken()}`
        }
      });
      setMessage('Booking successful! Confirmation email sent.');
      setFormData({ origin: '', destination: '', travel_date: '' });
    } catch (error) {
      setMessage('Error creating booking. Please try again.');
    }
  };

  return (
    <div className="p-4 max-w-md mx-auto">
      <h2 className="text-2xl font-bold mb-4">Book a Ride</h2>
      {message && <p className="mb-2 text-green-600">{message}</p>}
      <form onSubmit={handleSubmit} className="grid gap-4">
        <input type="text" name="origin" placeholder="Origin" value={formData.origin} onChange={handleChange} className="p-2 border rounded" required />
        <input type="text" name="destination" placeholder="Destination" value={formData.destination} onChange={handleChange} className="p-2 border rounded" required />
        <input type="date" name="travel_date" value={formData.travel_date} onChange={handleChange} className="p-2 border rounded" required />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">Submit Booking</button>
      </form>
    </div>
  );
};

export default BookingForm;
