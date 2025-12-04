import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';
import Swal from 'sweetalert2';
import { Eye, EyeOff, PlusCircle } from 'lucide-react';

const ModalNuevoRouter = ({ isOpen, onClose, onCreated }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    host: '',
    puerto: 22,
    usuario: '',
    contrasena: ''
  });

  const [showPassword, setShowPassword] = useState(false);
  const [testSuccess, setTestSuccess] = useState(false);
  const clavePrivada = '/app/.ssh/id_rsa';

  useEffect(() => {
    if (isOpen) {
      setFormData({ nombre: '', host: '', puerto: 22, usuario: '', contrasena: '' });
      setTestSuccess(false);
    }
  }, [isOpen]);

  const validarIP = (ip) => {
    const ipRegex = /^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$/;
    return ipRegex.test(ip);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (name === 'host' || name === 'usuario') setTestSuccess(false);
  };

  const handleTest = async () => {
    if (!validarIP(formData.host)) {
      toast.error("IP inválida. Usa un formato correcto como 192.168.1.1");
      return;
    }

    Swal.fire({
      title: 'Verificando conexión SSH...',
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      }
    });

    try {
      const res = await fetch('http://localhost:5002/mikrotik/test-conexion-ssh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          host: formData.host,
          puerto: formData.puerto,
          usuario: formData.usuario,
          clave_privada: clavePrivada
        })
      });

      const result = await res.json();
      Swal.close();

      if (res.ok && result.status === 'success') {
        Swal.fire({
          icon: 'success',
          title: '¡Conexión exitosa!',
          text: result.message,
          timer: 2500,
          showConfirmButton: false
        });
        setTestSuccess(true);
      } else {
        Swal.fire({
          icon: 'error',
          title: 'Error en la prueba',
          text: result.message || "Fallo en la prueba de conexión."
        });
      }
    } catch (err) {
      Swal.close();
      Swal.fire({
        icon: 'error',
        title: 'Error inesperado',
        text: err.message
      });
    }
  };

  const handleSubmit = async () => {
    try {
      const payload = { ...formData, clave_privada: clavePrivada };
      const res = await fetch('http://localhost:5002/mikrotik/configurar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      if (res.ok && result.status === 'success') {
        toast.success("Router agregado correctamente ✔️");
        onCreated();
        onClose();
      } else {
        toast.error(result.message || "Error al guardar.");
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
          <PlusCircle size={24} />
          <h2 className="text-xl font-bold">Agregar Nuevo Router</h2>
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
        </div>

        <div className="flex justify-between mt-6">
          <button
            onClick={handleTest}
            className="bg-yellow-500 hover:bg-yellow-600 text-white font-medium px-4 py-2 rounded-lg transition shadow"
          >
            Test de Conexión
          </button>

          <div className="space-x-2">
            <button
              onClick={onClose}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-medium px-4 py-2 rounded-lg transition"
            >
              Cancelar
            </button>
            <button
              onClick={handleSubmit}
              disabled={!testSuccess}
              className={`px-4 py-2 rounded-lg font-medium shadow transition ${
                testSuccess
                  ? 'bg-blue-600 hover:bg-blue-700 text-white'
                  : 'bg-gray-400 text-gray-200 cursor-not-allowed'
              }`}
            >
              Agregar
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModalNuevoRouter;
