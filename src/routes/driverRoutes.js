import { Routes, Route } from 'react-router-dom';
import DriverTravelPlans from '../pages/DriverTravelPlans';
import CreateTravelPlan from '../pages/CreateTravelPlan';
import EditTravelPlan from '../pages/EditTravelPlan';

const DriverRoutes = () => {
  return (
    <Routes>
      <Route path="plans" element={<DriverTravelPlans />} />
      <Route path="plans/create" element={<CreateTravelPlan />} />
      <Route path="plans/:id/edit" element={<EditTravelPlan />} />
    </Routes>
  );
};

export default DriverRoutes;
