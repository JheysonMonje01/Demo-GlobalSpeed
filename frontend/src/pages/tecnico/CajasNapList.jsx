import React, { useEffect, useState, useCallback } from 'react';
import { FaMapMarkedAlt } from 'react-icons/fa';
import { toast } from 'react-toastify';
import MapaCajasNapModal from '../../components/MapaCajasNapModal';
import GoogleMapLoader from '../../components/GoogleMapLoader';
import CajaNapCardListSoloVer from '../../components/CajaNapCardList';

const CajasNapListPage = () => {
  const [cajas, setCajas] = useState([]);
  const [modalMapa, setModalMapa] = useState(false);

  const fetchCajas = useCallback(async () => {
    try {
      const res = await fetch('http://localhost:5004/cajas-nap');
      const data = await res.json();
      setCajas(data);
    } catch (error) {
      toast.error('Error al cargar las cajas NAP');
    }
  }, []);

  useEffect(() => {
    fetchCajas();
  }, [fetchCajas]);

  return (
    <div className="p-6">
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">🧰 Cajas NAP</h1>
          <button
            onClick={() => setModalMapa(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg shadow hover:bg-blue-700 flex items-center gap-2"
          >
            <FaMapMarkedAlt />
            Ver Mapa
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cajas.map((caja) => (
            <CajaNapCardListSoloVer key={caja.id_caja} caja={caja} />
          ))}
        </div>
      </div>

      {modalMapa && (
        <GoogleMapLoader>
          <MapaCajasNapModal cajas={cajas} onClose={() => setModalMapa(false)} />
        </GoogleMapLoader>
      )}
    </div>
  );
};

export default CajasNapListPage;
