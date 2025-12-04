// ModalActivarServicio.jsx
import React, { useState } from 'react';
import { toast } from 'react-toastify';
import Swal from 'sweetalert2';

const ModalActivarServicio = ({ contratoId, onClose, onSuccess }) => {
  const [modo, setModo] = useState('automatico');
  const [form, setForm] = useState({ usuario_pppoe: '', contrasena: '' });
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const mostrarComandosSwal = (comandos) => {
  if (!Array.isArray(comandos)) return;

  let lista = '';

  comandos.forEach((grupo) => {
    if (grupo.comando_olt_huawei) {
      grupo.comando_olt_huawei.forEach((linea) => {
        lista += `<div>${linea}</div>`;
      });
    } else if (typeof grupo === 'string') {
      lista += `<div>${grupo}</div>`;
    }
  });

  Swal.fire({
    title: '📶 Comandos enviados a la OLT',
    html: `
      <div style="text-align: left; max-height: 300px; overflow-y: auto; background-color: #f4f4f4; border: 1px solid #ccc; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 0.9rem;">
        ${lista}
      </div>
    `,
    icon: 'info',
    confirmButtonColor: '#4CAF50',
    confirmButtonText: 'Entendido',
    width: 700
  });
};


  const activarServicio = async () => {
    try {
      setLoading(true);
      const id_usuario = localStorage.getItem('id_usuario');
      const url = modo === 'manual'
        ? 'http://localhost:5007/pppoe/crear'
        : 'http://localhost:5007/pppoe/crear-automatico';

       const payload = modo === 'manual'
      ? { ...form, id_contrato: contratoId, id_usuario: parseInt(id_usuario) }
      : { id_contrato: contratoId, id_usuario: parseInt(id_usuario) };

       console.log("📤 Payload enviado al backend:", payload); // 🟢 Aquí se imprime
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
       if (res.ok) {
        toast.success('✅ Servicio activado correctamente');
        if (data.comando_huawei || data.comando_olt_huawei) {
          mostrarComandosSwal(data.comando_huawei || data.comando_olt_huawei);
        }
        onSuccess();
      } else {
        toast.error(`❌ Error: ${data.message}`);
      }
    } catch (error) {
      toast.error('❌ Error al activar servicio');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6">
        <h2 className="text-2xl font-bold mb-4 text-center text-green-700">Activar Servicio PPPoE</h2>

        <div className="flex justify-center gap-4 mb-4">
          <button
            onClick={() => setModo('automatico')}
            className={`px-4 py-2 rounded-lg ${modo === 'automatico' ? 'bg-green-600 text-white' : 'bg-gray-200'}`}
          >Automático</button>
          <button
            onClick={() => setModo('manual')}
            className={`px-4 py-2 rounded-lg ${modo === 'manual' ? 'bg-green-600 text-white' : 'bg-gray-200'}`}
          >Manual</button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="font-semibold">ID Contrato:</label>
            <input
              type="text"
              value={contratoId}
              disabled
              className="w-full mt-1 px-3 py-2 border rounded-md bg-gray-100"
            />
          </div>

          {modo === 'manual' && (
            <>
              <div>
                <label className="font-semibold">Usuario PPPoE</label>
                <input
                  type="text"
                  name="usuario_pppoe"
                  value={form.usuario_pppoe}
                  onChange={handleChange}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                />
              </div>
              <div>
                <label className="font-semibold">Contraseña</label>
                <input
                  type="password"
                  name="contrasena"
                  value={form.contrasena}
                  onChange={handleChange}
                  className="w-full mt-1 px-3 py-2 border rounded-md"
                />
              </div>
            </>
          )}

          <div className="flex justify-end gap-2 mt-6">
            <button onClick={onClose} className="px-4 py-2 bg-gray-400 text-white rounded-md">Cancelar</button>
            <button
              onClick={activarServicio}
              disabled={loading}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
              {loading ? 'Activando...' : 'Activar Servicio'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ModalActivarServicio;
