import React, { useEffect, useState } from 'react';
import { FaPlus, FaCreditCard, FaTrashAlt, FaEdit, FaEye  } from 'react-icons/fa';
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';
import ModalVerMetodoPago from '../../components/ModalVerMetodoPago'; // ajusta ruta si necesario
import ModalEditarMetodoPago from '../../components/ModalEditarMetodoPago'; // ajusta ruta
import ModalNuevoMetodoPago from '../../components/ModalNuevoMetodoPago';




const MetodoPagoPage = () => {
  const [metodos, setMetodos] = useState([]);
  const [busqueda, setBusqueda] = useState('');
  const [estadoFiltro, setEstadoFiltro] = useState('');
  const [verificacionFiltro, setVerificacionFiltro] = useState('');
  const [pagina, setPagina] = useState(1);
  const [porPagina] = useState(6);
  const MySwal = withReactContent(Swal);
  const [modalMetodo, setModalMetodo] = useState(null);
  const [modalEditar, setModalEditar] = useState(null);
  const [modalNuevo, setModalNuevo] = useState(false);


  useEffect(() => {
    obtenerMetodos();
  }, [busqueda]);

  const obtenerMetodos = async () => {
    try {
      const res = await fetch(`http://localhost:5008/metodos_pago/buscar?nombre=${busqueda}`);
      const data = await res.json();
      setMetodos(data);
    } catch (error) {
      console.error('Error al obtener métodos de pago:', error);
    }
  };

  const filtrar = (lista) => {
    return lista.filter((m) => {
      const estadoMatch = estadoFiltro === '' || String(m.estado) === estadoFiltro;
      const verificacionMatch = verificacionFiltro === '' || String(m.requiere_verificacion) === verificacionFiltro;
      return estadoMatch && verificacionMatch;
    });
  };

  const metodosFiltrados = filtrar(metodos);
  const metodosPaginados = metodosFiltrados.slice((pagina - 1) * porPagina, pagina * porPagina);
  const totalPaginas = Math.ceil(metodosFiltrados.length / porPagina);

  const formatearFecha = (fechaISO) => {
    const fecha = new Date(fechaISO);
    return fecha.toLocaleDateString('es-EC', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const handleNuevoMetodo = () => {
    MySwal.fire({
      title: 'Añadir Método de Pago',
      text: 'Aquí podrías abrir un modal para registrar un nuevo método.',
      icon: 'info',
    });
  };

  const eliminarMetodo = async (id) => {
    const confirmacion = await MySwal.fire({
      title: '¿Estás seguro?',
      text: 'Esta acción eliminará el método de pago.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar',
    });

    if (confirmacion.isConfirmed) {
      try {
        const res = await fetch(`http://localhost:5008/metodos_pago/borrar/${id}`, {
          method: 'DELETE',
        });
        const data = await res.json();
        if (res.ok) {
          MySwal.fire('¡Eliminado!', data.message || 'Método eliminado.', 'success');
          obtenerMetodos();
        } else {
          MySwal.fire('Error', data.error || 'No se pudo eliminar.', 'error');
        }
      } catch (err) {
        console.error(err);
        MySwal.fire('Error', 'Ocurrió un error inesperado.', 'error');
      }
    }
  };

  const editarMetodo = (metodo) => {
    MySwal.fire({
      title: 'Editar Método',
      text: `Aquí abrirías el modal para editar el método: ${metodo.nombre}`,
      icon: 'info',
    });
  };

  return (
    <div className="p-6 flex justify-center">
      <div className="w-full max-w-screen-2xl bg-white shadow-2xl border-b-4 border-green-600 rounded-xl p-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-green-700 flex items-center gap-3">
            <FaCreditCard className="text-green-700" />
            Métodos de Pago Disponibles
          </h1>
          <button
            onClick={() => setModalNuevo(true)}
            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg shadow flex items-center gap-2"
            >
            <FaPlus /> Añadir Método de Pago
        </button>

        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <input
            type="text"
            placeholder="🔍 Buscar por nombre..."
            value={busqueda}
            onChange={(e) => {
              setBusqueda(e.target.value);
              setPagina(1);
            }}
            className="border border-green-500 rounded-lg px-4 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500 w-full"
          />
          <select
            value={estadoFiltro}
            onChange={(e) => {
              setEstadoFiltro(e.target.value);
              setPagina(1);
            }}
            className="border border-gray-300 rounded-lg px-4 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">🎯 Filtrar por estado</option>
            <option value="true">Activo</option>
            <option value="false">Inactivo</option>
          </select>
          <select
            value={verificacionFiltro}
            onChange={(e) => {
              setVerificacionFiltro(e.target.value);
              setPagina(1);
            }}
            className="border border-gray-300 rounded-lg px-4 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">✅ Verificación requerida</option>
            <option value="true">Sí</option>
            <option value="false">No</option>
          </select>
        </div>

        {metodosFiltrados.length === 0 ? (
          <div className="text-center text-gray-500 mt-10 text-lg font-medium">
            Aún no hay métodos de pago registrados.
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {metodosPaginados.map((metodo) => (
              <div
                key={metodo.id_metodo_pago}
                className="bg-white border border-gray-100 rounded-xl shadow-md p-6 hover:shadow-lg transition relative"
              >
                {/* Título + acciones */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2 text-green-700 text-xl font-semibold">
                    <FaCreditCard />
                    <span className="capitalize">{metodo.nombre}</span>
                  </div>
                  <div className="flex gap-2">
                    <button
                        onClick={() => setModalMetodo(metodo)}
                        title="Ver detalles"
                        className="p-2 text-gray-600 hover:text-black transition"
                        >
                        <FaEye />
                    </button>

                    <button
                        onClick={() => setModalEditar(metodo)}
                        title="Editar"
                        className="p-2 text-blue-600 hover:text-blue-800 transition"
                        >
                        <FaEdit />
                    </button>

                    <button
                      onClick={() => eliminarMetodo(metodo.id_metodo_pago)}
                      title="Eliminar"
                      className="p-2 text-red-600 hover:text-red-800 transition"
                    >
                      <FaTrashAlt />
                    </button>
                  </div>
                </div>

                <p className="text-gray-600 text-sm mb-4">
                  {metodo.descripcion || 'Sin descripción'}
                </p>

                <div className="flex flex-col gap-2 text-sm">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold">Estado:</span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-sm font-semibold ${
                        metodo.estado ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                      }`}
                    >
                      {metodo.estado ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    <span className="font-semibold">¿Requiere verificación?:</span>
                    <span
                      className={`px-2 py-0.5 rounded-full text-sm font-semibold ${
                        metodo.requiere_verificacion
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-yellow-100 text-yellow-700'
                      }`}
                    >
                      {metodo.requiere_verificacion ? 'Sí' : 'No'}
                    </span>
                  </div>

                  <div>
                    <span className="font-semibold">Fecha de creación:</span>{' '}
                    <span className="text-gray-700">
                      {formatearFecha(metodo.fecha_creacion)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {totalPaginas > 1 && (
          <div className="flex justify-center mt-10 gap-2">
            {Array.from({ length: totalPaginas }, (_, i) => (
              <button
                key={i + 1}
                onClick={() => setPagina(i + 1)}
                className={`px-3 py-1 rounded-full border ${
                  pagina === i + 1
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-green-700 border-green-300 hover:bg-green-100'
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        )}
      </div>
      {modalMetodo && (
  <ModalVerMetodoPago metodo={modalMetodo} onClose={() => setModalMetodo(null)} />
)}

{modalEditar && (
  <ModalEditarMetodoPago
    metodo={modalEditar}
    metodosExistentes={metodos} // se usa para validar nombre único
    onClose={() => setModalEditar(null)}
    onSuccess={obtenerMetodos}
  />
)}
{modalNuevo && (
  <ModalNuevoMetodoPago
    metodosExistentes={metodos}
    onClose={() => setModalNuevo(false)}
    onSuccess={obtenerMetodos}
  />
)}




    </div>
  );
};

export default MetodoPagoPage;
