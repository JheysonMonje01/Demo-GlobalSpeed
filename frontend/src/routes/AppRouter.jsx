import { BrowserRouter, Routes, Route } from 'react-router-dom';
import LoginPage from '../auth/LoginPage';
import AdminRoutes from './AdminRoutes';
import TecnicoRoutes from './TecnicoRoutes';
import ClienteRoutes from './ClienteRoutes';
import ProtectedRoute from '../components/ProtectedRoute';
import UnauthorizedPage from '../pages/UnauthorizedPage'; // crea una página simple si no existe
import RecuperarContraseña from '../auth/RecuperarContraseña';
import RestablecerContraseña from '../auth/RestablecerContraseña';
import HomePage from '../pages/HomePage';

const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
         {/* Recuperación de contraseña (públicas) */}
        <Route path="/recuperar" element={<RecuperarContraseña />} />
        <Route path="/restablecer" element={<RestablecerContraseña />} />

        <Route
          path="/admin/*"
          element={
            <ProtectedRoute allowedRoles={[1]}>
              <AdminRoutes />
            </ProtectedRoute>
          }
        />
        <Route
          path="/tecnico/*"
          element={
            <ProtectedRoute allowedRoles={[2]}>
              <TecnicoRoutes />
            </ProtectedRoute>
          }
        />
        <Route
          path="/cliente/*"
          element={
            <ProtectedRoute allowedRoles={[3]}>
              <ClienteRoutes />
            </ProtectedRoute>
          }
        />
        <Route path="/unauthorized" element={<UnauthorizedPage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;
