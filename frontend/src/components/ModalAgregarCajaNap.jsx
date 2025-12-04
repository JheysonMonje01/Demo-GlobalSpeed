import React, { useState, useCallback, useRef, useEffect } from 'react';
import {
  FaTimes, FaMapMarkerAlt, FaWarehouse,
  FaSatelliteDish, FaLayerGroup, FaTrash
} from 'react-icons/fa';
import {
  GoogleMap,
  Marker,
  Circle,
  useJsApiLoader
} from '@react-google-maps/api';
import { toast } from 'react-toastify';

const containerStyle = {
  width: '100%',
  height: '100%',
};

const ModalAgregarCajaNap = ({ onClose, onSuccess, isLoaded }) => {
  const [form, setForm] = useState({
    nombre_caja_nap: '',
    ubicacion: '',
    latitud: '',
    longitud: '',
    observacion: '',
    radio_cobertura: '',
    capacidad_puertos_cliente: '',
    id_puerto_pon_olt: '',
  });

  const [marker, setMarker] = useState(null);
  const mapRef = useRef(null);
  const [puertos, setPuertos] = useState([]);
  const [tarjetas, setTarjetas] = useState([]);
  const [slotNumero, setSlotNumero] = useState(null);

  

  const getAddress = useCallback(async (lat, lng) => {
    try {
      const response = await fetch(
        `https://maps.googleapis.com/maps/api/geocode/json?latlng=${lat},${lng}&key=${import.meta.env.VITE_GOOGLE_MAPS_API_KEY}`
      );
      const data = await response.json();
      if (data.status === 'OK' && data.results.length > 0) {
        return data.results[0].formatted_address;
      }
      return `Lat: ${lat}, Lng: ${lng}`;
    } catch (error) {
      console.error("Error fetching address:", error);
      return `Lat: ${lat}, Lng: ${lng}`;
    }
  }, []);

  const handleMapClick = useCallback(async (event) => {
    const lat = event.latLng.lat();
    const lng = event.latLng.lng();
    const address = await getAddress(lat, lng);

    setForm(prev => ({
      ...prev,
      latitud: lat,
      longitud: lng,
      ubicacion: address,
    }));

    const newMarker = { lat, lng };
    setMarker(newMarker);

    if (mapRef.current) {
      mapRef.current.setCenter(newMarker);
      mapRef.current.setZoom(19);
    }
  }, [getAddress]);

  const handleClearLocation = useCallback(() => {
    setMarker(null);
    setForm(prev => ({
      ...prev,
      latitud: '',
      longitud: '',
      ubicacion: '',
      radio_cobertura: '',
    }));
  }, []);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    if (name === 'radio_cobertura' || name === 'capacidad_puertos_cliente') {
      if (!/^\d*$/.test(value)) return;
    }
    setForm(prev => ({
      ...prev,
      [name]: value,
    }));
  }, []);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();
    const errors = [];
    if (form.radio_cobertura && (isNaN(form.radio_cobertura) || parseInt(form.radio_cobertura) <= 0)) {
      errors.push("El radio de cobertura debe ser un número positivo.");
    }
    if (isNaN(form.capacidad_puertos_cliente) || parseInt(form.capacidad_puertos_cliente) <= 0) {
      errors.push("La capacidad debe ser un número positivo.");
    }
    if (!form.id_puerto_pon_olt) {
      errors.push("Debe seleccionar el Puerto PON OLT.");
    }
    if (errors.length > 0) {
      alert(errors.join("\n"));
      return;
    }
    try {
      const response = await fetch('http://localhost:5004/cajas-nap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(form),
      });
      if (response.ok) {
        toast.success('Caja NAP registrada con éxito');
        onSuccess?.();
        onClose();
      } else {
        const errorData = await response.json();
        toast.error(errorData.error || 'Error al guardar');
      }
    } catch (error) {
      console.error("Error submitting form:", error);
      toast.error('Error al guardar');
    }
  }, [form, onClose, onSuccess]);

  const onMapLoad = useCallback((map) => {
    mapRef.current = map;
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const resPuertos = await fetch('http://localhost:5004/puertos');
        const dataPuertos = await resPuertos.json();
        setPuertos(dataPuertos);
        const resTarjetas = await fetch('http://localhost:5004/tarjetas-olt');
        const dataTarjetas = await resTarjetas.json();
        setTarjetas(dataTarjetas);
      } catch (error) {
        toast.error('Error al cargar puertos o tarjetas');
      }
    };
    fetchData();
  }, []);

  const handlePuertoChange = useCallback((e) => {
    const selectedId = e.target.value;
    setForm(prev => ({ ...prev, id_puerto_pon_olt: selectedId }));
    const puerto = puertos.find(p => p.id_puerto_pon_olt === parseInt(selectedId));
    if (puerto) {
      const tarjeta = tarjetas.find(t => t.id_tarjeta_olt === puerto.id_tarjeta_olt);
      setSlotNumero(tarjeta ? tarjeta.slot_numero : null);
    }
  }, [puertos, tarjetas]);

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl overflow-hidden">
        <div className="flex justify-between items-center p-6 border-b bg-gray-50">
          <h2 className="text-2xl font-bold text-green-700">Registrar Caja NAP</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <FaTimes size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col md:flex-row">
          <div className="w-full md:w-1/2 p-6 space-y-5">
            {[{
              label: 'Nombre de la Caja', name: 'nombre_caja_nap', icon: <FaWarehouse />, type: 'text', placeholder: 'Ej: Caja Central', required: true
            }, {
              label: 'Ubicación', name: 'ubicacion', icon: <FaMapMarkerAlt />, type: 'text', placeholder: 'Ubicación detectada automáticamente', disabled: true
            }, {
              label: 'Observación', name: 'observacion', icon: <FaSatelliteDish />, type: 'text', placeholder: 'Ingrese alguna observación'
            }, {
              label: 'Radio de Cobertura', name: 'radio_cobertura', icon: <FaLayerGroup />, type: 'number', placeholder: 'Ej: 500'
            }, {
              label: 'Capacidad de Puertos', name: 'capacidad_puertos_cliente', icon: <FaLayerGroup />, type: 'number', placeholder: 'Ej: 10', required: true
            }].map(({ label, name, icon, placeholder, ...rest }) => (
              <div key={name} className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">{label}</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-gray-500">
                    {icon}
                  </div>
                  <input
                    name={name}
                    value={form[name]}
                    onChange={handleChange}
                    className={`block w-full pl-10 pr-3 py-2 border rounded-md shadow-sm sm:text-sm focus:outline-none focus:ring-2 focus:ring-green-500 ${form[name] ? 'border-green-500' : 'border-gray-300'}`}
                    placeholder={placeholder}
                    {...rest}
                  />
                </div>
              </div>
            ))}

            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Puerto PON OLT</label>
              <select
                name="id_puerto_pon_olt"
                value={form.id_puerto_pon_olt}
                onChange={handlePuertoChange}
                className="w-full border rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-green-500"
                required
              >
                <option value="">Seleccionar puerto...</option>
                {puertos.map(p => {
                    const tarjeta = tarjetas.find(t => t.id_tarjeta_olt === p.id_tarjeta_olt);
                    return (
                        <option key={p.id_puerto_pon_olt} value={p.id_puerto_pon_olt}>
                        Puerto {p.numero_puerto} - Slot {tarjeta?.slot_numero ?? 'Desconocido'}
                        </option>
                    );
                    })}
              </select>
              {slotNumero !== null && (
                <p className="text-sm text-gray-600">
                  Slot asociado: <strong>{slotNumero}</strong>
                </p>
              )}
            </div>

            <button
              type="submit"
              className="w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              Guardar
            </button>
          </div>

          <div className="w-full md:w-1/2 p-6 bg-gray-50">
            <div className="h-[420px] w-full rounded-xl shadow-lg overflow-hidden relative">
              {isLoaded ? (
                <>
                  <GoogleMap
                    mapContainerStyle={containerStyle}
                    center={marker || { lat: -1.6743, lng: -78.6486 }}
                    zoom={marker ? 17.7 : 14}
                    onClick={handleMapClick}
                    onLoad={onMapLoad}
                  >
                    {marker && <Marker position={marker} />}
                    {marker && form.radio_cobertura && (
                      <Circle
                        center={marker}
                        radius={parseInt(form.radio_cobertura)}
                        options={{
                          strokeColor: '#10b981',
                          strokeOpacity: 0.8,
                          strokeWeight: 2,
                          fillColor: '#10b981',
                          fillOpacity: 0.2,
                        }}
                      />
                    )}
                  </GoogleMap>
                  {marker && (
                    <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2">
                      <button
                        type="button"
                        onClick={handleClearLocation}
                        className="flex items-center justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-500 hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      >
                        <FaTrash className="mr-2" /> Borrar Ubicación
                      </button>
                    </div>
                  )}
                </>
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  Cargando mapa...
                </div>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ModalAgregarCajaNap;
