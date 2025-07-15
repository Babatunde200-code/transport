import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { getAuthToken } from '../services/auth';
import { Link } from 'react-router-dom';

const DriverTravelPlans = () => {
  const [plans, setPlans] = useState([]);
  const [loading, setLoading] = useState(true);

  const [formData, setFormData] = useState({
    origin: '',
    destination: '',
    departure_date: ''
  });

  const fetchPlans = async () => {
    try {
      const res = await axios.get('http://127.0.0.1:8000/api/travel/plans/', {
        headers: { Authorization: `Bearer ${getAuthToken()}` }
      });
      setPlans(res.data);
    } catch (err) {
      console.error('Error fetching plans:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://127.0.0.1:8000/api/travel/plans/', formData, {
        headers: {
          Authorization: `Bearer ${getAuthToken()}`
        }
      });
      setFormData({ origin: '', destination: '', departure_date: '' });
      fetchPlans(); // refresh list
    } catch (err) {
      console.error('Error creating plan:', err);
    }
  };

  useEffect(() => {
    fetchPlans();
  }, []);

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">Create a Travel Plan</h2>
      <form onSubmit={handleSubmit} className="grid gap-3 max-w-md mb-8">
        <input
          type="text"
          name="origin"
          value={formData.origin}
          onChange={handleChange}
          placeholder="Origin"
          required
          className="border px-3 py-2 rounded"
        />
        <input
          type="text"
          name="destination"
          value={formData.destination}
          onChange={handleChange}
          placeholder="Destination"
          required
          className="border px-3 py-2 rounded"
        />
        <input
          type="date"
          name="departure_date"
          value={formData.departure_date}
          onChange={handleChange}
          required
          className="border px-3 py-2 rounded"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded">
          Add Travel Plan
        </button>
      </form>

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">My Travel Plans</h2>
        <Link to="/available-plans" className="text-blue-600 underline">
          View Available Rides
        </Link>
      </div>

      {loading ? <p>Loading...</p> : (
        <div className="grid gap-4">
          {plans.length === 0 ? <p>No travel plans yet.</p> :
            plans.map(plan => (
              <div key={plan.id} className="border p-4 rounded shadow">
                <p><strong>From:</strong> {plan.origin}</p>
                <p><strong>To:</strong> {plan.destination}</p>
                <p><strong>Date:</strong> {plan.departure_date}</p>
                <p><strong>Status:</strong> {plan.approved ? "Approved" : "Pending"}</p>
              </div>
            ))
          }
        </div>
      )}
    </div>
  );
};

export default DriverTravelPlans;
