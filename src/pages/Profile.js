import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const Profile = () => {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
        const token = localStorage.getItem('access_token');
      if (!token) return navigate('/login');

      try {
        const response = await axios.get('http://localhost:8000/auth/profile/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        setUser(response.data);
      } catch (error) {
        console.error('Error fetching profile:', error);
      }
    };

    fetchProfile();
  }, [navigate]);

  if (!user) {
    return <div className="text-center text-gray-600 mt-10">Loading profile...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="bg-white shadow-xl rounded-2xl p-8 max-w-md w-full">
        <div className="text-center">
          {user.profile_picture ? (
            <img
              src={user.profile_picture}
              alt="Profile"
              className="w-24 h-24 mx-auto mb-4 rounded-full object-cover border border-gray-300"
            />
          ) : (
            <div className="w-24 h-24 mx-auto mb-4 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 text-3xl">
              {user.full_name ? user.full_name[0].toUpperCase() : 'U'}
            </div>
          )}
          <h2 className="text-2xl font-semibold text-gray-800">{user.full_name}</h2>
          <p className="text-gray-500">{user.email}</p>
        </div>
        <div className="mt-6">
          <div className="mb-4">
            <label className="text-sm text-gray-500">Phone Number</label>
            <p className="text-lg font-medium text-gray-800">{user.phone_number}</p>
          </div>
          <div className="mb-4">
            <label className="text-sm text-gray-500">Country</label>
            <p className="text-lg font-medium text-gray-800">{user.country}</p>
          </div>
        </div>
        <div className="mt-6 text-center">
          <button
            onClick={() => navigate('/edit-profile')}
            className="px-5 py-2 bg-blue-600 text-white rounded-xl shadow hover:bg-blue-700"
          >
            Edit Profile
          </button>
        </div>
      </div>
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-tr from-blue-100 to-white px-4">
      <div className="bg-white shadow-2xl rounded-xl w-full max-w-md p-8">
        <h2 className="text-3xl font-semibold text-blue-700 text-center mb-6">User Profile</h2>

        {/* Your user profile details here */}

        <div className="mt-6 text-center">
          <Link to="/driver/plans">
            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
              View Travel Plans
            </button>
          </Link>
        </div>
      </div>
    </div>
    </div>

  );
};

export default Profile;

