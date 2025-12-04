import React, { useState } from 'react';
import { FaTimes, FaEdit } from 'react-icons/fa';
import { toast } from 'react-toastify';
import Swal from 'sweetalert2';

const ModalEditarMetodoPago = ({ metodo, metodosExistentes = [], onClose, onSuccess }) => {
  const [form, setForm] = useState({
    nombre: metodo.nombre,
    descripcion: metodo.descripcion || '',
    estado: metodo.estado,
    requiere_verificacion: metodo.requiere_verificacion,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    const val = value === 'true' ? true : value === 'false' ? false : value;
    setForm((prev) => ({ ...prev, [name]: val }));
  };

  const validarNombreUnico = () => {
    const nombreLower = form.nombre.trim().toLowerCase();
    return metodosExistentes.every(
      (m) =>
        m.id_metodo_pago === metodo.id_metodo_pago || m.nombre.trim().toLowerCase() !== nombreLower
    );
  };

  const handleSubmit = async () => {
    if (form.nombre.trim() === '') {
      toast.error('El nombre es obligatorio.');
      return;
    }

    if (!validarNombreUnico()) {
      toast.warning('Ya existe otro método con ese nombre.');
      return;
    }

    try {
      const res = await fetch(`http://localhost:5008/metodos_pago/${metodo.id_metodo_pago}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(form),
      });

      const data = await res.json();
      if (res.ok) {
        toast.success('✅ Método actualizado correctamente');
        onSuccess();
        onClose();
      } else {
        toast.error(data.error || '❌ No se pudo actualizar.');
      }
    } catch (err) {
      console.error(err);
      toast.error('Error de red o del servidor.');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 bg-opacity-40">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md p-6 relative animate-fade-in border-t-4 border-green-600">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-red-600 text-lg"
        >
          <FaTimes />
        </button>

        <div className="flex items-center gap-2 mb-4">
          <FaEdit className="text-green-600 text-xl" />
          <h2 className="text-xl font-bold text-green-700">Editar Método de Pago</h2>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block font-medium text-sm text-gray-700 mb-1">Nombre:</label>
            <input
              type="text"
              name="nombre"
              value={form.nombre}
              onChange={handleChange}
              className="w-full border rounded-lg px-3 py-2 shadow-sm focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block font-medium text-sm text-gray-700 mb-1">Descripción:</label>
            <textarea
              name="descripcion"
              value={form.descripcion}
              onChange={handleChange}
              rows={3}
              className="w-full border rounded-lg px-3 py-2 shadow-sm focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="block font-medium text-sm text-gray-700 mb-1">Estado:</label>
            <select
              name="estado"
              value={form.estado}
              onChange={handleChange}
              className="w-full border rounded-lg px-3 py-2 shadow-sm focus:ring-2 focus:ring-green-500"
            >
              <option value={true}>Activo</option>
              <option value={false}>Inactivo</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-sm text-gray-700 mb-1">¿Requiere verificación?</label>
            <select
              name="requiere_verificacion"
              value={form.requiere_verificacion}
              onChange={handleChange}
              className="w-full border rounded-lg px-3 py-2 shadow-sm focus:ring-2 focus:ring-green-500"
            >
              <option value={true}>Sí</option>
              <option value={false}>No</option>
            </select>
          </div>

          <div className="pt-4 flex justify-end">
            <button
              onClick={handleSubmit}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg shadow"
            >
              Guardar Cambios
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModalEditarMetodoPago;
