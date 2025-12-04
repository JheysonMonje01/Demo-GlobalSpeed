import React, { useEffect, useState } from 'react';
import { FaTimes } from 'react-icons/fa';
import { toast } from 'react-toastify';

const ModalEditarTarjetaOLT = ({ isOpen, onClose, onSave, tarjeta }) => {
  const [form, setForm] = useState({
    nombre: '',
    capacidad_puertos_pon: '',
    id_olt: '',
    slot_numero: '',
    estado: true
  });

  const [olts, setOlts] = useState([]);
  const [slotsDisponibles, setSlotsDisponibles] = useState([]);

  useEffect(() => {
    if (isOpen && tarjeta) {
      setForm({
        nombre: tarjeta.nombre || '',
        capacidad_puertos_pon: tarjeta.capacidad_puertos_pon || '',
        id_olt: tarjeta.id_olt || '',
        slot_numero: tarjeta.slot_numero || '',
        estado: tarjeta.estado ?? true
      });
      fetchOLTs();
    }
  }, [isOpen, tarjeta]);

  useEffect(() => {
    if (form.id_olt) {
      cargarSlotsDisponibles(form.id_olt);
    }
  }, [form.id_olt]);

  const fetchOLTs = async () => {
    try {
      const res = await fetch('http://localhost:5004/olts');
      const data = await res.json();
      setOlts(data);
    } catch (error) {
      toast.error('Error al cargar las OLTs');
    }
  };

  const cargarSlotsDisponibles = async (id_olt) => {
    try {
      const res = await fetch(`http://localhost:5004/olts/${id_olt}`);
      const olt = await res.json();

      const resTarjetas = await fetch(`http://localhost:5004/tarjetas-olt?id_olt=${id_olt}`);
      const tarjetas = await resTarjetas.json();

      const slotsOcupados = tarjetas
        .filter(t => t.id_tarjeta_olt !== tarjeta.id_tarjeta_olt) // excluir el slot actual
        .map(t => t.slot_numero);

      const disponibles = [];
      for (let i = 0; i < olt.capacidad; i++) {
        if (!slotsOcupados.includes(i) || i === tarjeta.slot_numero) {
          disponibles.push(i);
        }
      }

      setSlotsDisponibles(disponibles);
    } catch (error) {
      toast.error('Error al obtener los slots disponibles');
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      nombre: form.nombre.trim(),
      capacidad_puertos_pon: parseInt(form.capacidad_puertos_pon),
      id_olt: parseInt(form.id_olt),
      slot_numero: parseInt(form.slot_numero),
      estado: form.estado
    };

    try {
      const res = await fetch(`http://localhost:5004/tarjetas-olt/${tarjeta.id_tarjeta_olt}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        toast.success('Tarjeta actualizada correctamente ✅');
        onSave();
        onClose();
        setForm({
          nombre: '',
          capacidad_puertos_pon: '',
          id_olt: '',
          slot_numero: '',
          estado: true
        });
      } else {
        const err = await res.json();
        toast.error(err.message || 'Error al actualizar');
      }
    } catch (error) {
      toast.error('Error de red al actualizar');
    }
  };

  if (!isOpen || !tarjeta) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 border-t-4 border-green-700">
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-gray-500 hover:text-gray-700"
        >
          <FaTimes />
        </button>

        <h2 className="text-xl font-bold mb-6 text-gray-800">Editar Tarjeta OLT</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Nombre */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre</label>
            <input
              type="text"
              name="nombre"
              value={form.nombre}
              onChange={handleChange}
              required
              className="w-full border border-gray-300 px-3 py-2 rounded-md"
            />
          </div>

          {/* Capacidad */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Capacidad (puertos PON)</label>
            <input
              type="number"
              name="capacidad_puertos_pon"
              value={form.capacidad_puertos_pon}
              onChange={handleChange}
              required
              min={1}
              className="w-full border border-gray-300 px-3 py-2 rounded-md"
            />
          </div>

          {/* OLT asociada */}
          {/* <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">OLT asociada</label>
            <select
              name="id_olt"
              value={form.id_olt}
              onChange={handleChange}
              required
              className="w-full border border-gray-300 px-3 py-2 rounded-md"
            >
              <option value="">-- Selecciona una OLT --</option>
              {olts.map(olt => (
                <option key={olt.id_olt} value={olt.id_olt}>
                  {olt.marca} {olt.modelo} (IP: {olt.ip_gestion})
                </option>
              ))}
            </select>
          </div>*/}

          {/* Slot */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Slot en la OLT</label>
            <select
              name="slot_numero"
              value={form.slot_numero}
              onChange={handleChange}
              required
              className="w-full border border-gray-300 px-3 py-2 rounded-md"
            >
              <option value="">-- Selecciona un slot --</option>
              {slotsDisponibles.map((slot) => (
                <option key={slot} value={slot}>
                  Slot {slot}
                </option>
              ))}
            </select>
          </div>

          {/* Estado */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Estado</label>
            <div className="flex space-x-4">
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

          {/* Guardar */}
          <div className="flex gap-4 mt-4">
            <button
              type="submit"
              className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md font-semibold"
            >
              Guardar cambios
            </button>
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md font-semibold"
            >
              Cancelar
            </button>
          </div>

        </form>
      </div>
    </div>
  );
};

export default ModalEditarTarjetaOLT;
