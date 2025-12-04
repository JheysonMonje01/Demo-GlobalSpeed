import React, { useEffect, useRef, useState } from "react";
import {
  GoogleMap,
  Marker,
  DirectionsRenderer,
} from "@react-google-maps/api";
import { toast } from "react-toastify";

const containerStyle = {
  width: "100%",
  height: "400px",
};

const MapaUbicacionContrato = ({ ubicacionSeleccionada, setUbicacionSeleccionada, setNombreUbicacion  }) => {
  const [mapCenter] = useState({ lat: -1.663550, lng: -78.654646 }); // Riobamba
  const [cajasNAP, setCajasNAP] = useState([]);
  const [cajaSeleccionada, setCajaSeleccionada] = useState(null);
  const [directions, setDirections] = useState(null);
  const mapRef = useRef(null);
  //const caja = data.caja_mas_cercana;
  


  useEffect(() => {
    obtenerCajasNap();
  }, []);

  const obtenerCajasNap = async () => {
    try {
      const res = await fetch("http://localhost:5004/cajas-nap");
      const data = await res.json();
      if (res.ok) setCajasNAP(data);
      else toast.error("❌ Error al cargar cajas NAP");
    } catch (error) {
      toast.error("❌ Error al conectar con el servidor de cajas NAP");
    }
  };

  const handleMapClick = async (event) => {
  const lat = event.latLng.lat();
  const lng = event.latLng.lng();
  setUbicacionSeleccionada({ lat, lng });
  const geocoder = new window.google.maps.Geocoder();
geocoder.geocode({ location: { lat, lng } }, (results, status) => {
  if (status === "OK" && results[0]) {
    setNombreUbicacion(results[0].formatted_address);
  } else {
    setNombreUbicacion("Dirección no encontrada");
  }
});

  try {
    const res = await fetch(`http://localhost:5004/cajas-nap/disponible-cercana?lat=${lat}&lng=${lng}`);
    const data = await res.json();
    const caja = data.caja_mas_cercana;

    if (res.ok && caja?.id_caja) {
      setCajaSeleccionada(caja); // guarda id_caja, latitud, longitud, etc.

      const directionsService = new window.google.maps.DirectionsService();
      directionsService.route(
        {
          origin: { lat, lng },
          destination: {
            lat: parseFloat(caja.latitud),
            lng: parseFloat(caja.longitud),
          },
          travelMode: window.google.maps.TravelMode.WALKING,
        },
        (result, status) => {
          if (status === window.google.maps.DirectionsStatus.OK) {
            setDirections(result);
            toast.success("✅ Caja NAP cercana encontrada");
          } else {
            toast.error("❌ No se pudo trazar la ruta");
          }
        }
      );
    } else {
      toast.error("❌ No hay cajas NAP disponibles cerca");
    }
  } catch (err) {
    toast.error("❌ Error al consultar caja NAP");
  }
};






  return (
    <div className="w-full h-[400px] rounded-lg overflow-hidden shadow-md">
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={ubicacionSeleccionada || mapCenter}
        zoom={14}
        onLoad={(map) => (mapRef.current = map)}
        onClick={handleMapClick}
      >
        {cajasNAP.map((caja) => (
          <Marker
            key={caja.id_caja}
            position={{ lat: parseFloat(caja.latitud), lng: parseFloat(caja.longitud) }}
            label={{ text: `NAP-${caja.id_caja}`, fontSize: "10px", color: "white" }}
          />
        ))}

        {ubicacionSeleccionada && (
          <Marker
            position={ubicacionSeleccionada}
            icon={{
              url: "http://maps.google.com/mapfiles/ms/icons/blue-dot.png",
            }}
          />
        )}

        {directions && <DirectionsRenderer directions={directions} />}
      </GoogleMap>
    </div>
  );
};

export default MapaUbicacionContrato;
