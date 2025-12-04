import React, { useState, useEffect } from 'react';
import { FaEnvelope } from 'react-icons/fa';
import { toast } from 'react-toastify';

const ModalAgregarCorreo = ({ visible, onClose, idEmpresa, onSuccess, correosExistentes = [] }) => {
  const [correo, setCorreo] = useState('');
  const [tipo, setTipo] = useState('');

  useEffect(() => {
    if (visible) {
      setCorreo('');
      setTipo('');
    }
  }, [visible]);

  const validarEmail = (email) => {
    // Validación básica de email
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const handleGuardar = async () => {
    if (!correo.trim()) {
      toast.error("El correo no puede estar vacío");
      return;
    }

    if (!validarEmail(correo)) {
      toast.error("Formato de correo inválido");
      return;
    }

    if (!tipo.trim()) {
      toast.error("El tipo no puede estar vacío");
      return;
    }

    const yaExiste = correosExistentes.some(c => c.correo === correo);
    if (yaExiste) {
      toast.error("Ese correo ya está registrado");
      return;
    }

    try {
      const res = await fetch(`http://localhost:5002/api/empresa/${idEmpresa}/correos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ correo, tipo })
      });

      const data = await res.json();

      if (res.ok) {
        toast.success("Correo añadido correctamente");
        onSuccess(); // recargar empresa
        onClose();   // cerrar modal
      } else {
        toast.error(data.error || "Error al añadir el correo");
      }
    } catch (err) {
      toast.error("Error de conexión con el servidor");
      console.error(err);
    }
  };

  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md shadow-lg">
        <h3 className="text-xl font-bold mb-4 flex items-center gap-2"><FaEnvelope /> Añadir Correo</h3>

        <label className="block text-sm font-medium mb-1">Correo Electrónico</label>
        <input
          type="email"
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
          placeholder="ejemplo@empresa.com"
          className="w-full px-4 py-2 border rounded mb-4 focus:outline-none focus:ring-2 focus:ring-green-400"
        />

        <label className="block text-sm font-medium mb-1">Tipo de Correo</label>
        <input
          type="text"
          value={tipo}
          onChange={(e) => setTipo(e.target.value)}
          placeholder="Ej: corporativo, personal..."
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

export default ModalAgregarCorreo;
