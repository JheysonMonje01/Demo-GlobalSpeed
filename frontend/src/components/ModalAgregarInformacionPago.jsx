import React, { useState, useEffect } from 'react';
import { toast } from 'react-toastify';

const ModalAgregarInfoPago = ({ onClose, onSuccess }) => {
  const [form, setForm] = useState({
    nombre_beneficiario: '',
    entidad_financiera: '',
    numero_cuenta: '',
    tipo_cuenta: '',
    id_metodo_pago: '',
    instrucciones: '',
    estado: true,
  });

  const [metodosPago, setMetodosPago] = useState([]);

  useEffect(() => {
    fetch('http://localhost:5008/metodos_pago/buscar')
      .then((res) => res.json())
      .then((data) => setMetodosPago(data))
      .catch(() => toast.error('Error al cargar métodos de pago'));
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === 'numero_cuenta' && !/^\d*$/.test(value)) return;

    setForm({ ...form, [name]: value });
  };

  const handleSubmit = async () => {
    const {
      nombre_beneficiario,
      entidad_financiera,
      numero_cuenta,
      tipo_cuenta,
      id_metodo_pago,
    } = form;

    if (!nombre_beneficiario || !entidad_financiera || !numero_cuenta || !tipo_cuenta || !id_metodo_pago) {
      toast.error('Todos los campos marcados con * son obligatorios.');
      return;
    }
    console.log("Datos enviados al backend:", form);

    try {
      const response = await fetch('http://localhost:5008/informacion_metodos_pago/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...form,
          id_metodo_pago: parseInt(form.id_metodo_pago), 
          estado: form.estado === 'activo' || form.estado === true,
        }),
      });

      if (response.ok) {
        toast.success('✅ Información de pago guardada correctamente');
        onSuccess();
        onClose();
      } else {
        const error = await response.json();
        toast.error(`Error: ${error.message || 'No se pudo guardar'}`);
      }
    } catch (err) {
      toast.error('🚫 Error al enviar la información');
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 bg-opacity-30">
      <div className="bg-white rounded-xl shadow-lg w-full max-w-4xl mx-4">
        {/* Header */}
        <div className="flex justify-between items-center px-6 py-4 border-b">
          <h2 className="text-green-700 text-xl font-bold flex items-center gap-2">
            <i className="fas fa-university text-green-700"></i> Agregar Información de Pago
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-red-600 text-xl">&times;</button>
        </div>

        {/* Formulario */}
        <div className="px-6 py-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium text-gray-700">Nombre del Beneficiario *</label>
            <input name="nombre_beneficiario" value={form.nombre_beneficiario} onChange={handleChange}
              className="w-full mt-1 px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500" />
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700">Entidad Financiera *</label>
            <input name="entidad_financiera" value={form.entidad_financiera} onChange={handleChange}
              className="w-full mt-1 px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500" />
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700">Número de Cuenta *</label>
            <input
              type="number"
              name="numero_cuenta"
              value={form.numero_cuenta}
              onChange={handleChange}
              className="w-full mt-1 px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500"
            />
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700">Tipo de Cuenta *</label>
            <select name="tipo_cuenta" value={form.tipo_cuenta} onChange={handleChange}
              className="w-full mt-1 px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500">
              <option value="">-- Seleccionar --</option>
              <option value="ahorros">Ahorros</option>
              <option value="corriente">Corriente</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700">Método de Pago *</label>
            <select name="id_metodo_pago" value={form.id_metodo_pago} onChange={handleChange}
              className="w-full mt-1 px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500">
              <option value="">-- Seleccionar método --</option>
              {metodosPago.map((m) => (
                <option key={m.id_metodo_pago} value={m.id_metodo_pago}>{m.nombre}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm font-medium text-gray-700">Estado</label>
            <select name="estado" value={form.estado ? 'activo' : 'inactivo'} onChange={(e) =>
              setForm({ ...form, estado: e.target.value === 'activo' })}
              className="w-full mt-1 px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500">
              <option value="activo">Activo</option>
              <option value="inactivo">Inactivo</option>
            </select>
          </div>

          <div className="md:col-span-2">
            <label className="text-sm font-medium text-gray-700">Instrucciones (opcional)</label>
            <textarea name="instrucciones" rows={3} value={form.instrucciones} onChange={handleChange}
              className="w-full mt-1 px-4 py-2 border rounded-md focus:ring-2 focus:ring-green-500" />
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t flex justify-end gap-4">
          <button onClick={onClose}
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium px-5 py-2 rounded-md">
            Cancelar
          </button>
          <button onClick={handleSubmit}
            className="bg-green-600 hover:bg-green-700 text-white font-medium px-6 py-2 rounded-md shadow-md">
            Guardar Información
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalAgregarInfoPago;
