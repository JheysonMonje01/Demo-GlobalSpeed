import React, { useEffect, useState } from 'react';
import {
  FaMapMarkerAlt, FaPlug, FaNetworkWired
} from 'react-icons/fa';

const CajaNapCardListSoloVer = ({ caja }) => {
  const [puerto, setPuerto] = useState(null);
  const [tarjeta, setTarjeta] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resPuerto = await fetch(`http://localhost:5004/puertos/${caja.id_puerto_pon_olt}`);
        const dataPuerto = await resPuerto.json();
        setPuerto(dataPuerto);

        if (dataPuerto?.id_tarjeta_olt) {
          const resTarjeta = await fetch(`http://localhost:5004/tarjetas-olt/${dataPuerto.id_tarjeta_olt}`);
          const dataTarjeta = await resTarjeta.json();
          setTarjeta(dataTarjeta);
        }
      } catch (error) {
        console.error("Error cargando puerto o tarjeta:", error);
      }
    };
    fetchData();
  }, [caja.id_puerto_pon_olt]);

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-md p-4 transition duration-300 hover:shadow-lg">
      <h2 className="text-lg font-semibold text-gray-800 mb-1 truncate">{caja.nombre_caja_nap}</h2>
      <p className="text-sm text-gray-600 flex items-center">
        <FaMapMarkerAlt className="mr-2 text-green-500" />
        {caja.ubicacion}
      </p>

      <div className="mt-3 text-sm text-gray-700 space-y-1">
        <p className="flex items-center">
          <FaNetworkWired className="mr-2 text-blue-500" />
          <strong>Slot Tarjeta:</strong>&nbsp;{tarjeta?.slot_numero ?? 'N/A'}
        </p>
        <p className="flex items-center">
          <FaNetworkWired className="mr-2 text-blue-500" />
          <strong>Puerto PON OLT:</strong>&nbsp;{puerto?.numero_puerto ?? caja.id_puerto_pon_olt}
        </p>
        <p className="flex items-center">
          <FaPlug className="mr-2 text-indigo-500" />
          <strong>Capacidad:</strong>&nbsp;{caja.capacidad_puertos_cliente}
        </p>
        <p>
          <strong>Ocupados:</strong>&nbsp;{caja.puertos_ocupados}
        </p>
        <p>
          <strong>Estado:</strong>&nbsp;
          <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${caja.estado ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
            {caja.estado ? 'Activo' : 'Inactivo'}
          </span>
        </p>
      </div>
    </div>
  );
};

export default CajaNapCardListSoloVer;
