import { signup } from '../services/api';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Signup = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    full_name: '',
    username: '',
    email: '',
    phone_number: '',
    password: '',
  });

  

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleChange = e => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    setError('');
    setSuccess('');
  };

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/auth/signup/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (res.ok) {
        setSuccess('Signup successful. Check your email or phone for the verification code.');
        setTimeout(() => navigate("/verify"), 2000);
      } else {
        const data = await res.json();
        setError(data.message || 'Signup failed.');
      }
    } catch (err) {
      console.log(err)
      setError('Server error. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-tr from-blue-100 to-white px-4">
      <div className="bg-white shadow-2xl rounded-xl w-full max-w-md p-8">
        <h2 className="text-3xl font-semibold text-blue-700 text-center mb-6">Create an Account</h2>
        {error && <p className="text-red-600 text-sm mb-4 text-center">{error}</p>}
        {success && <p className="text-green-600 text-sm mb-4 text-center">{success}</p>}
        <form onSubmit={handleSubmit} className="space-y-4">
        <div>
            <label className="text-sm font-medium">Fullname</label>
            <input
              type="text"
              name="full_name"
              onChange={handleChange}
              required
              className="w-full mt-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          <div>
            <label className="text-sm font-medium">Username</label>
            <input
              type="text"
              name="username"
              onChange={handleChange}
              required
              className="w-full mt-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
          </div>
          <div>
            <label className="text-sm font-medium">Email</label>
            <input
              type="email"
              name="email"
              onChange={handleChange}
              required
              className="w-full mt-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Phone Number</label>
            <input
              type="tel"
              name="phone_number"
              onChange={handleChange}
              required
              className="w-full mt-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
          <div>
            <label className="text-sm font-medium">Password</label>
            <input
              type="password"
              name="password"
              onChange={handleChange}
              required
              className="w-full mt-1 p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400"
            />
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Sign Up
          </button>
        </form>
        <p className="mt-4 text-sm text-center">
          Already have an account?{' '}
          <a href="/login" className="text-blue-600 hover:underline">
            Login
          </a>
        </p>
      </div>
    </div>
  );
};

export default Signup;
