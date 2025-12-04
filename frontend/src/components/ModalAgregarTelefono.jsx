import React, { useState, useEffect } from 'react';
import { FaPhone } from 'react-icons/fa';
import { toast } from 'react-toastify';

const ModalAgregarTelefono = ({ visible, onClose, idEmpresa, onSuccess, telefonosExistentes = []  }) => {
  const [telefono, setTelefono] = useState('');
  const [tipo, setTipo] = useState('');

  const handleGuardar = async () => {
    if (!telefono.trim()) {
      toast.error("El número de teléfono no puede estar vacío");
      return;
    }

    if (!tipo.trim()) {
      toast.error("El tipo no puede estar vacío");
      return;
    }
    const existe = telefonosExistentes.some(t => t.telefono === telefono);
    if (existe) {
      toast.error("Ese número de teléfono ya está registrado");
      return;
    }


    try {
      const res = await fetch(`http://localhost:5002/api/empresa/${idEmpresa}/telefonos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ telefono, tipo })
      });

      const data = await res.json();

      if (res.ok) {
        toast.success("Teléfono añadido correctamente");
        onSuccess(); // Recarga la empresa
        onClose();   // Cierra el modal
      } else {
        toast.error(data.error || "Error al añadir el teléfono");
      }
    } catch (err) {
      toast.error("Error de conexión con el servidor");
      console.error(err);
    }
  };
  useEffect(() => {
  if (visible) {
    setTelefono('');
    setTipo('');
  }
}, [visible]);

  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-lg">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2"><FaPhone /> Añadir Teléfono</h3>

        <label className="block text-sm font-medium mb-1">Número de Teléfono</label>
        <input
            type="text"
            value={telefono}
            onChange={(e) => {
                const valor = e.target.value;
                // Solo acepta dígitos
                if (/^\d*$/.test(valor)) {
                setTelefono(valor);
                }
            }}
            placeholder="Ej: 0999999999"
            className="w-full px-4 py-2 border rounded mb-4 focus:outline-none focus:ring-2 focus:ring-green-400"
        />


        <label className="block text-sm font-medium mb-1">Tipo de Teléfono</label>
        <input
          type="text"
          value={tipo}
          onChange={(e) => setTipo(e.target.value)}
          placeholder=""
          className="w-full px-4 py-2 border rounded mb-4 focus:outline-none focus:ring-2 focus:ring-green-400"
        />

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded"
          >
            Cancelar
          </button>
          <button
            onClick={handleGuardar}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded"
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalAgregarTelefono;
