import React, { useState } from "react";
import DatePicker from "react-datepicker";
import { toast } from "react-toastify";
import "react-datepicker/dist/react-datepicker.css";
import { es } from "date-fns/locale";

const ModalEditarOrdenPago = ({ orden, onClose, onActualizarExitoso }) => {
  const parseFecha = (fechaString) => {
  // Intenta parsear ISO (YYYY-MM-DD)
  const date = new Date(fechaString);
  return isNaN(date) ? new Date() : date;
};

const [nuevaFecha, setNuevaFecha] = useState(parseFecha(orden?.fecha_vencimiento));

  const [observacion, setObservacion] = useState("");
const formatearFechaISO = (fechaDate) => {
  const fechaEcuador = new Date(fechaDate.getTime() - (fechaDate.getTimezoneOffset() * 60000)); // Ajuste a zona horaria
  return fechaEcuador.toISOString().split("T")[0]; // Solo YYYY-MM-DD
};

  const handleActualizar = async () => {
    if (!nuevaFecha || !observacion.trim()) {
      toast.error("Por favor, completa todos los campos.");
      return;
    }

    try {
      const response = await fetch(`http://localhost:5008/orden_pago/${orden.id_orden_pago}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          nueva_fecha_vencimiento: formatearFechaISO(nuevaFecha),
          observacion,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("Fecha de vencimiento actualizada correctamente");
        onActualizarExitoso(); // Recarga las órdenes
        onClose(); // Cierra el modal
      } else {
        toast.error(data.message || "Error al actualizar la fecha.");
      }
    } catch (error) {
      console.error("Error:", error);
      toast.error("Ocurrió un error en el servidor.");
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-30 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md shadow-xl border border-green-300">
        <h2 className="text-xl font-bold text-green-600 flex items-center mb-4">
          📅 Actualizar Vencimiento
        </h2>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nueva Fecha de Vencimiento
          </label>
          <DatePicker
            selected={nuevaFecha}
            onChange={(date) => setNuevaFecha(date)}
            minDate={new Date()}
            dateFormat="dd/MM/yyyy"
            locale={es}
            className="w-full px-4 py-2 border rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            placeholderText="Selecciona una fecha"
          />
        </div>

        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Observación
          </label>
          <textarea
            value={observacion}
            onChange={(e) => setObservacion(e.target.value)}
            placeholder="Motivo de la actualización..."
            className="w-full border rounded px-4 py-2 shadow-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            rows={3}
          />
        </div>

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300"
          >
            Cancelar
          </button>
          <button
            onClick={handleActualizar}
            className="px-4 py-2 rounded bg-green-600 text-white hover:bg-green-700"
          >
            Actualizar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalEditarOrdenPago;
