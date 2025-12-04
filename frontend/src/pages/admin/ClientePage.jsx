import React, { useEffect, useState } from 'react';
import {
  FaPlus, FaEye, FaEdit, FaTrash, FaSearch, FaArrowLeft, FaArrowRight
} from 'react-icons/fa';
import UsuarioDetalleModal from '../../components/UsuarioDetalleModal';
import UsuarioEditarModal from '../../components/ModalEditarUsuario';
//import ModalRegistrarUsuario from '../../components/ModalRegistrarUsuario';
import ModalRegistrarCliente from '../../components/ModalRegistrarCliente';

import Swal from 'sweetalert2';

const ClientesPage = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [filtroRol, setFiltroRol] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('');
  const [busqueda, setBusqueda] = useState('');
  const [pagina, setPagina] = useState(1);
  const [itemsPorPagina, setItemsPorPagina] = useState(10);
  const [usuarioSeleccionado, setUsuarioSeleccionado] = useState(null);
  const [usuarioEditar, setUsuarioEditar] = useState(null);
  const [modalRegistroAbierto, setModalRegistroAbierto] = useState(false);
  


  const idUsuarioLogeado = parseInt(localStorage.getItem('id_usuario'));
  const rolUsuarioLogeado = parseInt(localStorage.getItem('rol'));

  const fetchUsuarios = async () => {
  try {
    const res = await fetch('http://localhost:5001/api/personas-filtros');
    const data = await res.json();

    const usuariosConDatos = await Promise.all(
      data.map(async (usuario) => {
        let rolNombre = 'Sin rol';
        let estadoUsuario = false;
        let idRol = null;

        try {
          const resUser = await fetch(`http://localhost:5000/auth/usuarios/filtrado?id_usuario=${usuario.id_usuario}`);
          const datosUsuario = await resUser.json();

          if (Array.isArray(datosUsuario) && datosUsuario.length > 0 && datosUsuario[0].id_rol) {
            idRol = datosUsuario[0].id_rol;
            const resRol = await fetch(`http://localhost:5000/api/roles/filtrado?id_rol=${idRol}`);
            const datosRol = await resRol.json();
            rolNombre = Array.isArray(datosRol) && datosRol.length > 0 && datosRol[0].nombre_rol ? datosRol[0].nombre_rol : 'Rol no encontrado';
            estadoUsuario = datosUsuario[0].estado;
          }
        } catch (error) {
          console.error(`❌ Error consultando rol de ${usuario.nombre}:`, error);
        }

        return { ...usuario, rol: rolNombre, estado: estadoUsuario, id_rol: idRol };
      })
    );

    // ✅ Filtrar solo clientes (id_rol === 3)
    const clientes = usuariosConDatos.filter(u => u.id_rol === 3);
    setUsuarios(clientes);
  } catch (error) {
    console.error('❌ Error al cargar usuarios:', error);
  }
};


  useEffect(() => {
    fetchUsuarios();
  }, []);

  const handleEliminarUsuario = async (usuario) => {
    const { id_usuario, estado } = usuario;
    const resultado = await Swal.fire({
      title: estado ? '¿Desactivar usuario?' : '¿Eliminar permanentemente?',
      text: estado
        ? 'El usuario será desactivado, pero no eliminado de forma permanente.'
        : 'Esta acción eliminará el usuario de forma permanente. ¿Estás seguro?',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: estado ? 'Desactivar' : 'Eliminar',
      cancelButtonText: 'Cancelar',
    });

    if (resultado.isConfirmed) {
      const endpoint = estado
        ? `http://localhost:5000/auth/usuarios-persona-eliminar/${id_usuario}`
        : `http://localhost:5000/auth/usuarios-persona-eliminar/${id_usuario}/permanente`;

      try {
        const res = await fetch(endpoint, { method: 'DELETE' });
        if (!res.ok) throw new Error('Error en la solicitud');

        Swal.fire({
          title: '¡Listo!',
          text: estado ? 'Usuario desactivado' : 'Usuario eliminado permanentemente',
          icon: 'success',
          timer: 2000,
          showConfirmButton: false,
        });
        fetchUsuarios();
      } catch (error) {
        Swal.fire({
          title: 'Error',
          text: 'No se pudo completar la operación.',
          icon: 'error',
        });
      }
    }
  };

  // Permisos de edición y eliminación
  const puedeEditar = (u) => {
    if (idUsuarioLogeado === 1 && u.id_usuario !== 1) return true;
    if (idUsuarioLogeado === u.id_usuario) return true;
    if (rolUsuarioLogeado === 1 && u.id_rol !== 1) return true;
    return false;
  };

  const puedeEliminar = (u) => {
    if (idUsuarioLogeado === 1 && u.id_usuario !== 1) return true;
    if (rolUsuarioLogeado === 1 && u.id_rol !== 1 && u.id_usuario !== idUsuarioLogeado) return true;
    return false;
  };

  const usuariosFiltrados = usuarios
    .filter(u => u.nombre.toLowerCase().includes(busqueda.toLowerCase()) || u.correo.toLowerCase().includes(busqueda.toLowerCase()))
    .filter(u => !filtroRol || u.rol === filtroRol)
    .filter(u => !filtroEstado || (filtroEstado === 'Activo' ? u.estado : !u.estado));

  const paginados = usuariosFiltrados.slice((pagina - 1) * itemsPorPagina, pagina * itemsPorPagina);

  return (
    <div className="p-4 sm:p-6 bg-white shadow-lg rounded-xl text-sm border border-gray-100">
      {/* Encabezado */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-3 mb-6">
        <h2 className="text-2xl sm:text-3xl font-bold text-green-700 tracking-wide">Clientes</h2>
        {/*<button 
        onClick={() => setModalRegistroAbierto(true)}
        className="flex items-center justify-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg shadow hover:bg-green-700 transition"
        >
        <FaPlus /> <span className="hidden sm:inline">Agregar Cliente</span>
        </button>*/}
        {rolUsuarioLogeado !== 2 && (
          <button 
            onClick={() => setModalRegistroAbierto(true)}
            className="flex items-center justify-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg shadow hover:bg-green-700 transition"
          >
            <FaPlus /> <span className="hidden sm:inline">Agregar Cliente</span>
          </button>
        )}

      </div>

      {/* Filtros */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4 mb-5">
        <div className="relative">
          <FaSearch className="absolute top-3 left-3 text-gray-400" />
          <input
            type="text"
            placeholder="Buscar por nombre o correo"
            className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg w-full focus:ring-2 focus:ring-green-400 shadow-sm"
            value={busqueda}
            onChange={e => setBusqueda(e.target.value)}
          />
        </div>

        <select
          className="border border-gray-300 px-3 py-2 rounded-lg text-sm shadow-sm focus:outline-none focus:ring-green-400 w-full"
          value={filtroEstado}
          onChange={e => setFiltroEstado(e.target.value)}
        >
          <option value="">Todos los estados</option>
          <option value="Activo">Activo</option>
          <option value="Inactivo">Inactivo</option>
        </select>

      </div>

      {/* Tabla de usuarios */}
      <div className="w-full overflow-x-auto rounded-lg border border-gray-200">
        <table className="min-w-[700px] w-full text-xs sm:text-sm text-left">
          <thead className="bg-green-100 text-green-900">
            <tr>
                <th className="px-3 py-2 font-semibold">Nombre y Apellido</th>
                <th className="px-3 py-2 font-semibold">Cédula/RUC</th> {/* antes: Rol */}
                <th className="px-3 py-2 font-semibold">Dirección</th> {/* nuevo */}
                <th className="px-3 py-2 font-semibold">Correo</th>
                <th className="px-3 py-2 font-semibold">Teléfono</th>
                <th className="px-3 py-2 font-semibold">Estado</th>
                <th className="px-3 py-2 text-center font-semibold">Acciones</th>
            </tr>
            </thead>
          <tbody>
            {paginados.map((u, i) => (
              <tr key={i} className="border-t hover:bg-green-50">
                <td className="px-3 py-2 flex items-center gap-2">
                  <img
                    src={u.foto ? `data:image/jpeg;base64,${u.foto}` : "/imagenes/perfil-none.avif"}
                    alt="perfil"
                    className="w-8 h-8 rounded-full object-cover border shadow-sm"
                  />
                  <span className="font-medium">{u.nombre} {u.apellido}</span>
                </td>
                <td className="px-3 py-2 text-gray-800">{u.cedula_ruc}</td>
                <td className="px-3 py-2 text-gray-700">{u.direccion_domiciliaria}</td>
                <td className="px-3 py-2 text-gray-700">{u.correo}</td>
                <td className="px-3 py-2 text-gray-700">{u.telefono}</td>
                <td className="px-3 py-2">
                  <span className={`px-2 py-1 text-xs rounded-full font-semibold ${u.estado ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`}>
                    {u.estado ? 'Activo' : 'Inactivo'}
                  </span>
                </td>
                <td className="px-3 py-2 text-center space-x-2">
                  <button className="text-yellow-500 hover:text-yellow-600" onClick={() => setUsuarioSeleccionado(u)}><FaEye /></button>
                  {puedeEditar(u) && (
                    <button className="text-blue-500 hover:text-blue-600" onClick={() => setUsuarioEditar(u)}><FaEdit /></button>
                  )}
                  {puedeEliminar(u) && (
                    <button className="text-red-500 hover:text-red-600" onClick={() => handleEliminarUsuario(u)}><FaTrash /></button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Paginación */}
      <div className="mt-6 flex flex-col sm:flex-row gap-2 justify-between items-center text-xs sm:text-sm">
        <div>
          Items por página:
          <select
            className="ml-2 border border-gray-300 px-2 py-1 rounded-lg shadow-sm"
            value={itemsPorPagina}
            onChange={e => setItemsPorPagina(Number(e.target.value))}
          >
            {[5, 10, 20].map(n => (
              <option key={n} value={n}>{n}</option>
            ))}
          </select>
        </div>
        <div className="flex items-center gap-2">
          {(pagina - 1) * itemsPorPagina + 1} - {Math.min(pagina * itemsPorPagina, usuariosFiltrados.length)} de {usuariosFiltrados.length}
          <button
            disabled={pagina === 1}
            onClick={() => setPagina(p => p - 1)}
            className="px-2 py-1 border rounded disabled:opacity-50 hover:bg-gray-100"
          >
            <FaArrowLeft />
          </button>
          <button
            disabled={pagina * itemsPorPagina >= usuariosFiltrados.length}
            onClick={() => setPagina(p => p + 1)}
            className="px-2 py-1 border rounded disabled:opacity-50 hover:bg-gray-100"
          >
            <FaArrowRight />
          </button>
        </div>
      </div>

      {/* Modales */}
      {usuarioSeleccionado && (
        <UsuarioDetalleModal
          usuario={usuarioSeleccionado}
          onClose={() => setUsuarioSeleccionado(null)}
        />
      )}

      {usuarioEditar && (
        <UsuarioEditarModal
          usuario={usuarioEditar}
          onClose={() => setUsuarioEditar(null)}
          onSave={() => {
            setUsuarioEditar(null);
            fetchUsuarios();
          }}
        />
      )}

        {modalRegistroAbierto && (
        <ModalRegistrarCliente
            onClose={() => setModalRegistroAbierto(false)}
            onSuccess={() => {
            setModalRegistroAbierto(false);
            fetchUsuarios();
            }}
        />
        )}



    </div>
  );
};

export default ClientesPage;
