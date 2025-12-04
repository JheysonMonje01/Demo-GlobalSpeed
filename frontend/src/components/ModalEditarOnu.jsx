import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const ModalEditarOnu = ({ onu, onClose, onSuccess }) => {
  const [serial, setSerial] = useState(onu.serial || '');
  const [modelo, setModelo] = useState(onu.modelo_onu || '');
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    setSerial(onu.serial || '');
    setModelo(onu.modelo_onu || '');
  }, [onu]);

  const handleActualizar = async () => {
    if (!serial.trim()) {
      toast.error('El campo serial es obligatorio');
      return;
    }

    setEnviando(true);
    try {
      const res = await fetch(`http://localhost:5004/onus/${onu.id_onu}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ serial: serial.trim(), modelo_onu: modelo || null })
      });
      const data = await res.json();
      if (res.ok) {
        toast.success('ONU actualizada correctamente');
        onSuccess();
        onClose();
      } else {
        toast.error(data.message);
      }
    } catch (err) {
      toast.error('Error al actualizar la ONU');
    } finally {
      setEnviando(false);
    }
  };

  return (
   <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 border-t-4 border-green-700">
        <h2 className="text-2xl font-semibold text-green-700 mb-4">Editar ONU</h2>

        <div className="mb-4">
          <label className="block mb-1 font-medium text-gray-700">Serial *</label>
          <input
            type="text"
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            value={serial}
            onChange={(e) => setSerial(e.target.value)}
            placeholder="Ingrese el nuevo serial"
          />
        </div>

        <div className="mb-4">
          <label className="block mb-1 font-medium text-gray-700">Modelo (opcional)</label>
          <input
            type="text"
            className="w-full border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500"
            value={modelo}
            onChange={(e) => setModelo(e.target.value)}
            placeholder="Ej: Huawei HG8546M"
          />
        </div>

        <div className="flex justify-end gap-3 mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 text-gray-800 rounded hover:bg-gray-400"
            disabled={enviando}
          >
            Cancelar
          </button>
          <button
            onClick={handleActualizar}
            className="px-5 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            disabled={enviando}
          >
            {enviando ? 'Guardando...' : 'Actualizar'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalEditarOnu;
