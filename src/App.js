import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Signup from './pages/Signup';
import VerifyToken from "./pages/VerifyToken";
import Profile from "./pages/Profile";
import EditProfile from './pages/EditProfile';
import DriverTravelPlans from "./pages/DriverTravelPlans"
import BookingForm from './pages/BookingForm';
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="auth/signup/" element={<Signup />} />
        <Route path="/verify" element={<VerifyToken />} />
        <Route path="/login" element={<Login />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/edit-profile" element={<EditProfile />} />
        <Route path="/travel-plans" element={<DriverTravelPlans />} />
        <Route path="/book" element={<BookingForm />} />
      </Routes>
    </Router>
  );
}
export default App;
