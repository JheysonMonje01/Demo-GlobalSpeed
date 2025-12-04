// GoogleMapLoader.jsx

import React from 'react';
import { useJsApiLoader } from '@react-google-maps/api';
import { toast } from 'react-toastify';

const LIBRARIES = ['places', 'geometry']; // ✅ fuera del componente

const GoogleMapLoader = ({ children }) => {
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-maps-script-loader', // ✅ importante para prevenir duplicados
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries: LIBRARIES, // ✅ siempre el mismo array
    language: 'es',
    region: 'EC',
  });

  if (loadError) {
    toast.error('Error al cargar Google Maps');
    return <div className="text-center p-6 text-red-600">No se pudo cargar el mapa</div>;
  }

  if (!isLoaded) {
    return <div className="text-center p-6 text-gray-500">Cargando mapa...</div>;
  }

  return <>{typeof children === 'function' ? children({ isLoaded }) : children}</>;

};

export default GoogleMapLoader;
