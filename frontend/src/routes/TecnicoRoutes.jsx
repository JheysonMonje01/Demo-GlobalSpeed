// src/routes/TecnicoRoutes.jsx
import { Routes, Route } from 'react-router-dom';
import TecnicoDashboard from '../pages/TecnicoDashboard';
import TecnicoLayout from '../layout/TecnicoLayout';
import PerfilUsuarioPage from '../pages/perfil/PerfilUsuarioPage';
import ClientesPage from '../pages/admin/ClientePage';
import PlanesSoloVista from '../pages/PlanesSoloVista';
import MonitoreoPage from '../pages/admin/MonitoreoPage';
import OrdenesTecnicoPage from '../pages/tecnico/OrdenesTecnicoPage';
import CajasNapListPage from '../pages/tecnico/CajasNapList';

const TecnicoRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<TecnicoLayout />}>
        <Route path="dashboard" element={<TecnicoDashboard />} />
        <Route path="perfil" element={<PerfilUsuarioPage />} />
        <Route path="clientes" element={<ClientesPage />} />
        <Route path="planes" element={<PlanesSoloVista />} />
        <Route path="monitoreo" element={<MonitoreoPage />} />
        <Route path="ordenes" element={<OrdenesTecnicoPage />} />
        <Route path="/red/naps" element={<CajasNapListPage />} />
        {/* Puedes agregar más rutas aquí */}
      </Route>
    </Routes>
  );
};
export default TecnicoRoutes;
