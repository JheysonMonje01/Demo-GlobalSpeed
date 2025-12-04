import { useEffect, useRef, useState, useCallback } from 'react';
import { FaPlus, FaTrash, FaEdit, FaMapMarkedAlt, FaSearch } from 'react-icons/fa';
import ModalNuevoDatacenter from '../../components/ModalRegistrarDatacenter';
import { GoogleMap, Marker, useJsApiLoader } from '@react-google-maps/api';
import iconoDataCenter from '../../assets/datacenter-icon.png';
import Swal from 'sweetalert2';
import ModalEditarDatacenter from '../../components/ModalEditarDatacenter';
import GoogleMapLoader from '../../components/GoogleMapLoader';

const BASE_URL = 'http://localhost:5004/datacenters';
const centerDefault = { lat: -1.6635, lng: -78.6546 }; // Riobamba

const getIcon = () => {
  if (window.google?.maps?.Size) {
    return {
      url: iconoDataCenter,
      scaledSize: new window.google.maps.Size(35, 35),
    };
  }
  return undefined;
};


const DatacenterPage = () => {
  const [datacenters, setDatacenters] = useState([]);
  const [filtro, setFiltro] = useState('');
  const [mostrarModal, setMostrarModal] = useState(false);
  const [editarDatacenter, setEditarDatacenter] = useState(null);
  const mapRef = useRef(null);


  const fetchDataCenters = useCallback(async () => {
    try {
      const query = new URLSearchParams({ nombre: filtro }).toString();
      const response = await fetch(`${BASE_URL}?${query}`);
      if (!response.ok) throw new Error('Error al obtener los DataCenters');
      const data = await response.json();
      setDatacenters(data);
      return data;
    } catch (error) {
      console.error(error);
      return [];
    }
  }, [filtro]);

  const handleEliminar = async (id) => {
    const confirm = await Swal.fire({
      title: '¿Estás seguro?',
      text: 'Esta acción eliminará el DataCenter permanentemente.',
      icon: 'warning',
      showCancelButton: true,
      confirmButtonColor: '#d33',
      cancelButtonColor: '#3085d6',
      confirmButtonText: 'Sí, eliminar',
      cancelButtonText: 'Cancelar'
    });

    if (confirm.isConfirmed) {
      try {
        const res = await fetch(`${BASE_URL}/${id}`, { method: 'DELETE' });
        if (res.ok) {
          await fetchDataCenters();
          Swal.fire('Eliminado', 'El DataCenter ha sido eliminado.', 'success');
        } else {
          const data = await res.json();
          Swal.fire('Error', data.error || 'Error al eliminar', 'error');
        }
      } catch (err) {
        console.error('Error al eliminar:', err);
        Swal.fire('Error', 'No se pudo conectar con el servidor.', 'error');
      }
    }
  };

  const handleEditarExitoso = async () => {
    await fetchDataCenters();
    setEditarDatacenter(null);
  };

  useEffect(() => {
    fetchDataCenters();
  }, [fetchDataCenters]);

  useEffect(() => {
    if (mapRef.current && window.google?.maps?.LatLngBounds) {
      if (datacenters.length === 0) {
        mapRef.current.setCenter(centerDefault);
        mapRef.current.setZoom(13);
      } else {
        const bounds = new window.google.maps.LatLngBounds();
        datacenters.forEach(dc => {
          const lat = Number(dc.latitud);
          const lng = Number(dc.longitud);
          if (!isNaN(lat) && !isNaN(lng) && isFinite(lat) && isFinite(lng)) {
            bounds.extend(new window.google.maps.LatLng(lat, lng));
          }
        });
        if (!bounds.isEmpty()) {
          mapRef.current.fitBounds(bounds);
        }
      }
    }
  }, [datacenters]);

  const handleRegistrarExitoso = async () => {
    await fetchDataCenters();
  };

  return (
    <div className="p-3">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex flex-col md:flex-row justify-between items-center mb-6 gap-3">
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
            <FaMapMarkedAlt className="text-green-600" />
            <span>DataCenters</span>
          </h1>
          <button
            className="bg-green-600 hover:bg-green-700 text-white flex items-center gap-2 px-4 py-2 rounded shadow transition"
            onClick={() => setMostrarModal(true)}
          >
            <FaPlus /> Añadir DataCenter
          </button>
        </div>

        <div className="flex items-center gap-3 mb-5">
          <div className="relative w-full md:w-1/3">
            <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400">
              <FaSearch />
            </span>
            <input
              type="text"
              value={filtro}
              onChange={e => setFiltro(e.target.value)}
              placeholder="Buscar por nombre o ubicación"
              className="pl-10 pr-4 py-2 w-full border border-gray-300 rounded-md shadow-sm focus:ring focus:ring-green-200"
            />
          </div>
        </div>

        <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-sm mb-6">
          <table className="min-w-full table-auto text-sm">
            <thead className="bg-green-100 text-green-900 font-semibold">
              <tr>
                <th className="px-4 py-3 text-left">Nombre</th>
                <th className="px-4 py-3 text-left">Ubicación</th>
                <th className="px-4 py-3 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody className="text-gray-800">
              {datacenters.map(dc => (
                <tr key={dc.id_datacenter} className="border-t hover:bg-gray-50 transition">
                  <td className="px-4 py-2">{dc.nombre}</td>
                  <td className="px-4 py-2">{dc.ubicacion}</td>
                  <td className="px-4 py-2 text-center flex justify-center gap-4">
                    <button
                      className="text-blue-600 hover:text-blue-800"
                      onClick={() => setEditarDatacenter(dc)}
                    >
                      <FaEdit />
                    </button>
                    <button
                      className="text-red-600 hover:text-red-800"
                      onClick={() => handleEliminar(dc.id_datacenter)}
                    >
                      <FaTrash />
                    </button>
                  </td>
                </tr>
              ))}
              {datacenters.length === 0 && (
                <tr>
                  <td colSpan="3" className="text-center py-6 text-gray-500">
                    No se encontraron resultados.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
          <GoogleMapLoader>
          <div className="h-[300px] rounded-xl overflow-hidden border border-gray-300">
            <GoogleMap
              mapContainerStyle={{ width: '100%', height: '100%' }}
              onLoad={map => (mapRef.current = map)}
              options={{
                mapTypeControl: true,
                streetViewControl: false,
                fullscreenControl: false
              }}
              center={centerDefault}
              zoom={13}
            >
              {datacenters.map((dc) => (
                <Marker
                  key={dc.id_datacenter}
                  position={{ lat: parseFloat(dc.latitud), lng: parseFloat(dc.longitud) }}
                  icon={getIcon()}
                  title={dc.nombre}
                />
              ))}
            </GoogleMap>
          </div>
       </GoogleMapLoader>
      </div>

      {mostrarModal && (
        <ModalNuevoDatacenter
          onClose={() => setMostrarModal(false)}
          onSuccess={handleRegistrarExitoso}
        />
      )}

      {editarDatacenter && (
        <ModalEditarDatacenter
          datacenter={editarDatacenter}
          onClose={() => setEditarDatacenter(null)}
          onSuccess={handleEditarExitoso}
        />
      )}
    </div>
  );
};

export default DatacenterPage;
