import React, { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { FaTimes } from 'react-icons/fa';
import {
  GoogleMap,
  Marker,
  Circle,
  useJsApiLoader,
  InfoWindow
} from '@react-google-maps/api';


const containerStyle = {
  width: '100%',
  height: '600px'
};

const coloresPorPuerto = [
  '#FF0000', '#008000', '#0000FF', '#FFA500', '#800080', '#00CED1', '#A52A2A', '#FFC0CB'
];

const MapaCajasNapModal = ({ cajas, onClose }) => {
  const [puertoSeleccionado, setPuertoSeleccionado] = useState('');
  const [cajaActiva, setCajaActiva] = useState(null);
  const [puertos, setPuertos] = useState([]);
  const [tarjetas, setTarjetas] = useState([]);
  const [zoom, setZoom] = useState(16);
  const mapRef = useRef(null);


  useEffect(() => {
    const fetchData = async () => {
      try {
        const resPuertos = await fetch('http://localhost:5004/puertos');
        const dataPuertos = await resPuertos.json();
        setPuertos(dataPuertos);

        const resTarjetas = await fetch('http://localhost:5004/tarjetas-olt');
        const dataTarjetas = await resTarjetas.json();
        setTarjetas(dataTarjetas);
      } catch (err) {
        console.error('Error al cargar puertos o tarjetas:', err);
      }
    };
    fetchData();
  }, []);

  const centro = useMemo(() => {
    const visibles = puertoSeleccionado
      ? cajas.filter(c => c.id_puerto_pon_olt === parseInt(puertoSeleccionado))
      : cajas;
    return visibles.length > 0
      ? { lat: parseFloat(visibles[0].latitud), lng: parseFloat(visibles[0].longitud) }
      : { lat: -1.6743, lng: -78.6486 };
  }, [cajas, puertoSeleccionado]);

  const cajasFiltradas = useMemo(() => {
    const idSeleccionado = parseInt(puertoSeleccionado);
    return puertoSeleccionado
      ? cajas.filter(c => c.id_puerto_pon_olt === idSeleccionado)
      : cajas;
  }, [cajas, puertoSeleccionado]);

  const getColorPorPuerto = (idPuerto) => {
    const index = idPuerto % coloresPorPuerto.length;
    return coloresPorPuerto[index];
  };

  const obtenerPuertoTexto = (idPuerto) => {
    const puerto = puertos.find(p => p.id_puerto_pon_olt === idPuerto);
    const tarjeta = puerto ? tarjetas.find(t => t.id_tarjeta_olt === puerto.id_tarjeta_olt) : null;
    const slot = tarjeta ? tarjeta.slot_numero : 'N/A';
    return puerto ? `Puerto ${puerto.numero_puerto} - Slot ${slot}` : `Puerto PON #${idPuerto}`;
  };

  const handleMarkerClick = (caja) => {
    setCajaActiva(caja);
    if (mapRef.current) {
      mapRef.current.panTo({ lat: parseFloat(caja.latitud), lng: parseFloat(caja.longitud) });
      mapRef.current.setZoom(18);
      setZoom(18);
    }
  };

  const handleCloseInfoWindow = () => {
    setCajaActiva(null);
    if (mapRef.current) {
      mapRef.current.setZoom(16);
      setZoom(16);
    }
  };

  return (
    
    <div className="fixed inset-0 bg-black bg-opacity-60 z-50 flex items-center justify-center p-4">
       <div className="bg-white rounded-lg shadow-xl w-full max-w-6xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center p-4 border-b bg-gray-100">
          <h2 className="text-lg font-bold text-gray-800">Mapa de Cajas NAP</h2>
          <button onClick={onClose} className="text-gray-600 hover:text-gray-800">
            <FaTimes />
          </button>
        </div>

        <div className="px-4 pt-4">
          <select
            value={puertoSeleccionado}
            onChange={(e) => {
              setPuertoSeleccionado(e.target.value);
              setCajaActiva(null);
              setZoom(16);
            }}
            className="mb-4 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none"
          >
            <option value="">Todos los Puertos PON</option>
            {[...new Set(cajas.map(c => c.id_puerto_pon_olt))].map(id => (
              <option key={id} value={id}>{obtenerPuertoTexto(id)}</option>
            ))}
          </select>

          
            <GoogleMap
              key={puertoSeleccionado}
              mapContainerStyle={containerStyle}
              center={centro}
              zoom={zoom}
              onLoad={(map) => { mapRef.current = map; }}
            >
              {cajasFiltradas.map((caja) => {
                const color = getColorPorPuerto(caja.id_puerto_pon_olt);
                const posicion = {
                  lat: parseFloat(caja.latitud),
                  lng: parseFloat(caja.longitud)
                };
                return (
                  <React.Fragment key={caja.id_caja}>
                    <Marker
                      position={posicion}
                      onClick={() => handleMarkerClick(caja)}
                      icon={{
                        path: window.google.maps.SymbolPath.CIRCLE,
                        scale: 8,
                        fillColor: color,
                        fillOpacity: 1,
                        strokeWeight: 1,
                      }}
                    />
                    {caja.id_caja === cajaActiva?.id_caja && caja.radio_cobertura && (
                      <Circle
                        center={posicion}
                        radius={parseFloat(caja.radio_cobertura)}
                        options={{
                          strokeColor: color,
                          fillColor: color,
                          strokeOpacity: 0.7,
                          fillOpacity: 0.1,
                          strokeWeight: 2,
                        }}
                      />
                    )}
                  </React.Fragment>
                );
              })}

              {cajaActiva && (
                <InfoWindow
                  position={{ lat: parseFloat(cajaActiva.latitud), lng: parseFloat(cajaActiva.longitud) }}
                  onCloseClick={handleCloseInfoWindow}
                >
                  <div className="text-sm">
                    <p className="font-bold">{cajaActiva.nombre_caja_nap}</p>
                    <p className="text-gray-600">{cajaActiva.ubicacion}</p>
                    <p>{obtenerPuertoTexto(cajaActiva.id_puerto_pon_olt)}</p>
                    <p>Capacidad: {cajaActiva.capacidad_puertos_cliente}</p>
                    <p>Ocupados: {cajaActiva.puertos_ocupados}</p>
                  </div>
                </InfoWindow>
              )}
            </GoogleMap>
            <div className="text-center py-10 text-gray-500">Cargando mapa...</div>
          
        </div>
      </div>
    </div>
  );
};

export default MapaCajasNapModal;
