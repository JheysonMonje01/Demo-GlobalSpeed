import React, { useEffect, useState } from 'react';
import { Trash2, PlusCircle, Edit3, Users } from 'lucide-react';
import { toast } from 'react-toastify';
import Swal from 'sweetalert2';
import ModalAgregarOnu from '../../components/ModalAgregarOnu';
import ModalEditarOnu from '../../components/ModalEditarOnu';



const estados = [
  { label: 'Todos', value: '' },
  { label: 'Libre', value: 'libre' },
  { label: 'Asignado', value: 'asignado' },
  { label: 'Preactivacion', value: 'preactivacion' },
  { label: 'Activa', value: 'activa' },
  { label: 'Inactiva', value: 'inactiva' },
  { label: 'Liberada', value: 'liberada' },
];

const OnuInventarioPage = () => {
  const [onus, setOnus] = useState([]);
  const [resumen, setResumen] = useState({ total: 0, libres: 0, activas: 0 });
  const [busqueda, setBusqueda] = useState('');
  const [estado, setEstado] = useState('');
  const [pagina, setPagina] = useState(1);
  const elementosPorPagina = 10;
  const [mostrarModal, setMostrarModal] = useState(false);
  const [mostrarModalEditar, setMostrarModalEditar] = useState(false);
  const [onuSeleccionada, setOnuSeleccionada] = useState(null);

  const abrirModalEditar = (onu) => {
  setOnuSeleccionada(onu);
  setMostrarModalEditar(true);
};


  useEffect(() => {
    cargarResumen();
  }, []);

  useEffect(() => {
    cargarOnus();
  }, [busqueda, estado]);

  const cargarResumen = async () => {
    try {
      const res = await fetch('http://localhost:5004/onus/resumen');
      const data = await res.json();
      if (res.ok) setResumen(data);
      else toast.error(data.message);
    } catch (error) {
      toast.error('Error al cargar el resumen');
    }
  };

  const cargarOnus = async () => {
    try {
      const url = new URL('http://localhost:5004/onus/filtrar');
      if (busqueda) url.searchParams.append('q', busqueda);
      if (estado) url.searchParams.append('estado', estado);

      const res = await fetch(url);
      const data = await res.json();
      if (res.ok) setOnus(data);
      else toast.error(data.message);
    } catch (error) {
      toast.error('Error al cargar ONUs');
    }
  };

  const eliminarOnu = async (id) => {
    const resultado = await Swal.fire({
      title: '¿Eliminar ONU?',
      text: 'Esta acción no se puede deshacer',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    });

    if (!resultado.isConfirmed) return;

    try {
      const res = await fetch(`http://localhost:5004/onus/${id}`, { method: 'DELETE' });
      const data = await res.json();
      if (res.ok) {
        toast.success(data.message);
        cargarOnus();
      } else toast.error(data.message);
    } catch (err) {
      toast.error('Error al eliminar ONU');
    }
  };

  const totalPaginas = Math.ceil(onus.length / elementosPorPagina);
  const onusPaginados = onus.slice((pagina - 1) * elementosPorPagina, pagina * elementosPorPagina);

  const estadoColor = (estado) => {
    switch (estado) {
      case 'libre': return 'bg-green-100 text-green-700';
      case 'asignado': return 'bg-blue-100 text-blue-700';
      case "instalado": return "bg-gray-100 text-white-700";
      case 'preactivacion': return 'bg-yellow-100 text-yellow-700';
      case 'activo': return 'bg-emerald-500 text-emerald-900';
      case 'inactivo': return 'bg-gray-200 text-gray-800';
      case 'liberado': return 'bg-red-100 text-red-700';
      default: return 'bg-slate-100 text-slate-800';
    }
  };

  const capitalizar = (texto) => texto.charAt(0).toUpperCase() + texto.slice(1).toLowerCase();

  

  return (
    <div className="p-6">
      <div className="bg-white rounded-xl shadow-md p-6 border border-green-300">
        <div className="flex flex-col md:flex-row items-center justify-between mb-6 gap-4">
          <h1 className="text-3xl font-bold text-green-700">Inventario de ONUs</h1>
          <button
            onClick={() => setMostrarModal(true)}
            className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded shadow flex items-center"
            >
            <PlusCircle className="mr-2" size={18} /> Añadir ONU
            </button>

        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="flex items-center bg-blue-100 p-4 rounded shadow">
            <div className="bg-blue-500 text-white p-2 rounded-full mr-4">
              <Users size={24} />
            </div>
            <div>
              <div className="text-xl font-bold text-blue-700">{resumen.total}</div>
              <div className="text-sm text-blue-700">Total de ONUs</div>
            </div>
          </div>
          <div className="flex items-center bg-green-100 p-4 rounded shadow">
            <div className="bg-green-600 text-white p-2 rounded-full mr-4">
              <Users size={24} />
            </div>
            <div>
              <div className="text-xl font-bold text-green-700">{resumen.libres}</div>
              <div className="text-sm text-green-700">ONUs Libres</div>
            </div>
          </div>
          <div className="flex items-center bg-orange-100 p-4 rounded shadow">
            <div className="bg-orange-500 text-white p-2 rounded-full mr-4">
              <Users size={24} />
            </div>
            <div>
              <div className="text-xl font-bold text-orange-700">{resumen.activas}</div>
              <div className="text-sm text-orange-700">ONUs Activas</div>
            </div>
          </div>
        </div>

        <div className="flex flex-col md:flex-row gap-4 items-center mb-6">
          <input
            type="text"
            placeholder="Buscar por serial o modelo..."
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
            className="border border-gray-300 rounded px-4 py-2 w-full md:w-1/3 shadow-sm"
          />

          <select
            value={estado}
            onChange={(e) => setEstado(e.target.value)}
            className="border border-gray-300 rounded px-4 py-2 w-full md:w-1/4 shadow-sm"
          >
            {estados.map((op) => (
              <option key={op.value} value={op.value}>{op.label}</option>
            ))}
          </select>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left border border-black rounded-xl overflow-hidden">
            <thead className="bg-green-700 text-white">
              <tr>
                <th className="p-3 font-semibold">#</th>
                <th className="p-3 font-semibold">Serial</th>
                <th className="p-3 font-semibold">Modelo</th>
                <th className="p-3 font-semibold">Estado</th>
                <th className="p-3 font-semibold text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {onusPaginados.map((onu, index) => (
                <tr key={onu.id_onu} className="border-b hover:bg-green-50">
                  <td className="p-3">
                    <span className="inline-block w-6 h-6 text-center text-white bg-green-600 rounded-full">
                      {(pagina - 1) * elementosPorPagina + index + 1}
                    </span>
                  </td>
                  <td className="p-3 font-medium text-gray-800">{onu.serial}</td>
                  <td className="p-3">{onu.modelo_onu || '-'}</td>
                  <td className="p-3">
                    <span className={`px-3 py-1 text-xs font-semibold rounded-full ${estadoColor(onu.estado)}`}>
                      {capitalizar(onu.estado)}
                    </span>
                  </td>
                  <td className="p-3 text-center">
                    <div className="flex justify-center gap-3">
                      <button
                        className="text-blue-600 hover:text-blue-700"
                        title="Editar"
                        onClick={() => abrirModalEditar(onu)}
                        >
                        <Edit3 size={18} />
                        </button>

                      <button
                        className="text-red-500 hover:text-red-600"
                        title="Eliminar"
                        onClick={() => eliminarOnu(onu.id_onu)}
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {onusPaginados.length === 0 && (
                <tr>
                  <td colSpan="5" className="text-center py-4 text-gray-500">No hay resultados</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {totalPaginas > 1 && (
          <div className="flex justify-center mt-6 gap-2">
            {Array.from({ length: totalPaginas }, (_, i) => (
              <button
                key={i + 1}
                className={`px-3 py-1 rounded text-sm ${pagina === i + 1 ? 'bg-green-700 text-white' : 'border border-green-600 text-green-700'}`}
                onClick={() => setPagina(i + 1)}
              >
                {i + 1}
              </button>
            ))}
          </div>
        )}
      </div>
      {mostrarModal && (
        <ModalAgregarOnu
            onClose={() => setMostrarModal(false)}
            onSuccess={() => {
            cargarOnus();
            cargarResumen();
            
            }}
        />
        )}

        {mostrarModalEditar && (
        <ModalEditarOnu
            visible={mostrarModalEditar}
            onu={onuSeleccionada}
            onClose={() => {
            setMostrarModalEditar(false);
            setOnuSeleccionada(null);
            }}
            onSuccess={() => {
            cargarOnus();
            cargarResumen();
            setMostrarModalEditar(false);
            }}
        />
        )}


    </div>
  );
};

export default OnuInventarioPage;
