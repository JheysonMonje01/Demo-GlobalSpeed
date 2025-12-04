import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Swal from 'sweetalert2';
import { Eye, EyeOff, Router } from 'lucide-react';
import 'react-toastify/dist/ReactToastify.css';

const ModalEditarRouter = ({ isOpen, onClose, routerData, onUpdated }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    host: '',
    usuario: '',
    contrasena: '',
    estado: true
  });

  const [showPassword, setShowPassword] = useState(false);
  const [originalHost, setOriginalHost] = useState('');
  const [originalUsuario, setOriginalUsuario] = useState('');

  useEffect(() => {
    if (routerData) {
      setFormData({
        nombre: routerData.nombre || '',
        host: routerData.host || '',
        usuario: routerData.usuario || '',
        contrasena: routerData.contrasena || '',
        estado: routerData.estado
      });
      setOriginalHost(routerData.host || '');
      setOriginalUsuario(routerData.usuario || '');
    }
  }, [routerData]);

  const validarIP = (ip) => {
    const ipRegex = /^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$/;
    return ipRegex.test(ip);
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async () => {
    if (!validarIP(formData.host)) {
      toast.error("IP inválida. Usa un formato como 192.168.1.1");
      return;
    }

    const cambioHost = formData.host !== originalHost;
    const cambioUsuario = formData.usuario !== originalUsuario;

    try {
      const res = await fetch(`http://localhost:5002/mikrotik/configuraciones/${routerData.id_mikrotik}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const result = await res.json();

      if (res.ok && result.status === 'success') {
        toast.success("Configuración actualizada correctamente 🎉");

        if (cambioHost || cambioUsuario) {
          Swal.fire({
            icon: 'info',
            title: 'Recuerda realizar el test de conexión',
            text: 'Has cambiado el Host o Usuario. Verifica la conexión con el botón de test.',
            confirmButtonColor: '#3085d6'
          });
        }

        onUpdated();
        onClose();
      } else {
        toast.error(result.message || "Error al actualizar");
      }
    } catch (error) {
      toast.error("Error inesperado: " + error.message);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 border-t-4 border-green-700">
        <div className="flex items-center mb-4 space-x-2 text-green-700">
          <Router size={24} />
          <h2 className="text-xl font-bold">Editar Configuración MikroTik</h2>
        </div>

        <div className="space-y-5">
          <div>
            <label className="text-sm font-semibold text-gray-600">Nombre</label>
            <input
              type="text"
              name="nombre"
              value={formData.nombre}
              onChange={handleChange}
              className="w-full mt-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-green-400 focus:outline-none"
              placeholder="Ej. Router Principal"
            />
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-600">Host (IP)</label>
            <input
              type="text"
              name="host"
              value={formData.host}
              onChange={handleChange}
              className="w-full mt-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-green-400 focus:outline-none"
              placeholder="Ej. 192.168.1.1"
            />
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-600">Usuario</label>
            <input
              type="text"
              name="usuario"
              value={formData.usuario}
              onChange={handleChange}
              className="w-full mt-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-green-400 focus:outline-none"
              placeholder="Ej. admin"
            />
          </div>

          <div>
            <label className="text-sm font-semibold text-gray-600">Contraseña</label>
            <div className="relative mt-1">
              <input
                type={showPassword ? "text" : "password"}
                name="contrasena"
                value={formData.contrasena}
                onChange={handleChange}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-green-400 focus:outline-none pr-10"
                placeholder="••••••"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute inset-y-0 right-3 flex items-center text-gray-500 hover:text-gray-700"
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          {!routerData.estado && (
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="estado"
                name="estado"
                checked={formData.estado}
                onChange={handleChange}
                className="w-4 h-4 rounded"
              />
              <label htmlFor="estado" className="text-sm font-medium text-gray-700">
                Activar router (actualmente inactivo)
              </label>
            </div>
          )}
        </div>

        <div className="flex justify-end mt-6 space-x-3">
          <button
            onClick={onClose}
            className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium px-4 py-2 rounded-lg transition"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            className="bg-green-600 hover:bg-green-700 text-white font-medium px-4 py-2 rounded-lg transition shadow"
          >
            Guardar Cambios
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalEditarRouter;