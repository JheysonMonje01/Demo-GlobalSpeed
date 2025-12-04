import React, { useEffect, useState } from 'react';
import { FaTimes } from 'react-icons/fa';
import PasswordFieldWithValidation from './PasswordFieldWithValidation';
import ConfirmarContrasena from './ConfirmarContrasena';
import { toast } from 'react-toastify';
import { validarTelefonoEcuatoriano } from '../utils/validaciones';

const UsuarioEditarModal = ({ usuario, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    nombre: '',
    apellido: '',
    correo: '',
    telefono: '',
    direccion: '',
    estado: true,
    contrasena: '',
    confirmarContrasena: '',
  });
  const [cambiarPassword, setCambiarPassword] = useState(false);
  const [telefonoError, setTelefonoError] = useState('');


  useEffect(() => {
    if (usuario) {
      setFormData({
        nombre: usuario.nombre || '',
        apellido: usuario.apellido || '',
        correo: usuario.correo || '',
        telefono: usuario.telefono || '',
        direccion: usuario.direccion_domiciliaria || '',
        estado: usuario.estado || false,
        contrasena: '',
        confirmarContrasena: '',
      });
    }
  }, [usuario]);

  const handleChange = (e) => {
  const { name, value } = e.target;

  if (name === 'telefono') {
    const numbers = value.replace(/\D/g, '');

    setFormData((prev) => ({ ...prev, telefono: numbers }));

    if (numbers === '') {
      setTelefonoError('');
    } else if (!/^09/.test(numbers)) {
      setTelefonoError('Debe comenzar con 09');
    } else if (numbers.length !== 10) {
      setTelefonoError('Debe tener 10 dígitos');
    } else {
      setTelefonoError('');
    }
  } else {
    setFormData((prev) => ({ ...prev, [name]: value }));
  }
};


  

  const handleSave = async () => {
    if (cambiarPassword && formData.contrasena && formData.contrasena !== formData.confirmarContrasena) {
      toast.error('Las contraseñas no coinciden');
      return;
    }

    const payload = {
      nombre: formData.nombre,
      apellido: formData.apellido,
      correo: formData.correo,
      telefono: formData.telefono,
      direccion_domiciliaria: formData.direccion,
      estado: formData.estado,
    };

    if (cambiarPassword && formData.contrasena) {
      payload.contrasena = formData.contrasena;
    }

    if (!validarTelefonoEcuatoriano(formData.telefono)) {
      return toast.error('El número de teléfono debe empezar con 09 y tener 10 dígitos');
    }



    try {
      const res = await fetch(`http://localhost:5000/auth/usuarios-personas/${usuario.id_usuario}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error('Error al actualizar');

      toast.success('Usuario actualizado correctamente');
      onSave();
    } catch (error) {
      console.error(error);
      toast.error('Error al actualizar el usuario');
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 border-t-4 border-green-700">
        <button onClick={onClose} className="absolute -top-3 -right-3 bg-white p-1 rounded-full shadow-md hover:text-red-600">
          <FaTimes size={18} />
        </button>
        <h2 className="text-2xl font-bold text-gray-800 mb-5 text-center">Editar Usuario</h2>

        <div className="space-y-4">
          {['nombre', 'apellido', 'correo', 'direccion'].map((campo) => (
            <div key={campo} className="space-y-1">
              <label className="text-sm font-medium text-gray-700 capitalize">{campo}</label>
              <input
                type="text"
                name={campo}
                value={formData[campo]}
                onChange={handleChange}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-green-400 focus:outline-none"
              />
            </div>
          ))}

          {/* Teléfono con validación visual */}
          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">Teléfono</label>
            <input
              type="text"
              name="telefono"
              value={formData.telefono}
              onChange={handleChange}
              className={`w-full px-4 py-2 rounded-lg shadow-sm focus:outline-none focus:ring-2 ${
                formData.telefono
                  ? telefonoError
                    ? 'border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:ring-green-400'
                  : 'border-gray-300 focus:ring-green-400'
              }`}
            />
            {formData.telefono && telefonoError && (
              <p className="text-red-600 text-xs mt-1">{telefonoError}</p>
            )}
          </div>

          <div className="space-y-1">
            <label className="text-sm font-medium text-gray-700">Estado</label>
            <select
              name="estado"
              value={formData.estado}
              onChange={(e) => setFormData({ ...formData, estado: e.target.value === 'true' })}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-400"
            >
              <option value="true">Activo</option>
              <option value="false">Inactivo</option>
            </select>
          </div>

          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={cambiarPassword}
              onChange={() => setCambiarPassword(!cambiarPassword)}
              className="w-4 h-4"
            />
            <label className="text-sm font-medium text-gray-700">¿Cambiar contraseña?</label>
          </div>

          {cambiarPassword && (
            <>
              <PasswordFieldWithValidation
                value={formData.contrasena}
                onChange={(e) => setFormData({ ...formData, contrasena: e.target.value })}
              />

              <ConfirmarContrasena
                original={formData.contrasena}
                value={formData.confirmarContrasena}
                onChange={(e) => setFormData({ ...formData, confirmarContrasena: e.target.value })}
              />
            </>
          )}

          <div className="flex justify-end gap-4 mt-6">
            <button
              onClick={handleSave}
              className="bg-green-600 text-white px-6 py-2 rounded-lg shadow hover:bg-green-700 transition"
            >
              Guardar Cambios
            </button>
            <button
              onClick={onClose}
              className="bg-gray-300 text-gray-800 px-6 py-2 rounded-lg shadow hover:bg-gray-400 transition"
            >
              Cancelar
            </button>
          </div>

        </div>
      </div>
    </div>
  );
};

export default UsuarioEditarModal;
