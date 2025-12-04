// ListadoUsuarios.jsx
import { FaEdit, FaTrash, FaUserPlus, FaUserShield, FaSortAlphaDown, FaSortAlphaUp } from 'react-icons/fa';
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ModalEditarUsuario from '../../components/ModalEditarUsuario'
import Swal from 'sweetalert2';

const ListadoUsuarios = () => {
  const [usuarios, setUsuarios] = useState([]);
  const [filtroNombre, setFiltroNombre] = useState('');
  const [filtroRol, setFiltroRol] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('');
  const [pagina, setPagina] = useState(1);
  const [ordenCampo, setOrdenCampo] = useState(null);
  const [ordenAsc, setOrdenAsc] = useState(true);
  const [modalUsuario, setModalUsuario] = useState(null);
  const usuariosPorPagina = 5;
  const navigate = useNavigate();
  const idUsuarioActual = parseInt(localStorage.getItem('id_usuario'), 10);

  useEffect(() => {
    setUsuarios([
      { id: 1, nombre: 'Jonathan', apellido: 'Chamorro', rol: 'Administrador', correo: 'admin@example.com', estado: true, creado: '2024-12-20T10:15:00Z' },
      { id: 2, nombre: 'Lucía', apellido: 'Gómez', rol: 'Técnico', correo: 'tecnico@example.com', estado: false, creado: '2025-01-15T08:40:00Z' },
      { id: 3, nombre: 'Pedro', apellido: 'López', rol: 'Cliente', correo: 'cliente1@example.com', estado: true, creado: '2025-02-01T12:00:00Z' },
      { id: 4, nombre: 'Sofía', apellido: 'Mora', rol: 'Cliente', correo: 'cliente2@example.com', estado: false, creado: '2025-03-10T09:30:00Z' },
      { id: 5, nombre: 'Carlos', apellido: 'Vera', rol: 'Administrador', correo: 'carlos@example.com', estado: true, creado: '2025-04-05T11:45:00Z' },
      { id: 6, nombre: 'Ana', apellido: 'Martínez', rol: 'Técnico', correo: 'ana@example.com', estado: true, creado: '2025-05-01T08:20:00Z' },
    ]);
  }, []);

  const handleEliminar = (id, nombre) => {
  Swal.fire({
    title: '¿Estás seguro?',
    text: `¿Deseas eliminar al usuario "${nombre}"? Esta acción no se puede deshacer.`,
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
  }).then((result) => {
    if (result.isConfirmed) {
      eliminarUsuario(id); // Tu función para eliminar desde el backend
      Swal.fire('Eliminado', 'El usuario ha sido eliminado.', 'success');
    }
  });
};

  const formatearFecha = (fechaIso) => new Date(fechaIso).toLocaleDateString();

  const ordenarPor = (campo) => {
    if (ordenCampo === campo) setOrdenAsc(!ordenAsc);
    else {
      setOrdenCampo(campo);
      setOrdenAsc(true);
    }
  };

  const usuariosFiltrados = usuarios
    .filter((u) => u.nombre.toLowerCase().includes(filtroNombre.toLowerCase()) &&
      (filtroRol ? u.rol === filtroRol : true) &&
      (filtroEstado ? u.estado === (filtroEstado === 'Activo') : true))
    .sort((a, b) => {
      if (!ordenCampo) return 0;
      const aValue = a[ordenCampo];
      const bValue = b[ordenCampo];
      return ordenAsc ? (aValue > bValue ? 1 : -1) : (aValue < bValue ? 1 : -1);
    });

  const totalPaginas = Math.ceil(usuariosFiltrados.length / usuariosPorPagina);
  const usuariosPaginados = usuariosFiltrados.slice((pagina - 1) * usuariosPorPagina, pagina * usuariosPorPagina);

  return (
   
      <div className="min-h-[calc(92vh-4rem)] p-4 sm:p-6 bg-gradient-to-br from-green-50 to-white">
        <div className="flex flex-col sm:flex-row justify-between items-center mb-6 gap-4">
          <h2 className="text-2xl sm:text-3xl font-bold text-green-800 flex items-center gap-2">
            <FaUserShield className="text-green-600" /> Lista de Usuarios
          </h2>
          <button onClick={() => navigate('/admin/usuarios/register')} className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm shadow-md">
            <FaUserPlus /> Registrar Usuario
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
          <input type="text" placeholder="Buscar por nombre..." className="py-1.5 px-3 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white text-sm" value={filtroNombre} onChange={(e) => setFiltroNombre(e.target.value)} />
          <select className="py-1.5 px-3 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white text-sm" value={filtroRol} onChange={(e) => setFiltroRol(e.target.value)}>
            <option value="">Todos los roles</option>
            <option value="Administrador">Administrador</option>
            <option value="Técnico">Técnico</option>
            <option value="Cliente">Cliente</option>
          </select>
          <select className="py-1.5 px-3 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white text-sm" value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)}>
            <option value="">Todos los estados</option>
            <option value="Activo">Activo</option>
            <option value="Inactivo">Inactivo</option>
          </select>
        </div>

        <div className="overflow-x-auto shadow-lg rounded-xl bg-white">
          <table className="min-w-full text-sm border border-gray-200">
            <thead>
              <tr className="bg-green-700 text-white">
                {['nombre', 'apellido', 'rol', 'estado', 'creado'].map((campo) => (
                  <th key={campo} className="py-3 px-4 text-left cursor-pointer select-none hover:underline" onClick={() => ordenarPor(campo)}>
                    <div className="flex items-center gap-1 capitalize">
                      {campo === 'creado' ? 'Fecha' : campo}
                      {ordenCampo === campo && (ordenAsc ? <FaSortAlphaDown className="text-xs" /> : <FaSortAlphaUp className="text-xs" />)}
                    </div>
                  </th>
                ))}
                <th className="py-3 px-4 text-left">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {usuariosPaginados.map((usuario, index) => {
                const esAdmin = usuario.rol === 'Administrador';
                const puedeEditar = idUsuarioActual === usuario.id || (!esAdmin || idUsuarioActual === 1);
                const puedeEliminar = usuario.id !== idUsuarioActual && (!esAdmin || idUsuarioActual === 1);
                return (
                  <tr key={usuario.id} className={`border-b ${index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}>
                    <td className="py-3 px-4 font-medium text-gray-700">{usuario.nombre}</td>
                    <td className="py-3 px-4">{usuario.apellido}</td>
                    <td className="py-3 px-4">{usuario.rol}</td>
                    <td className="py-3 px-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${usuario.estado ? 'bg-green-200 text-green-800' : 'bg-red-200 text-red-800'}`}>{usuario.estado ? 'Activo' : 'Inactivo'}</span>
                    </td>
                    <td className="py-3 px-4">{formatearFecha(usuario.creado)}</td>
                    <td className="py-3 px-4 flex gap-3">
                      {puedeEditar && (
                        <button onClick={() => setModalUsuario(usuario)} title="Editar" className="text-blue-600 hover:text-blue-800 transition">
                          <FaEdit />
                        </button>
                      )}
                      {puedeEliminar && (
                        <button title="Eliminar" className="text-red-600 hover:text-red-800 transition"
                        onClick={() => handleEliminar(usuario.id_usuario, `${usuario.nombre} ${usuario.apellido}`)}
                        >
                          <FaTrash />
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
              {usuariosPaginados.length === 0 && (
                <tr>
                  <td colSpan="6" className="py-6 text-center text-gray-500 italic">No se encontraron usuarios.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="flex justify-center flex-wrap items-center gap-2 mt-6">
          {Array.from({ length: totalPaginas }, (_, i) => i + 1).map((num) => (
            <button key={num} onClick={() => setPagina(num)} className={`px-3 py-1.5 rounded-full text-sm font-medium transition shadow ${pagina === num ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-800 hover:bg-green-200'}`}>{num}</button>
          ))}
        </div>

        <ModalEditarUsuario usuario={modalUsuario} onClose={() => setModalUsuario(null)} />
      </div>
    
  );
};

export default ListadoUsuarios;
