import React, { useEffect, useState, useCallback } from "react";
import { GoogleMap, Marker, Circle, useJsApiLoader } from "@react-google-maps/api";

const containerStyle = {
  width: "100%",
  height: "300px",
};

const UbicacionSection = ({ lat, lng, setLat, setLng, direccion, setDireccion }) => {
  const [cajasNap, setCajasNap] = useState([]);

  const { isLoaded, loadError } = useJsApiLoader({
    googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
    libraries: ["places"],
  });

  const defaultCenter = {
    lat: lat || -1.676063,
    lng: lng || -78.648529,
  };

  const onMapClick = async (event) => {
    const newLat = event.latLng.lat();
    const newLng = event.latLng.lng();
    setLat(newLat);
    setLng(newLng);

    const geocoder = new window.google.maps.Geocoder();
    geocoder.geocode({ location: { lat: newLat, lng: newLng } }, (results, status) => {
      if (status === "OK" && results[0]) {
        setDireccion(results[0].formatted_address);
      } else {
        setDireccion("Dirección no encontrada");
      }
    });
  };

  const fetchCajasNap = async () => {
    try {
      const res = await fetch("http://localhost:5004/cajas-nap");
      const data = await res.json();
      setCajasNap(data);
    } catch (error) {
      console.error("Error al obtener cajas NAP:", error);
    }
  };

  useEffect(() => {
    if (isLoaded) fetchCajasNap();
  }, [isLoaded]);

  if (loadError) return <p className="text-red-500">❌ Error al cargar el mapa</p>;
  if (!isLoaded) return <p>🗺️ Cargando mapa...</p>;

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-700 flex items-center">
        📍 Ubicación del Cliente
      </h2>

      <GoogleMap
        mapContainerStyle={containerStyle}
        center={{ lat: lat || defaultCenter.lat, lng: lng || defaultCenter.lng }}
        zoom={16}
        onClick={onMapClick}
      >
        {lat && lng && <Marker position={{ lat, lng }} />}
        {cajasNap.map((caja) => (
          <Circle
            key={caja.id_caja}
            center={{ lat: caja.latitud, lng: caja.longitud }}
            radius={caja.radio_cobertura}
            options={{
              strokeColor: "#2c7a7b",
              fillColor: "#81e6d9",
              fillOpacity: 0.3,
              strokeOpacity: 0.6,
            }}
          />
        ))}
      </GoogleMap>

      <input
        type="text"
        value={lat || ""}
        placeholder="Latitud"
        readOnly
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        value={lng || ""}
        placeholder="Longitud"
        readOnly
        className="w-full p-2 border rounded"
      />
      <input
        type="text"
        value={direccion || ""}
        placeholder="Dirección"
        readOnly
        className="w-full p-2 border rounded"
      />
    </div>
  );
};

export default React.memo(UbicacionSection);
