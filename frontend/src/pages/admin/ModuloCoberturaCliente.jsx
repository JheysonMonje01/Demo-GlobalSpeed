import React, { useState, useEffect } from 'react';
import { FaMapMarkerAlt, FaSearchLocation } from 'react-icons/fa';
import {
  GoogleMap,
  Marker,
  Circle,
  DirectionsRenderer,
  useJsApiLoader, InfoWindow
} from '@react-google-maps/api';
import { toast } from 'react-toastify';
import Swal from 'sweetalert2';
import GoogleMapLoader from "../../components/GoogleMapLoader"; // asegúrate de importar bien


const containerStyle = {
  width: '100%',
  height: '500px'
};
const LIBRARIES = ['places', 'geometry'];

const ModuloCoberturaCliente = () => {
  const [direccion, setDireccion] = useState('');
  const [coordenadasCliente, setCoordenadasCliente] = useState(null);
  const [cajasNap, setCajasNap] = useState([]);
  const [directions, setDirections] = useState(null);
  const [cajaCercana, setCajaCercana] = useState(null);
  const [distanciaMetros, setDistanciaMetros] = useState(null);
  
  const [cajaSeleccionada, setCajaSeleccionada] = useState(null);
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY;



  useEffect(() => {
    const fetchCajas = async () => {
      try {
        const res = await fetch('http://localhost:5004/cajas-nap');
        const data = await res.json();
        setCajasNap(data);
      } catch (error) {
        toast.error('Error al cargar cajas NAP');
      }
    };
    fetchCajas();
  }, []);

  const geocodeDireccion = async () => {
    if (!direccion) return;
    try {
      const res = await fetch(`https://maps.googleapis.com/maps/api/geocode/json?address=${encodeURIComponent(direccion)}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`);
      const data = await res.json();
      if (data.results.length > 0) {
        const location = data.results[0].geometry.location;
        setCoordenadasCliente(location);
        verificarCobertura(location);
      } else {
        Swal.fire({
          icon: 'warning',
          title: 'Dirección no encontrada',
          text: 'No se encontró la dirección ingresada.',
          confirmButtonColor: '#facc15'
        });
      }
    } catch (err) {
      Swal.fire({
        icon: 'error',
        title: 'Error',
        text: 'Error al obtener coordenadas.',
        confirmButtonColor: '#ef4444'
      });
    }
  };

  const verificarCobertura = async (cliente) => {
  let cajaDentroCobertura = null;
  let distanciaMinima = Infinity;
  let cajaMasCercanaDisponible = null;
  
  for (const caja of cajasNap) {
    const capacidad = parseInt(caja.capacidad_puertos_cliente);
    const ocupados = parseInt(caja.puertos_ocupados);
    const disponibles = caja.capacidad_puertos_cliente - caja.puertos_ocupados;

    if (disponibles <= 0) continue;

    const distancia = google.maps.geometry.spherical.computeDistanceBetween(
      new google.maps.LatLng(cliente.lat, cliente.lng),
      new google.maps.LatLng(parseFloat(caja.latitud), parseFloat(caja.longitud))
    );

    if (distancia < distanciaMinima) {
      distanciaMinima = distancia;
      cajaMasCercanaDisponible = { ...caja, disponibles };
    }

    if (distancia <= parseFloat(caja.radio_cobertura)) {
      cajaDentroCobertura = { ...caja, disponibles };
    }
  }

  const directionsService = new google.maps.DirectionsService();

  if (cajaDentroCobertura) {
    setCajaCercana(cajaDentroCobertura);
    setDistanciaMetros(distanciaMinima);

    directionsService.route(
      {
        origin: new google.maps.LatLng(cliente.lat, cliente.lng),
        destination: new google.maps.LatLng(parseFloat(cajaDentroCobertura.latitud), parseFloat(cajaDentroCobertura.longitud)),
        travelMode: google.maps.TravelMode.WALKING,
      },
      (result, status) => {
        if (status === 'OK') {
          setDirections(result);
          Swal.fire({
            icon: 'success',
            title: '¡Cobertura disponible!',
            html: `
              <p><strong>Caja NAP:</strong> ${cajaDentroCobertura.nombre_caja_nap}</p>
              <p><strong>Distancia:</strong> ${Math.round(distanciaMinima)} metros</p>
              <p><strong>Puertos disponibles:</strong> ${cajaDentroCobertura.disponibles}</p>
              <p>El cliente está dentro del área de cobertura.</p>
            `,
            confirmButtonColor: '#10b981'
          });
        }
      }
    );
  } else if (cajaMasCercanaDisponible) {
    setCajaCercana(cajaMasCercanaDisponible);
    setDistanciaMetros(distanciaMinima);

    directionsService.route(
      {
        origin: new google.maps.LatLng(cliente.lat, cliente.lng),
        destination: new google.maps.LatLng(parseFloat(cajaMasCercanaDisponible.latitud), parseFloat(cajaMasCercanaDisponible.longitud)),
        travelMode: google.maps.TravelMode.WALKING,
      },
      (result, status) => {
        if (status === 'OK') {
          setDirections(result);
          Swal.fire({
            icon: 'info',
            title: 'Fuera de cobertura',
            html: `
              <p>No hay cobertura directa en esta ubicación.</p>
              <p><strong>Caja NAP más cercana:</strong> ${cajaMasCercanaDisponible.nombre_caja_nap}</p>
              <p><strong>Distancia:</strong> ${Math.round(distanciaMinima)} metros</p>
              <p><strong>Puertos disponibles:</strong> ${cajaMasCercanaDisponible.disponibles}</p>
              <p>Se ha trazado la ruta hasta la caja más cercana.</p>
            `,
            confirmButtonColor: '#3b82f6'
          });
        }
      }
    );
  } else {
    setCajaCercana(null);
    setDirections(null);
    Swal.fire({
      icon: 'error',
      title: 'Sin cobertura ni puertos disponibles',
      html: `
        <p>No hay ninguna caja NAP cercana con puertos libres.</p>
        <p>Por favor, contacte al administrador.</p>
      `,
      confirmButtonColor: '#ef4444'
    });
  }
};






  const handleMapClick = (e) => {
    const lat = e.latLng.lat();
    const lng = e.latLng.lng();
    const location = { lat, lng };
    setDireccion('');
    setCoordenadasCliente(location);
    verificarCobertura(location);
  };

  return (
    
    <div className="p-6 bg-white rounded-xl shadow-lg">
      <h2 className="text-2xl font-bold text-green-700 mb-4 flex items-center gap-2">
        <FaSearchLocation /> Verificación de Cobertura
      </h2>
      <div className="mb-6 flex flex-col md:flex-row md:items-end gap-4">
 <div className="mb-6">
  <label className="text-sm font-medium text-gray-700 block mb-1">
    Dirección del Cliente (o haz clic en el mapa)
  </label>
  
  <div className="flex flex-col md:flex-row md:items-center gap-5">
    <input
      type="text"
      value={direccion}
      onChange={(e) => setDireccion(e.target.value)}
      placeholder="Ej: Av. Quito y 10 de Agosto"
      className="w-full md:w-[980px] border px-4 py-2 rounded-md"
    />

    <button
      onClick={geocodeDireccion}
      className="bg-green-600 hover:bg-green-700 text-white px-5 py-2 rounded-md shadow flex items-center gap-2 h-[42px]"
    >
      <FaSearchLocation className="text-white" />
      Verificar Cobertura
    </button>
  </div>

  <p className="text-xs text-gray-500 mt-1">
    También puedes hacer clic en el mapa para ubicar al cliente.
  </p>
</div>

</div>


      
      
        <div className="w-full h-[500px]">
          <GoogleMap
            mapContainerStyle={containerStyle}
            center={coordenadasCliente || { lat: -1.6743, lng: -78.6486 }}
            zoom={15}
            onClick={handleMapClick}
          >
            {coordenadasCliente && <Marker position={coordenadasCliente} icon="http://maps.google.com/mapfiles/ms/icons/red-dot.png" />}
            {cajasNap.map((caja) => {
              const capacidad = parseInt(caja.capacidad_puertos_cliente);
              const ocupados = parseInt(caja.puertos_ocupados);
              const disponibles = capacidad - ocupados;
              const esSaturada = disponibles <= 0;

              return (
                <React.Fragment key={caja.id_caja}>
                  <Marker
                    position={{ lat: parseFloat(caja.latitud), lng: parseFloat(caja.longitud) }}
                    icon={`http://maps.google.com/mapfiles/ms/icons/${esSaturada ? 'red' : 'green'}-dot.png`}
                    onClick={() => setCajaSeleccionada(caja)}
                  />
                  <Circle
                    center={{ lat: parseFloat(caja.latitud), lng: parseFloat(caja.longitud) }}
                    radius={parseFloat(caja.radio_cobertura)}
                    options={{
                      fillColor: esSaturada ? '#ef4444' : '#10b981',
                      fillOpacity: 0.15,
                      strokeColor: esSaturada ? '#b91c1c' : '#059669',
                      strokeWeight: 2,
                      clickable: false,
                      zIndex: 1
                    }}
                  />
                </React.Fragment>
              );
            })}


            {cajaSeleccionada && (
              <InfoWindow
                position={{ lat: parseFloat(cajaSeleccionada.latitud), lng: parseFloat(cajaSeleccionada.longitud) }}
                onCloseClick={() => setCajaSeleccionada(null)}
              >
                <div className="text-sm">
                  <p><strong>{cajaSeleccionada.nombre_caja_nap}</strong></p>
                  <p>Ubicación: {cajaSeleccionada.ubicacion}</p>
                  <p>Puertos ocupados: {cajaSeleccionada.puertos_ocupados}</p>
                  <p>Capacidad: {cajaSeleccionada.capacidad_puertos_cliente}</p>
                  <p><strong>Disponibles:</strong> {cajaSeleccionada.capacidad_puertos_cliente - cajaSeleccionada.puertos_ocupados}</p>
                </div>
              </InfoWindow>
            )}

            {directions && <DirectionsRenderer directions={directions} />}
          </GoogleMap>
        </div>
      
    </div>
  );
};

export default ModuloCoberturaCliente;
