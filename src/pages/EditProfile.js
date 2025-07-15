import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate} from 'react-router-dom';

const EditProfile = () => {
  const [formData, setFormData] = useState({
    full_name: '',
    phone_number: '',
    country: '',
  });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    axios.get('http://localhost:8000/auth/profile/', {
      headers: { Authorization: `Bearer ${token}` },
    }).then(res => {
      setFormData(res.data);
      setLoading(false);
    }).catch(err => console.error(err));
  }, []);

  const handleChange = e => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    const token = localStorage.getItem('access_token');
    try {
      await axios.put('http://localhost:8000/auth/profile/', formData, {
        headers: { Authorization: `Bearer ${token}` },
      });
      navigate('/profile');
    } catch (err) {
      console.error('Update failed', err);
    }
  };

  if (loading) return <p className="text-center mt-10">Loading...</p>;

  return (

    <div className="min-h-screen flex items-center justify-center p-4 bg-gray-100">
      
      <form onSubmit={handleSubmit} className="bg-white p-8 shadow rounded-lg max-w-md w-full">
        <h2 className="text-xl font-semibold mb-4">Edit Profile</h2>

        <label className="block mb-2 text-sm font-medium">Full Name</label>
        <input
          type="text"
          name="full_name"
          value={formData.full_name}
          onChange={handleChange}
          className="w-full p-3 border rounded mb-4"
        />

        <label className="block mb-2 text-sm font-medium">Phone Number</label>
        <input
          type="text"
          name="phone_number"
          value={formData.phone_number}
          onChange={handleChange}
          className="w-full p-3 border rounded mb-4"
        />

        <label className="block mb-2 text-sm font-medium">Country</label>
        <input
          type="text"
          name="country"
          value={formData.country}
          onChange={handleChange}
          className="w-full p-3 border rounded mb-6"
        />

        <button type="submit" className="w-full bg-blue-600 text-white py-2 rounded">
          Save Changes
          
        </button>
        
      </form>

      

    </div>
  );
};

export default EditProfile;
