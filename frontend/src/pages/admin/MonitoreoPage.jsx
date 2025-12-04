import React, { useState, useEffect } from 'react';
import { FaSearch, FaSyncAlt, FaEye, FaEdit, FaTrash } from 'react-icons/fa';
import Swal from 'sweetalert2';
import ModalMonitoreo from '../../components/ModalMonitoreo';

const MonitoreoPage = () => {
  const [pppoeUsuarios, setPppoeUsuarios] = useState([]);
  const [planes, setPlanes] = useState([]);
  const [filtros, setFiltros] = useState({ nombre: '', plan: '', estado: '' });
  const [pagina, setPagina] = useState(1);
  const [modalOpen, setModalOpen] = useState(false);
  const [usuarioDetalle, setUsuarioDetalle] = useState(null);
  const elementosPorPagina = 10;

const verDetalle = async (idUsuarioPPPoE) => {
  const usuario = pppoeUsuarios.find(u => u.id_usuario_pppoe === idUsuarioPPPoE);

  if (!usuario || !usuario.estado) {
    Swal.fire({
      icon: "warning",
      title: "Usuario inactivo",
      text: "No se puede monitorear a un usuario inactivo.",
    });
    return;
  }

  try {
    const res = await fetch(`http://localhost:5007/gestion/pppoe/trafico/${idUsuarioPPPoE}`);
    const result = await res.json();

    if (result.status === "not_found") {
      Swal.fire({
        icon: "info",
        title: "Sin tráfico registrado",
        text: result.message || "No se encontró tráfico para este usuario.",
        confirmButtonColor: "#28a745"
      });
      return;
    }

    setUsuarioDetalle(usuario);
    setModalOpen(true);
  } catch (error) {
    console.error("Error al obtener tráfico:", error);
    Swal.fire({
      icon: "error",
      title: "Error de conexión",
      text: "No se pudo consultar el tráfico del usuario.",
    });
  }
};


  // Obtener usuarios PPPoE
  useEffect(() => {
    const obtenerUsuariosPPPoE = async () => {
      try {
        const res = await fetch("http://localhost:5007/pppoe/detalle");
        const result = await res.json();

        console.log("Usuarios PPPoE recibidos:", result);
        if (result.status === "success" && Array.isArray(result.data)) {
          setPppoeUsuarios(result.data);
        } else {
          setPppoeUsuarios([]);
        }
      } catch (error) {
        console.error("Error al obtener usuarios PPPoE:", error);
        setPppoeUsuarios([]);
      }
    };

    obtenerUsuariosPPPoE();
  }, []);

  // Obtener planes
  useEffect(() => {
    const obtenerPlanes = async () => {
      try {
        const res = await fetch("http://localhost:5005/planes");
        const result = await res.json();

        console.log("Planes recibidos:", result);
        if (result.status === "success" && Array.isArray(result.data)) {
          setPlanes(result.data);
        } else {
          setPlanes([]);
        }
      } catch (error) {
        console.error("Error al obtener planes:", error);
        setPlanes([]);
      }
    };

    obtenerPlanes();
  }, []);

  // Filtrado
  const usuariosFiltrados = pppoeUsuarios.filter((u) =>
    u.nombre_cliente.toLowerCase().includes(filtros.nombre.toLowerCase()) &&
    (filtros.plan ? u.nombre_plan === filtros.plan : true) &&
    (filtros.estado !== '' ? u.estado === (filtros.estado === 'activo') : true)
  );

  // Paginación
  const totalPaginas = Math.ceil(usuariosFiltrados.length / elementosPorPagina);
  const usuariosPaginados = usuariosFiltrados.slice((pagina - 1) * elementosPorPagina, pagina * elementosPorPagina);

  return (
    <div className="p-6 bg-white shadow-md rounded-xl border border-green-400">
      <h1 className="text-2xl font-bold text-green-600 mb-6">Gestión de Usuarios PPPoE</h1>

      {/* Filtros */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <input
          type="text"
          placeholder="🔍 Buscar por cliente"
          className="border border-green-300 p-2 rounded-lg w-full"
          value={filtros.nombre}
          onChange={(e) => {
            setFiltros({ ...filtros, nombre: e.target.value });
            setPagina(1);
          }}
        />

        <select
          className="border border-green-300 p-2 rounded-lg w-full"
          value={filtros.plan}
          onChange={(e) => {
            setFiltros({ ...filtros, plan: e.target.value });
            setPagina(1);
          }}
        >
          <option value="">📦 Filtrar por plan</option>
          {planes.map((plan, i) => (
            <option key={i} value={plan.nombre_plan}>
              {plan.nombre_plan}
            </option>
          ))}
        </select>

        <select
          className="border border-green-300 p-2 rounded-lg w-full"
          value={filtros.estado}
          onChange={(e) => {
            setFiltros({ ...filtros, estado: e.target.value });
            setPagina(1);
          }}
        >
          <option value="">⚙️ Estado</option>
          <option value="activo">Activo</option>
          <option value="inactivo">Inactivo</option>
        </select>

        <button
          onClick={() => {
            setFiltros({ nombre: '', plan: '', estado: '' });
            setPagina(1);
          }}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center justify-center"
        >
          <FaSyncAlt className="mr-2" /> Limpiar Filtros
        </button>
      </div>

      {/* Tabla */}
      <div className="overflow-x-auto">
        <table className="min-w-full bg-white border border-green-200 rounded-md">
          <thead>
            <tr className="bg-green-100 text-green-800">
              <th className="px-4 py-2 text-left">Cliente</th>
              <th className="px-4 py-2 text-left">Usuario PPPoE</th>
              <th className="px-4 py-2 text-left">Plan</th>
              <th className="px-4 py-2 text-left">IP Remota</th>
              <th className="px-4 py-2 text-left">Estado</th>
              <th className="px-4 py-2 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
  {usuariosPaginados.length > 0 ? (
    usuariosPaginados.map((u) => (
      <tr key={u.id_usuario_pppoe} className="border-t hover:bg-green-50">
        <td className="px-4 py-2">{u.nombre_cliente}</td>
        <td className="px-4 py-2">{u.usuario_pppoe}</td>
        <td className="px-4 py-2">{u.nombre_plan}</td>
        <td className="px-4 py-2">{u.ip_remota}</td>
        <td className="px-4 py-2">
          <span
            className={`px-2 py-1 rounded text-sm font-semibold ${
              u.estado ? 'bg-green-200 text-green-700' : 'bg-red-200 text-red-700'
            }`}
          >
            {u.estado ? 'Activo' : 'Inactivo'}
          </span>
        </td>
        <td className="p-2 text-center flex justify-center items-center space-x-2">
  {/* Ver detalle */}
  <button
  className="text-blue-600 hover:text-blue-800"
  title="Ver detalle"
  onClick={() => verDetalle(u.id_usuario_pppoe)}
>
  <FaEye />
</button>

</td>

      </tr>
    ))
  ) : (
    <tr>
      <td colSpan="6" className="text-center py-4 text-gray-500">
        No hay usuarios PPPoE registrados que coincidan con los filtros actuales.
      </td>
    </tr>
  )}
</tbody>

        </table>
      </div>

      {/* Paginación */}
      <div className="mt-6 flex justify-center items-center space-x-2">
  {/* Botón Anterior */}
  <button
    onClick={() => setPagina((prev) => Math.max(prev - 1, 1))}
    disabled={pagina === 1}
    className={`h-10 w-10 flex items-center justify-center rounded-full text-sm font-bold ${
      pagina === 1
        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
        : 'bg-green-600 text-white hover:bg-green-700'
    }`}
  >
    ‹
  </button>

  {/* Números de página con lógica para mostrar solo cercanas */}
  {Array.from({ length: totalPaginas }, (_, i) => i + 1)
    .filter((num) => num === 1 || num === totalPaginas || Math.abs(num - pagina) <= 2)
    .map((num, i, arr) => (
      <React.Fragment key={num}>
        {i > 0 && num - arr[i - 1] > 1 && (
          <span className="text-gray-400 px-1">…</span>
        )}
        <button
          onClick={() => setPagina(num)}
          className={`h-10 w-10 rounded-full text-sm font-bold ${
            pagina === num
              ? 'bg-green-700 text-white'
              : 'bg-green-100 text-green-700 hover:bg-green-200'
          }`}
        >
          {num}
        </button>
      </React.Fragment>
    ))}

  {/* Botón Siguiente */}
  <button
    onClick={() => setPagina((prev) => Math.min(prev + 1, totalPaginas))}
    disabled={pagina === totalPaginas}
    className={`h-10 w-10 flex items-center justify-center rounded-full text-sm font-bold ${
      pagina === totalPaginas
        ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
        : 'bg-green-600 text-white hover:bg-green-700'
    }`}
  >
    ›
  </button>
</div>
{modalOpen && usuarioDetalle && (
  <ModalMonitoreo
    usuario={usuarioDetalle}
    onClose={() => {
      setModalOpen(false);
      setUsuarioDetalle(null);
    }}
  />
)}

    </div>
  );
};

export default MonitoreoPage;
