import React, { useEffect, useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { toast } from 'react-toastify';

const ModalEditarPlan = ({ visible, onClose, onSuccess, plan }) => {
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [formData, setFormData] = useState({});
  const [pools, setPools] = useState([]);
  const [vlanNombre, setVlanNombre] = useState('');

  useEffect(() => {
    if (!plan) return;
    setFormData({
      precio: plan.precio || '',
      velocidad_subida: plan.velocidad_subida || '',
      velocidad_bajada: plan.velocidad_bajada || '',
      ip_local: plan.ip_local || '',
      dns: plan.dns || '',
      ip_pool_remoto: plan.ip_remota || '',
      rafaga_subida: plan.rafaga_subida || '',
      rafaga_bajada: plan.rafaga_bajada || '',
      max_subida: plan.max_subida || '',
      max_bajada: plan.max_bajada || '',
      tiempo_rafaga_subida: plan.tiempo_rafaga_subida || '',
      tiempo_rafaga_bajada: plan.tiempo_rafaga_bajada || ''
    });
  }, [plan]);

  useEffect(() => {
    const fetchPools = async () => {
      try {
        const res = await fetch('http://localhost:5004/pools');
        const data = await res.json();
        setPools(data);
      } catch (error) {
        toast.error('Error al cargar los pools');
      }
    };

    const fetchVlan = async () => {
      try {
        const res = await fetch(`http://localhost:5004/api/vlans/todas`);
        const data = await res.json();
        const vlan = data.find(v => v.id_vlan === plan.id_vlan);
        if (vlan) setVlanNombre(vlan.nombre);
      } catch (error) {
        toast.error('Error al cargar la VLAN');
      }
    };

    if (visible) {
      fetchPools();
      fetchVlan();
    }
  }, [visible, plan]);

  const handleChange = (e) => {
  const { name, value, type } = e.target;
  // Convertir a número si es campo numérico
  const numericFields = [
    'precio', 'velocidad_subida', 'velocidad_bajada',
    'rafaga_subida', 'rafaga_bajada', 'max_subida',
    'max_bajada', 'tiempo_rafaga_subida', 'tiempo_rafaga_bajada'
  ];

  const newValue = numericFields.includes(name) && value !== ''
    ? Number(value)
    : value;

  setFormData(prev => ({ ...prev, [name]: newValue }));
};


  const handleSubmit = async () => {
  const payload = {};
  for (const key in formData) {
    if (
      formData[key] !== '' &&
      formData[key] !== null &&
      formData[key] !== undefined &&
      formData[key] !== plan[key]
    ) {
      payload[key] = formData[key];
    }
  }

  // Validación rápida: evitar valores inválidos
  if (payload.velocidad_subida && (!Number.isInteger(payload.velocidad_subida) || payload.velocidad_subida <= 0)) {
    return toast.error("La velocidad de subida debe ser un entero positivo.");
  }

  if (formData.ip_pool_remoto === '' || formData.ip_pool_remoto === 'Seleccionar IP Pool') {
    return toast.error("Debe seleccionar un IP Pool Remoto válido.");
  }

  console.log("Datos a actualizar:", payload);

  try {
    const res = await fetch(`http://localhost:5005/planes/actualizar/${plan.id_plan}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    const data = await res.json();
    if (res.ok) {
      toast.success('Plan actualizado');
      onSuccess();
      onClose();
    } else {
      toast.error(data.message || 'Error al actualizar');
    }
  } catch (err) {
    toast.error('Error del servidor');
  }
};


  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4 overflow-y-auto">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl border-t-4 border-green-600 max-h-[90vh] flex flex-col">
        <h2 className="text-2xl font-bold text-center text-green-700 py-4 border-b">Editar Plan</h2>

        <div className="overflow-y-auto px-8 pt-4 pb-2" style={{ maxHeight: 'calc(90vh - 140px)' }}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Nombre del plan</label>
              <input value={plan.nombre_plan || ''} readOnly className="w-full border rounded-md px-3 py-2 bg-gray-100" />
            </div>
            <div>
              <label className="text-sm font-medium">Precio ($)</label>
              <input name="precio" value={formData.precio || ''} onChange={handleChange} className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">Velocidad subida (Mbps)</label>
              <input name="velocidad_subida" value={formData.velocidad_subida || ''} onChange={handleChange} className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">Velocidad bajada (Mbps)</label>
              <input name="velocidad_bajada" value={formData.velocidad_bajada || ''} onChange={handleChange} className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">IP local</label>
              <input name="ip_local" value={formData.ip_local || ''} onChange={handleChange} className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">DNS</label>
              <input name="dns" value={formData.dns || ''} onChange={handleChange} className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">IP Pool Remoto</label>
              <select name="ip_pool_remoto" value={formData.ip_pool_remoto || ''} onChange={handleChange} className="w-full border rounded-md px-3 py-2">
                <option value="">Seleccionar IP Pool</option>
                {pools.map(pool => (
                  <option key={pool.id_pool} value={pool.nombre}>{pool.nombre}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">VLAN</label>
              <input value={vlanNombre} readOnly className="w-full border rounded-md px-3 py-2 bg-gray-100" />
            </div>
          </div>

          <div className="mt-4">
            <button className="flex items-center text-green-600 font-semibold" onClick={() => setShowAdvanced(!showAdvanced)}>
              {showAdvanced ? <ChevronUp className="mr-1" /> : <ChevronDown className="mr-1" />}
              {showAdvanced ? 'Ocultar' : 'Mostrar'} Opciones Avanzadas
            </button>

            {showAdvanced && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                {[
                  { name: 'rafaga_subida', label: 'Ráfaga subida' },
                  { name: 'rafaga_bajada', label: 'Ráfaga bajada' },
                  { name: 'max_subida', label: 'Máximo subida' },
                  { name: 'max_bajada', label: 'Máximo bajada' },
                  { name: 'tiempo_rafaga_subida', label: 'Tiempo ráfaga subida' },
                  { name: 'tiempo_rafaga_bajada', label: 'Tiempo ráfaga bajada' }
                ].map(field => (
                  <div key={field.name}>
                    <label className="text-sm font-medium">{field.label}</label>
                    <input
                      type="number"
                      name={field.name}
                      value={formData[field.name] || ''}
                      onChange={handleChange}
                      className="w-full border rounded-md px-3 py-2"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-4 px-8 pb-6 pt-2 border-t">
          <button onClick={onClose} className="bg-gray-200 text-gray-800 px-5 py-2 rounded-md">Cancelar</button>
          <button onClick={handleSubmit} className="bg-green-600 text-white px-5 py-2 rounded-md hover:bg-green-700">Actualizar</button>
        </div>
      </div>
    </div>
  );
};

export default ModalEditarPlan;
