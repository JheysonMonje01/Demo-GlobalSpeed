// GestionPPPoE.jsx
import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import ModalActivarServicio from '../../components/ModalActivarServicio';

const estadoColor = (estado) => {
  switch (estado) {
    case 'libre': return 'bg-green-100 text-green-700';
    case 'asignada': return 'bg-blue-100 text-blue-700';
    case 'preactivacion': return 'bg-yellow-100 text-yellow-700';
    case 'activo': return 'bg-emerald-100 text-emerald-700';
    case 'inactivo': return 'bg-gray-200 text-gray-800';
    case 'liberado': return 'bg-red-100 text-red-700';
    default: return 'bg-slate-100 text-slate-800';
  }
};

const GestionPPPoE = () => {
  const [contratos, setContratos] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [planes, setPlanes] = useState([]);
  const [pppoeUsuarios, setPppoeUsuarios] = useState([]);
  const [modalContratoId, setModalContratoId] = useState(null);
  const [filtro, setFiltro] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('');
  const [filtroPlan, setFiltroPlan] = useState('');
  const [onus, setOnus] = useState([]);

  const cargarDatos = async () => {
    try {
      const [resContratos, resClientes, resPlanes, resPppoe, resOnus] = await Promise.all([
        fetch('http://localhost:5006/contratos'),
        fetch('http://localhost:5001/clientes'),
        fetch('http://localhost:5005/planes'),
        fetch('http://localhost:5007/pppoe'),
        fetch('http://localhost:5004/onus')
      ]);

      const [contratosData, clientesData, planesData, pppoeData, onusData] = await Promise.all([
        resContratos.json(), resClientes.json(), resPlanes.json(), resPppoe.json(), resOnus.json()
      ]);

      setContratos(contratosData);
      setClientes(clientesData);
      setPlanes(planesData.data || []);
      setPppoeUsuarios(pppoeData.usuarios_pppoe || []);
      setOnus(onusData || []);
    } catch (err) {
      toast.error('Error al cargar datos');
    }
  };

  useEffect(() => { cargarDatos(); }, []);

  const getCliente = (id) => clientes.find(c => c.id_cliente === id);
  const getPlan = (id) => Array.isArray(planes) ? planes.find(p => p.id_plan === id) : null;
  const getEstadoServicio = (idContrato) => getUsuarioPPPoE(idContrato) ? 'activo' : 'no activado';
  const tienePerfilPPPoE = (idContrato) => !!getUsuarioPPPoE(idContrato);
  const getEstadoOnu = (idContrato) => onus.find(o => o.id_contrato === idContrato)?.estado ?? 'no asignada';
  const getUsuarioPPPoE = (idContrato) => pppoeUsuarios.find(u => u.id_contrato === idContrato);

  const contratosFiltrados = contratos.filter(c => {
    const cliente = getCliente(c.id_cliente);
    const coincideNombre = `${cliente?.persona?.nombre ?? ''} ${cliente?.persona?.apellido ?? ''}`.toLowerCase().includes(filtro.toLowerCase());
    const coincideEstado = filtroEstado ? getEstadoServicio(c.id_contrato) === filtroEstado : true;
    const coincidePlan = filtroPlan ? c.id_plan === parseInt(filtroPlan) : true;
    return coincideNombre && coincideEstado && coincidePlan;
  });

  return (
    <div className="bg-white shadow-xl rounded-2xl p-6 border-t-4 border-green-700">
      <h1 className="text-3xl font-bold text-green-700 mb-6 text-center">🧩 Gestión de Contratos y Activación de Servicio</h1>

      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <input type="text" placeholder="🔍 Buscar cliente..." value={filtro} onChange={(e) => setFiltro(e.target.value)}
          className="w-full md:w-1/3 px-4 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500" />

        <select value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}
          className="w-full md:w-1/4 px-4 py-2 border rounded-md shadow-sm">
          <option value="">🟡 Estado Servicio</option>
          <option value="activo">✅ Activo</option>
          <option value="no activado">❌ No activado</option>
        </select>

        <select value={filtroPlan} onChange={(e) => setFiltroPlan(e.target.value)}
          className="w-full md:w-1/4 px-4 py-2 border rounded-md shadow-sm">
          <option value="">📶 Plan de Servicio</option>
          {planes.map(plan => <option key={plan.id_plan} value={plan.id_plan}>{plan.nombre_plan}</option>)}
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full bg-white rounded-xl shadow-md">
          <thead className="bg-green-600 text-white rounded-t-xl">
            <tr>
              <th className="px-4 py-2 text-left">#ID</th>
              <th className="px-4 py-2 text-left">Cliente</th>
              <th className="px-4 py-2 text-left">Plan</th>
              <th className="px-4 py-2 text-left">Estado ONU</th>
              <th className="px-4 py-2 text-left">Estado Servicio</th>
              <th className="px-4 py-2 text-left">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {contratosFiltrados.map(c => {
              const cliente = getCliente(c.id_cliente);
              const plan = getPlan(c.id_plan);
              const usuarioPPPoE = getUsuarioPPPoE(c.id_contrato);
              return (
                <tr key={c.id_contrato} className="border-b hover:bg-gray-50">
                  <td className="px-4 py-2 font-semibold">#{String(c.id_contrato).padStart(3, '0')}</td>
                  <td className="px-4 py-2">{cliente?.persona?.nombre} {cliente?.persona?.apellido}</td>
                  <td className="px-4 py-2 text-green-600">{plan?.nombre_plan || 'N/A'}</td>
                  <td className="px-4 py-2">
                    <span className={`px-2 py-1 rounded-full text-sm font-semibold ${estadoColor(getEstadoOnu(c.id_contrato))}`}>
                      {getEstadoOnu(c.id_contrato).replaceAll('_', ' ')}
                    </span>
                  </td>
                  <td className="px-4 py-2">
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold flex items-center justify-center w-fit gap-2 ${getEstadoServicio(c.id_contrato) === 'activo' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                      <div className={`w-3 h-3 rounded-full ${getEstadoServicio(c.id_contrato) === 'activo' ? 'bg-green-500' : 'bg-red-500'}`}></div>
                      {getEstadoServicio(c.id_contrato)}
                    </span>
                  </td>
                  <td className="text-center">
                    {usuarioPPPoE ? (
                      <div className="flex flex-col items-center gap-1">
                        <span className="text-green-700 font-semibold text-sm">Usuario PPPoE:</span>
                        <span className="inline-block bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-semibold">
                          {usuarioPPPoE.usuario_pppoe}
                        </span>
                      </div>
                    ) : (
                      <button onClick={() => setModalContratoId(c.id_contrato)}
                        className="bg-neutral-900 hover:bg-neutral-800 text-white px-4 py-2 rounded-lg flex items-center gap-2 mx-auto">
                        ⚡ Activar perfil PPPoE
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="flex justify-center mt-6">
        <nav className="flex items-center space-x-2">
          <button className="px-3 py-1 rounded-lg bg-gray-200 hover:bg-gray-300">&laquo;</button>
          {[1, 2, 3].map(n => (
            <button key={n} className="px-3 py-1 rounded-lg bg-green-600 text-white hover:bg-green-700">{n}</button>
          ))}
          <button className="px-3 py-1 rounded-lg bg-gray-200 hover:bg-gray-300">&raquo;</button>
        </nav>
      </div>

      {modalContratoId && (
        <ModalActivarServicio
          contratoId={modalContratoId}
          onClose={() => setModalContratoId(null)}
          onSuccess={() => {
            setModalContratoId(null);
            cargarDatos();
          }}
        />
      )}
    </div>
  );
};

export default GestionPPPoE;
