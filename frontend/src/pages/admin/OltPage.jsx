import React, { useEffect, useState } from 'react';
import { FaNetworkWired, FaTrash, FaEdit, FaPlus, FaSearch } from 'react-icons/fa';
import Swal from 'sweetalert2';
import OLTImage from '../../assets/OLT_Huawei-MA5600T.jpg'; // Ajusta el path si es diferente
import ModalEditarOLT from '../../components/ModalEditarOLT';
import ModalRegistrarOLT from '../../components/ModalRegistrarOLT';


const OLTPage = () => {
  const [olts, setOlts] = useState([]);
  const [busqueda, setBusqueda] = useState('');
  const [modalAbierto, setModalAbierto] = useState(false);
  const [oltSeleccionada, setOltSeleccionada] = useState(null);
  const [modalCrearAbierto, setModalCrearAbierto] = useState(false);
  const [slotsPorOLT, setSlotsPorOLT] = useState({});

  const fetchOLTs = async () => {
    try {
      const res = await fetch('http://localhost:5004/olts');
      const data = await res.json();
      setOlts(data);
      data.forEach(olt => fetchSlotsTarjetas(olt.id_olt));
    } catch (error) {
      console.error('Error al obtener OLTs:', error);
    }
  };

  const fetchSlotsTarjetas = async (id_olt) => {
    try {
      const res = await fetch(`http://localhost:5004/tarjetas-olt?id_olt=${id_olt}`);
      const data = await res.json();
      const slots = data.map(t => t.slot_numero);
      setSlotsPorOLT(prev => ({ ...prev, [id_olt]: slots }));
    } catch (error) {
      console.error(`Error al obtener tarjetas de OLT ${id_olt}:`, error);
    }
  };

  const handleEliminar = async (id) => {
    const confirmacion = await Swal.fire({
      title: '¿Estás seguro?',
      text: 'Esta acción eliminará la OLT de forma permanente.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    });

    if (confirmacion.isConfirmed) {
      try {
        const res = await fetch(`http://localhost:5004/olts/${id}`, {
          method: 'DELETE'
        });
        if (res.ok) {
          await fetchOLTs();
          Swal.fire('Eliminado', 'La OLT ha sido eliminada.', 'success');
        } else {
          Swal.fire('Error', 'No se pudo eliminar la OLT.', 'error');
        }
      } catch (err) {
        console.error(err);
        Swal.fire('Error', 'Hubo un problema al eliminar.', 'error');
      }
    }
  };

  const oltsFiltradas = olts.filter((olt) =>
    olt.modelo.toLowerCase().includes(busqueda.toLowerCase()) ||
    olt.ip_gestion.toLowerCase().includes(busqueda.toLowerCase()) ||
    olt.marca.toLowerCase().includes(busqueda.toLowerCase())
  );

  useEffect(() => {
    fetchOLTs();
  }, []);

  return (
    <div className="p-4">
      <div className="bg-white shadow-xl rounded-xl p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <FaNetworkWired className="text-green-600" />
            OLTs Registradas
          </h1>
          <button
            onClick={() => setModalCrearAbierto(true)}
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg shadow"
            >
            <FaPlus />
            Crear OLT
            </button>

        </div>

        {/* Filtro */}
        <div className="relative mb-6">
          <input
            type="text"
            placeholder="Buscar por modelo, IP o marca..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            value={busqueda}
            onChange={(e) => setBusqueda(e.target.value)}
          />
          <FaSearch className="absolute left-3 top-3 text-gray-500" />
        </div>

        {/* OLTs */}
        <div className="flex flex-col gap-6">
          {oltsFiltradas.map((olt) => (
  <div
    key={olt.id_olt}
    className="bg-white border border-gray-300 shadow-md rounded-xl p-5 hover:shadow-lg transition w-full"
  >
    <div className="flex flex-col lg:flex-row gap-6 items-start justify-between">
      {/* Imagen */}
      <img
        src={OLTImage}
        alt="OLT"
        className="w-full lg:w-48 h-auto rounded-md border object-contain"
      />

      {/* Contenido principal */}
      <div className="flex-1 flex flex-col justify-between">
        {/* Info y acciones en fila */}
        <div className="flex justify-between items-start gap-4 flex-wrap">
          <div>
            <span className="inline-block bg-green-100 text-green-700 text-xs font-semibold px-3 py-1 rounded-full shadow-sm mb-2">
              FRAME #{olt.id_olt - 1}
            </span>
            <h2 className="text-xl font-bold text-gray-800">
              {olt.modelo}{' '}
              <span className="text-sm font-medium text-gray-500">({olt.marca})</span>
            </h2>
            <p className="text-sm text-gray-600">IP: {olt.ip_gestion}</p>
            <p className="text-xs text-gray-400">
            Creado: {new Date(olt.fecha_creacion).toLocaleDateString()}
            </p>
            <div className="mt-1">
            {olt.estado ? (
                <span className="inline-block bg-green-100 text-green-700 text-xs font-semibold px-3 py-1 rounded-full shadow-sm">
                Activo
                </span>
            ) : (
                <span className="inline-block bg-red-100 text-red-700 text-xs font-semibold px-3 py-1 rounded-full shadow-sm">
                Inactivo
                </span>
            )}
            </div>


          </div>

          {/* Acciones en fila */}
          <div className="flex flex-row gap-3 mt-2">
            <button
                onClick={() => {
                    setOltSeleccionada(olt);
                    setModalAbierto(true);
                }}
                className="text-blue-500 hover:text-blue-700"
                title="Editar"
                >
                <FaEdit size={16} />
            </button>

            {/* Botón de eliminar oculto visualmente */}
            {/* 
            <button
            onClick={() => handleEliminar(olt.id_olt)}
            className="text-red-500 hover:text-red-700"
            title="Eliminar"
            >
            <FaTrash size={16} />
            </button> 
            */}
          </div>
        </div>

        {/* Slots y capacidad a la derecha (más arriba) */}
        <div className="flex justify-end mt-4">
          <div className="flex flex-col items-end">
            <div className="flex flex-wrap gap-1 justify-end">
              {Array.from({ length: olt.capacidad }).map((_, index) => {
                const ocupado = slotsPorOLT[olt.id_olt]?.includes(index);
                return (
                  <div
                    key={index}
                    className={`w-8 h-8 rounded-md text-xs font-bold flex items-center justify-center border ${
                      ocupado
                        ? 'bg-green-500 text-white border-green-600'
                        : 'bg-gray-100 text-gray-700 border-gray-300'
                    }`}
                  >
                    {index}
                  </div>
                );
              })}
            </div>
            <div className="text-sm text-gray-700 mt-2">
              Capacidad: <strong>{olt.capacidad}</strong> · Ocupados: <strong>{olt.slots_ocupados}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
))}


        </div>

        {/* Sin resultados */}
        {oltsFiltradas.length === 0 && (
          <div className="text-center text-gray-500 mt-6">
            No se encontraron OLTs con los criterios de búsqueda.
          </div>
        )}
      </div>

        <ModalRegistrarOLT
        isOpen={modalCrearAbierto}
        onClose={() => setModalCrearAbierto(false)}
        onSave={fetchOLTs}
        />


      <ModalEditarOLT
        isOpen={modalAbierto}
        onClose={() => setModalAbierto(false)}
        olt={oltSeleccionada}
        onSave={fetchOLTs}
        />

    </div>
  );
};

export default OLTPage;
