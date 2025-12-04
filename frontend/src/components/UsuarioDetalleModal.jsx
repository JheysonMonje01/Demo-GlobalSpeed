import React from 'react';
import { FaTimes, FaEnvelope, FaPhone, FaIdCard, FaMapMarkerAlt, FaCalendarAlt, FaUserShield } from 'react-icons/fa';

const UsuarioDetalleModal = ({ usuario, onClose }) => {
  if (!usuario) return null;

  const formatearFecha = (fecha) => {
    try {
      return new Date(fecha).toLocaleDateString('es-EC', {
        day: '2-digit', month: '2-digit', year: 'numeric'
      });
    } catch {
      return 'No disponible';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
      <div className="bg-white rounded-3xl p-8 w-full max-w-md shadow-2xl relative animate-fade-in">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-red-500"
        >
          <FaTimes size={20} />
        </button>

        <div className="text-center">
          <img
            src={usuario.foto ? `data:image/jpeg;base64,${usuario.foto}` : "/imagenes/perfil-none.avif"}
            alt="Foto perfil"
            className="w-28 h-28 mx-auto rounded-full object-cover border-2 border-green-500 shadow-lg"
          />
          <h2 className="mt-4 text-2xl font-bold text-green-700">
            {usuario.nombre} {usuario.apellido}
          </h2>
          <p className="text-sm text-gray-500 mb-4 italic flex items-center justify-center gap-1 ">
             {usuario.rol}
          </p>
        </div>

        <div className="text-[15px] text-gray-800 space-y-3 px-2">
          <p className="flex items-center gap-2"><FaEnvelope className="text-green-600" /><span className="font-semibold">Correo:</span> {usuario.correo}</p>
          <p className="flex items-center gap-2"><FaPhone className="text-green-600" /><span className="font-semibold">Teléfono:</span> {usuario.telefono}</p>
          <p className="flex items-center gap-2"><FaIdCard className="text-green-600" /><span className="font-semibold">Cédula:</span> {usuario.cedula_ruc}</p>
          <p className="flex items-center gap-2"><FaMapMarkerAlt className="text-green-600" /><span className="font-semibold">Dirección:</span> {usuario.direccion_domiciliaria}</p>
          <p className="flex items-center gap-2"><FaCalendarAlt className="text-green-600" /><span className="font-semibold">Fecha de creación:</span> {formatearFecha(usuario.fecha_creacion)}</p>
          <p className="flex items-center gap-2">
            <span className="font-semibold">Estado:</span>
            <span className={`font-semibold px-2 py-1 rounded-full text-white text-xs ${usuario.estado ? 'bg-green-500' : 'bg-red-500'}`}>
              {usuario.estado ? 'Activo' : 'Inactivo'}
            </span>
          </p>
        </div>
      </div>
    </div>
  );
};

export default UsuarioDetalleModal;
