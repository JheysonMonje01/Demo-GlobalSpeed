import React, { useEffect, useState, useCallback } from 'react';
import { FaSearch, FaPlus, FaMapMarkedAlt } from 'react-icons/fa';
import ModalAgregarCajaNap from '../../components/ModalAgregarCajaNap';
import ModalEditarCajaNap from '../../components/ModalEditarCajaNap';
import CajaNapCard from '../../components/CajaNapCard';
import MapaCajasNapModal from '../../components/MapaCajasNapModal';
import { toast } from 'react-toastify';
import GoogleMapLoader from '../../components/GoogleMapLoader'; // agrégalo arriba

const CajasNapPage = () => {
  const [cajas, setCajas] = useState([]);
  const [filtroTexto, setFiltroTexto] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('todos');
  const [filtroPuerto, setFiltroPuerto] = useState('');
  const [modalAgregar, setModalAgregar] = useState(false);
  const [modalEditar, setModalEditar] = useState(null);
  const [modalMapa, setModalMapa] = useState(false);
  const [paginaActual, setPaginaActual] = useState(1);
  const [puertos, setPuertos] = useState([]);
  const [tarjetas, setTarjetas] = useState([]);
  const itemsPorPagina = 6;

  const fetchCajas = useCallback(async () => {
    try {
      const resCajas = await fetch('http://localhost:5004/cajas-nap');
      const dataCajas = await resCajas.json();
      setCajas(dataCajas);

      const resPuertos = await fetch('http://localhost:5004/puertos');
      const dataPuertos = await resPuertos.json();
      setPuertos(dataPuertos);

      const resTarjetas = await fetch('http://localhost:5004/tarjetas-olt');
      const dataTarjetas = await resTarjetas.json();
      setTarjetas(dataTarjetas);
    } catch (error) {
      toast.error('Error al cargar datos');
    }
  }, []);

  useEffect(() => {
    fetchCajas();
  }, [fetchCajas]);

  const handleEliminar = async (id, fisico = false) => {
    if (!window.confirm("¿Eliminar esta caja NAP?")) return;
    const res = await fetch(`http://localhost:5004/cajas-nap/${id}?fisico=${fisico}`, {
      method: 'DELETE',
    });
    if (res.ok) fetchCajas();
  };

  const cajasFiltradas = cajas.filter(caja => {
    const coincideTexto =
      caja.nombre_caja_nap?.toLowerCase().includes(filtroTexto.toLowerCase()) ||
      caja.ubicacion?.toLowerCase().includes(filtroTexto.toLowerCase());

    const coincideEstado =
      filtroEstado === 'todos' || (filtroEstado === 'activo' && caja.estado) || (filtroEstado === 'inactivo' && !caja.estado);

    const coincidePuerto = filtroPuerto === '' || parseInt(filtroPuerto) === caja.id_puerto_pon_olt;

    return coincideTexto && coincideEstado && coincidePuerto;
  });

  const totalPaginas = Math.ceil(cajasFiltradas.length / itemsPorPagina);
  const cajasPagina = cajasFiltradas.slice(
    (paginaActual - 1) * itemsPorPagina,
    paginaActual * itemsPorPagina
  );

  return (
    <div className="p-6">
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-6">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            🧰 Cajas NAP Registradas
          </h1>
          <div className="flex gap-2">
            <button
              onClick={() => setModalMapa(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-700"
            >
              <FaMapMarkedAlt className="inline mr-2" /> Ver Mapa
            </button>
            <button
              onClick={() => setModalAgregar(true)}
              className="bg-green-600 text-white px-4 py-2 rounded-lg shadow hover:bg-green-700"
            >
              <FaPlus className="inline mr-2" /> Nueva Caja
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="relative">
            <FaSearch className="absolute left-3 top-3 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre o ubicación..."
              value={filtroTexto}
              onChange={(e) => setFiltroTexto(e.target.value)}
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-md w-full"
            />
          </div>

          <select
            value={filtroEstado}
            onChange={(e) => setFiltroEstado(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md w-full"
          >
            <option value="todos">Todos los estados</option>
            <option value="activo">Solo Activos</option>
            <option value="inactivo">Solo Inactivos</option>
          </select>

          <select
            value={filtroPuerto}
            onChange={(e) => setFiltroPuerto(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md w-full"
          >
            <option value="">Todos los puertos PON</option>
            {puertos.map(p => {
              const tarjeta = tarjetas.find(t => t.id_tarjeta_olt === p.id_tarjeta_olt);
              return (
                <option key={p.id_puerto_pon_olt} value={p.id_puerto_pon_olt}>
                  Puerto {p.numero_puerto} - Slot {tarjeta?.slot_numero ?? 'N/A'}
                </option>
              );
            })}
          </select>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {cajasPagina.map((caja) => (
            <CajaNapCard
              key={caja.id_caja}
              caja={caja}
              onEditar={() => setModalEditar(caja)}
              onEliminar={handleEliminar}
            />
          ))}
        </div>

        {totalPaginas > 1 && (
          <div className="flex justify-center mt-6 gap-2">
            {Array.from({ length: totalPaginas }, (_, i) => (
              <button
                key={i}
                onClick={() => setPaginaActual(i + 1)}
                className={`w-8 h-8 rounded-full border text-sm ${
                  paginaActual === i + 1
                    ? 'bg-green-600 text-white'
                    : 'hover:bg-gray-100 text-gray-700'
                }`}
              >
                {i + 1}
              </button>
            ))}
          </div>
        )}
      </div>

      {modalAgregar && (
  <GoogleMapLoader>
    {({ isLoaded }) => (
      <ModalAgregarCajaNap
        isLoaded={isLoaded}
        onClose={() => setModalAgregar(false)}
        onSuccess={fetchCajas}
      />
    )}
  </GoogleMapLoader>
)}





      {modalEditar && (
       
        <ModalEditarCajaNap caja={modalEditar} onClose={() => { setModalEditar(null); fetchCajas(); }} />
        
      )}
      {modalMapa && (
        <GoogleMapLoader>
          <MapaCajasNapModal cajas={cajasFiltradas} onClose={() => setModalMapa(false)} />
        </GoogleMapLoader>
      )}
    </div>
  );
};

export default CajasNapPage;
