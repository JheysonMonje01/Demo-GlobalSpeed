import React, { useState, useEffect } from 'react';
import { FaSearchLocation } from 'react-icons/fa';
import {
  GoogleMap,
  Marker,
  Circle,
  useJsApiLoader
} from '@react-google-maps/api';
import Swal from 'sweetalert2';
import { googleMapsOptions } from '../utils/googleMapsOptions';

const containerStyle = {
  width: '100%',
  height: '500px',
};

const VerificacionCoberturaPublica = () => {
  const { isLoaded } = useJsApiLoader(googleMapsOptions);

  const [direccion, setDireccion] = useState('');
  const [coordenadasCliente, setCoordenadasCliente] = useState(null);
  const [cajasNap, setCajasNap] = useState([]);
  const [mostrarCoberturas, setMostrarCoberturas] = useState(false);

  useEffect(() => {
    fetch('http://localhost:5004/cajas-nap')
      .then(res => res.json())
      .then(setCajasNap)
      .catch(() =>
        Swal.fire('Error', 'No se pudieron cargar las cajas NAP', 'error')
      );
  }, []);

  const geocodeDireccion = async () => {
    if (!direccion) return;
    const res = await fetch(
      `https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(
        direccion + ', Riobamba, Ecuador'
      )}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`
    );
    const data = await res.json();
    if (data.results.length > 0) {
      const location = data.results[0].geometry.location;
      setDireccion('');
      setCoordenadasCliente(location);
      verificarCobertura(location);
    } else {
      Swal.fire('Dirección no encontrada', 'Verifica tu dirección ingresada', 'warning');
    }
  };

  const verificarCobertura = (cliente) => {
    let hayCobertura = false;

    for (const caja of cajasNap) {
      const disponibles = caja.capacidad_puertos_cliente - caja.puertos_ocupados;
      if (disponibles <= 0) continue;

      const distancia = google.maps.geometry.spherical.computeDistanceBetween(
        new google.maps.LatLng(cliente.lat, cliente.lng),
        new google.maps.LatLng(parseFloat(caja.latitud), parseFloat(caja.longitud))
      );

      if (distancia <= parseFloat(caja.radio_cobertura)) {
        hayCobertura = true;
        break;
      }
    }

    setMostrarCoberturas(true);

    if (hayCobertura) {
      Swal.fire({
        icon: 'success',
        title: 'Cobertura disponible',
        text: 'Hay cobertura en tu ubicación.',
        confirmButtonColor: '#10b981'
      });
    } else {
      Swal.fire({
        icon: 'info',
        title: 'Sin cobertura',
        text: 'No hay cajas cercanas con puertos disponibles.',
        confirmButtonColor: '#facc15'
      });
    }
  };

  const usarUbicacionActual = () => {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const location = {
          lat: position.coords.latitude,
          lng: position.coords.longitude
        };
        setCoordenadasCliente(location);
        verificarCobertura(location);
      },
      () => {
        Swal.fire('Error', 'No se pudo obtener tu ubicación', 'error');
      }
    );
  };

  const handleMapClick = (e) => {
    const lat = e.latLng.lat();
    const lng = e.latLng.lng();
    const ubicacion = { lat, lng };
    setDireccion('');
    setCoordenadasCliente(ubicacion);
    verificarCobertura(ubicacion);
  };

  return (
    <div className="py-16 bg-gradient-to-br from-green-50 to-white">
      <div className="max-w-7xl mx-auto px-4">
        <h2 className="text-3xl md:text-4xl font-bold text-center text-green-700 mb-8">
          Verifica si tenemos cobertura en tu zona
        </h2>

        <div className="flex flex-col md:flex-row gap-4 mb-6 items-center justify-center">
          <input
            type="text"
            value={direccion}
            onChange={(e) => setDireccion(e.target.value)}
            placeholder="Ej: Av. Quito y 10 de Agosto"
            className="w-full md:w-[600px] border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-400"
          />
          <button
            onClick={geocodeDireccion}
            className="bg-green-600 hover:bg-green-700 text-white font-bold px-6 py-2 rounded-lg shadow flex items-center gap-2"
          >
            <FaSearchLocation /> Verificar
          </button>
          <button
            onClick={usarUbicacionActual}
            className="bg-blue-600 hover:bg-blue-700 text-white font-bold px-4 py-2 rounded-lg shadow"
          >
            Usar ubicación actual
          </button>
        </div>

        {isLoaded && (
          <GoogleMap
            mapContainerStyle={containerStyle}
            center={coordenadasCliente || { lat: -1.6743, lng: -78.6486 }}
            zoom={15}
            onClick={handleMapClick}
          >
            {coordenadasCliente && (
              <Marker position={coordenadasCliente} icon="http://maps.google.com/mapfiles/ms/icons/red-dot.png" />
            )}

            {mostrarCoberturas && cajasNap.map((caja) => {
              const disponibles = caja.capacidad_puertos_cliente - caja.puertos_ocupados;
              if (disponibles <= 0) return null;
              return (
                <Circle
                  key={caja.id_caja}
                  center={{ lat: parseFloat(caja.latitud), lng: parseFloat(caja.longitud) }}
                  radius={parseFloat(caja.radio_cobertura)}
                  options={{
                    fillColor: '#10b981',
                    fillOpacity: 0.15,
                    strokeColor: '#059669',
                    strokeWeight: 2
                  }}
                />
              );
            })}

          </GoogleMap>
        )}
      </div>
    </div>
  );
};

export default VerificacionCoberturaPublica;