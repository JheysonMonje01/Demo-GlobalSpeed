import React, { useState, useEffect } from 'react';
import { FaTimes, FaEye, FaEyeSlash } from 'react-icons/fa';
import { toast } from 'react-toastify';

const ModalEditarOLT = ({ isOpen, onClose, olt, onSave }) => {
  const [form, setForm] = useState({
    modelo: '',
    marca: '',
    ip_gestion: '',
    capacidad: '',
    estado: true,
    usuario_gestion: '',
    contrasena_gestion: ''
  });

  const [verContrasena, setVerContrasena] = useState(false);

  useEffect(() => {
    if (olt) {
      setForm({
        modelo: olt.modelo || '',
        marca: olt.marca || '',
        ip_gestion: olt.ip_gestion || '',
        capacidad: olt.capacidad || '',
        estado: olt.estado ?? true,
        usuario_gestion: olt.usuario_gestion || '',
        contrasena_gestion: ''
      });
    }
  }, [olt]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!olt) return;

    const dataToSend = {};
    for (const key in form) {
      if (form[key] !== '' && form[key] !== olt[key]) {
        dataToSend[key] = key === 'capacidad' ? parseInt(form[key]) : form[key];
      }
    }

    // Si quiere cambiar la contraseña, debe haber algo nuevo escrito
    if (form.contrasena_gestion.trim() !== '') {
      dataToSend.contrasena_gestion = form.contrasena_gestion;
    }

    try {
      const res = await fetch(`http://localhost:5004/olts/${olt.id_olt}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dataToSend)
      });

      if (res.ok) {
        toast.success('OLT actualizada correctamente 🎉');
        onSave();
        onClose();
      } else {
        const errorData = await res.json();
        toast.error(errorData?.error || 'Error al actualizar la OLT');
      }
    } catch (error) {
      console.error('Error:', error);
      toast.error('Ocurrió un error inesperado');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 border-t-4 border-green-700">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
        >
          <FaTimes size={18} />
        </button>

        <h2 className="text-2xl font-bold text-center text-gray-800 mb-6">Editar OLT</h2>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">

          <div>
            <label className="block font-medium text-gray-700 mb-1">Modelo</label>
            <input
              type="text"
              name="modelo"
              value={form.modelo}
              onChange={handleChange}
              placeholder="Ej: MA5800-X7"
              className="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-green-400"
            />
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">Marca</label>
            <input
              type="text"
              name="marca"
              value={form.marca}
              onChange={handleChange}
              placeholder="Ej: Huawei, ZTE"
              className="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-green-400"
            />
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">IP de gestión</label>
            <input
              type="text"
              name="ip_gestion"
              value={form.ip_gestion}
              onChange={handleChange}
              placeholder="Ej: 192.168.1.10"
              pattern="^(\d{1,3}\.){3}\d{1,3}$"
              title="Ingrese una IP válida. Ej: 192.168.0.1"
              className="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-green-400"
            />
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">Capacidad de puertos</label>
            <input
              type="number"
              name="capacidad"
              min={1}
              value={form.capacidad}
              onChange={handleChange}
              placeholder="Ej: 16"
              className="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-green-400"
            />
          </div>

          <div>
            <label className="block font-medium text-gray-700 mb-1">Usuario de gestión</label>
            <input
              type="text"
              name="usuario_gestion"
              value={form.usuario_gestion}
              onChange={handleChange}
              placeholder="Ej: admin"
              className="w-full border border-gray-300 px-3 py-2 rounded-lg focus:ring-2 focus:ring-green-400"
            />
          </div>

          <div className="relative">
            <label className="block font-medium text-gray-700 mb-1">Contraseña de gestión</label>
            <input
              type={verContrasena ? 'text' : 'password'}
              name="contrasena_gestion"
              value={form.contrasena_gestion}
              onChange={handleChange}
              placeholder="Nueva contraseña (opcional)"
              className="w-full border border-gray-300 px-3 py-2 rounded-lg pr-10 focus:ring-2 focus:ring-green-400"
            />
            <button
              type="button"
              onClick={() => setVerContrasena(!verContrasena)}
              className="absolute right-3 top-9 text-gray-500 hover:text-gray-700"
            >
              {verContrasena ? <FaEyeSlash /> : <FaEye />}
            </button>
          </div>

          <div className="sm:col-span-2">
            <label className="block font-medium text-gray-700 mb-1">Estado</label>
            <div className="flex gap-4">
              <button
                type="button"
                onClick={() => setForm({ ...form, estado: true })}
                className={`px-4 py-1 rounded-full text-sm font-semibold border ${
                  form.estado
                    ? 'bg-green-500 text-white border-green-600'
                    : 'bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200'
                }`}
              >
                Activo
              </button>
              <button
                type="button"
                onClick={() => setForm({ ...form, estado: false })}
                className={`px-4 py-1 rounded-full text-sm font-semibold border ${
                  !form.estado
                    ? 'bg-red-500 text-white border-red-600'
                    : 'bg-gray-100 text-gray-600 border-gray-300 hover:bg-gray-200'
                }`}
              >
                Inactivo
              </button>
            </div>
          </div>

          <div className="sm:col-span-2 flex gap-4 mt-2">
            <button
              type="submit"
              className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-3 rounded-lg font-semibold"
            >
              Guardar Cambios
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-3 rounded-lg font-semibold"
            >
              Cancelar
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};

export default ModalEditarOLT;
