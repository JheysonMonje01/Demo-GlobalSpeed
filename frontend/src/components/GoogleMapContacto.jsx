import React, { useState } from "react";
import {
  GoogleMap,
  Marker,
  InfoWindow,
  useJsApiLoader,
} from "@react-google-maps/api";

const containerStyle = {
  width: "100%",
  height: "100%",
  borderRadius: "1rem",
};

const center = {
  lat: -1.6728838891176219, // Coordenadas de la intersección (Primera Constituyente y Eugenio Espejo)
  lng: -78.64912926059873,
};

const GoogleMapContacto = ({ isLoaded }) => {
  const [showInfo, setShowInfo] = useState(true);

  if (!isLoaded) {
    return (
      <div className="text-center text-gray-500 py-20">
        Cargando mapa...
      </div>
    );
  }



  return (
    <GoogleMap
      mapContainerStyle={containerStyle}
      center={center}
      zoom={17}
      options={{
        disableDefaultUI: true,
        zoomControl: true,
      }}
    >
      <Marker
        position={center}
        onClick={() => setShowInfo(true)}
        />
      {showInfo && (
        <InfoWindow position={center} onCloseClick={() => setShowInfo(false)}>
          <div className="text-sm text-gray-700">
            <p className="font-bold text-green-700 mb-1">
              Oficina Principal - Global Speed
            </p>
            <p>Primera Constituyente & Eugenio Espejo</p>
            <p>Riobamba, Ecuador</p>
            <a
              href="https://www.google.com/maps/place/Primera+Constituyente+y+Eugenio+Espejo,+Riobamba"
              target="_blank"
              rel="noopener noreferrer"
              className="text-green-600 underline text-sm"
            >
              Ver en Google Maps
            </a>
          </div>
        </InfoWindow>
      )}
    </GoogleMap>
  ) 
};

export default React.memo(GoogleMapContacto);
