import { Routes, Route } from 'react-router-dom';
import AdminLayout from '../layout/AdminLayout';
import AdminDashboard from '../pages/AdminDashboard';
import EmpresaPage from '../pages/admin/EmpresaPage';
import PerfilUsuarioPage from '../pages/perfil/PerfilUsuarioPage';
import RegisterUser from '../pages/admin/RegisterUser';
import ListadoUsuarios from '../pages/admin/ListUser';
import UsuariosPage from '../pages/admin/UsuariosPage';
import DatacenterPage from '../pages/admin/DataCenterPage';
import OLTPage from '../pages/admin/OltPage';
import TarjetasOLTPage from '../pages/admin/TarjetasOLTPage';
import PuertosPonPage from '../pages/admin/PuertosPonPage';
import CajasNapPage from '../pages/admin/CajasNapPage';
//import ModuloCoberturaCliente from '../pages/admin/ModuloCoberturaCliente';
import RouterTable from '../pages/admin/RouterPage';
import IpPoolsPage from '../pages/admin/IpPoolsPage';
import VlanPage from '../pages/admin/VlanPage';
import OnuInventarioPage from '../pages/admin/OnuInventarioPage';
import PlanesPage from '../pages/admin/PlanesPage';
import ClientesPage from '../pages/admin/ClientePage';
import CrearContratoPage from '../pages/admin/CrearContratoPage';
import ContratosPage from '../pages/admin/ContratoPage';
import OnusPage from '../pages/admin/OnusPage';
import PaginaCobertura from '../pages/admin/PaginaCobertura';
import GestionPPPoE from '../pages/admin/GestionPPPoE';
import OrdenesInstalacionPage from '../pages/admin/OrdenesInstalacionPage';
import MetodoPagoPage from '../pages/admin/MetodoPagoPage';
import OrdenesPagoPage from '../pages/admin/OrdenesPagoPage';
import RegistrarPagoPage from '../pages/admin/RegistrarPagoPage';
import PagosPage from '../pages/admin/PagosPage';
import TablaPPPoE from '../pages/admin/TablaPPPoE';
import MonitoreoPage from '../pages/admin/MonitoreoPage';

const AdminRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<AdminLayout />}>
        <Route path="dashboard" element={<AdminDashboard />} />
        <Route path="empresa" element={<EmpresaPage />} />
        <Route path="perfil" element={<PerfilUsuarioPage />} />
        <Route path="usuarios" element={<UsuariosPage />} />
        <Route path="red/datacenter" element={<DatacenterPage />} />
        <Route path="red/olt" element={<OLTPage />} />
        <Route path="red/tarjetas" element={<TarjetasOLTPage/>} />
        <Route path="red/puertos" element={<PuertosPonPage/>} />
        <Route path="red/naps" element={<CajasNapPage/>} />
        <Route path="cobertura" element={<PaginaCobertura/>} />
        <Route path="/red/router" element={<RouterTable/>} />
        <Route path="/red/ip_pool" element={<IpPoolsPage/>} />
        <Route path="/red/vlan" element={<VlanPage/>} />
        <Route path="/onu/inventario" element={<OnuInventarioPage/>} />
        <Route path="/onu/gestion" element={<OnusPage/>} />
        <Route path="planes" element={<PlanesPage/>} />
        <Route path="clientes" element={<ClientesPage/>} />
        <Route path="contrato/crear" element={<CrearContratoPage/>} />
        <Route path="contrato/listar" element={<ContratosPage/>} />
        <Route path="gestion/pppoe" element={<GestionPPPoE/>} />
        <Route path="gestion/list" element={<TablaPPPoE/>} />
        <Route path="ordenes" element={<OrdenesInstalacionPage/>} />
        <Route path="metodo" element={<MetodoPagoPage/>} />
        <Route path="ordenes_pago" element={<OrdenesPagoPage/>} />
        <Route path="pagos/pago" element={<RegistrarPagoPage/>} />
        <Route path="pagos/ver_pagos" element={<PagosPage/>} />
        <Route path="monitoreo" element={<MonitoreoPage/>} />

        {/* Puedes agregar más rutas aquí */}
      </Route>
    </Routes>
  );
};

export default AdminRoutes;
