import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { ChevronDown, ChevronUp } from 'lucide-react';

const ModalAgregarPlan = ({ visible, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    nombre_plan: '',
    velocidad_subida: '',
    velocidad_bajada: '',
    ip_local: '',
    dns: '',
    precio: '',
    id_pool_remoto: '',
    id_vlan: '',
    rafaga_subida: '',
    rafaga_bajada: '',
    max_subida: '',
    max_bajada: '',
    tiempo_rafaga_subida: '',
    tiempo_rafaga_bajada: ''
  });

  const [pools, setPools] = useState([]);
  const [vlans, setVlans] = useState([]);
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    fetch('http://localhost:5004/pools')
      .then(res => res.json()).then(data => setPools(data));
    fetch('http://localhost:5004/api/vlans/todas')
      .then(res => res.json()).then(data => setVlans(data));
  }, []);

  const validateIP = ip => /^(\d{1,3}\.){3}\d{1,3}$/.test(ip);
  const isPositiveNumber = val => !isNaN(val) && Number(val) >= 0;
  const validateForm = () => {
    const { nombre_plan, velocidad_subida, velocidad_bajada, ip_local, dns, precio, id_pool_remoto, id_vlan } = formData;
    if (!nombre_plan || !velocidad_subida || !velocidad_bajada || !ip_local || !dns || !precio || !id_pool_remoto || !id_vlan) {
      toast.error("Todos los campos obligatorios deben completarse.");
      return false;
    }
    const subida = parseInt(velocidad_subida, 10);
const bajada = parseInt(velocidad_bajada, 10);
const precioNum = parseFloat(precio);

if (!Number.isInteger(subida) || subida <= 0) {
  toast.error("La velocidad de subida debe ser un número entero mayor a 0.");
  return false;
}
if (!Number.isInteger(bajada) || bajada <= 0) {
  toast.error("La velocidad de bajada debe ser un número entero mayor a 0.");
  return false;
}
if (isNaN(precioNum) || precioNum < 0) {
  toast.error("El precio debe ser un número positivo.");
  return false;
}

    if (!validateIP(ip_local) || !validateIP(dns)) {
      toast.error("La IP local y el DNS deben tener un formato válido.");
      return false;
    }
    return true;
  };

  const handleChange = e => {
    let { name, value } = e.target;
    if (name === "nombre_plan") value = value.toUpperCase();
    if (name === "precio") value = value.replace(/[^0-9.]/g, '').slice(0, 8);
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async () => {
  if (!validateForm()) return;

  const payload = {
    ...formData,
    nombre_plan: formData.nombre_plan.toUpperCase(),
    precio: parseFloat(formData.precio), // ✅ número válido
    velocidad_subida: parseInt(formData.velocidad_subida),
    velocidad_bajada: parseInt(formData.velocidad_bajada),
    max_subida: formData.max_subida ? parseInt(formData.max_subida) : null,
    max_bajada: formData.max_bajada ? parseInt(formData.max_bajada) : null,
    rafaga_subida: formData.rafaga_subida ? parseInt(formData.rafaga_subida) : null,
    rafaga_bajada: formData.rafaga_bajada ? parseInt(formData.rafaga_bajada) : null,
    tiempo_rafaga_subida: formData.tiempo_rafaga_subida ? parseInt(formData.tiempo_rafaga_subida) : null,
    tiempo_rafaga_bajada: formData.tiempo_rafaga_bajada ? parseInt(formData.tiempo_rafaga_bajada) : null,
  };

  console.log("Datos enviados al backend:", payload);

  try {
    const response = await fetch("http://localhost:5005/planes/crear_plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (response.ok) {
      toast.success("Plan creado exitosamente");
      onSuccess();
      onClose();
    } else {
      toast.error(data.message || "Error al registrar el plan");
    }
  } catch (err) {
    toast.error("Error en la conexión");
    console.error("Error al conectar:", err);
  }
};


  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl border-t-4 border-green-600 max-h-[90vh] flex flex-col">
        
        <h2 className="text-2xl font-bold text-center text-green-700 py-4 border-b">Registrar Nuevo Plan</h2>
        
        {/* Contenido desplazable */}
        <div className="overflow-y-auto px-8 py-4" style={{ maxHeight: 'calc(90vh - 120px)' }}>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium">Nombre del plan</label>
              <input type="text" name="nombre_plan" value={formData.nombre_plan} onChange={handleChange}
                className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">Precio ($)</label>
              <input type="number" name="precio" value={formData.precio} onChange={handleChange} min="0" step="0.01"
                className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">Velocidad subida (Mbps)</label>
              <input type="number" name="velocidad_subida" value={formData.velocidad_subida} onChange={handleChange}
                className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">Velocidad bajada (Mbps)</label>
              <input type="number" name="velocidad_bajada" value={formData.velocidad_bajada} onChange={handleChange}
                className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">IP local</label>
              <input type="text" name="ip_local" value={formData.ip_local} onChange={handleChange}
                className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">DNS</label>
              <input type="text" name="dns" value={formData.dns} onChange={handleChange}
                className="w-full border rounded-md px-3 py-2" />
            </div>
            <div>
              <label className="text-sm font-medium">IP Pool Remoto</label>
              <select name="id_pool_remoto" value={formData.id_pool_remoto} onChange={handleChange}
                className="w-full border rounded-md px-3 py-2">
                <option value="">Seleccionar IP Pool Remoto</option>
                {pools.map(pool => <option key={pool.id_pool} value={pool.id_pool}>{pool.nombre}</option>)}
              </select>
            </div>
            <div>
              <label className="text-sm font-medium">VLAN</label>
              <select name="id_vlan" value={formData.id_vlan} onChange={handleChange}
                className="w-full border rounded-md px-3 py-2">
                <option value="">Seleccionar VLAN</option>
                {vlans.map(vlan => <option key={vlan.id_vlan} value={vlan.id_vlan}>{vlan.nombre}</option>)}
              </select>
            </div>
          </div>

          <div className="mt-6">
            <button className="flex items-center text-green-600 font-semibold"
              onClick={() => setShowAdvanced(!showAdvanced)}>
              {showAdvanced ? <ChevronUp className="mr-1" /> : <ChevronDown className="mr-1" />}
              {showAdvanced ? 'Ocultar' : 'Mostrar'} Opciones Avanzadas
            </button>

            {showAdvanced && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
                {[
                  { name: 'rafaga_subida', label: 'Ráfaga subida (opcional)' },
                  { name: 'rafaga_bajada', label: 'Ráfaga bajada (opcional)' },
                  { name: 'max_subida', label: 'Máximo subida (opcional)' },
                  { name: 'max_bajada', label: 'Máximo bajada (opcional)' },
                  { name: 'tiempo_rafaga_subida', label: 'Tiempo ráfaga subida (opcional)' },
                  { name: 'tiempo_rafaga_bajada', label: 'Tiempo ráfaga bajada (opcional)' }
                ].map(field => (
                  <div key={field.name}>
                    <label className="text-sm font-medium">{field.label}</label>
                    <input type="number" name={field.name} value={formData[field.name]} onChange={handleChange}
                      className="w-full border rounded-md px-3 py-2" />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end gap-4 px-8 py-4 border-t">
          <button onClick={onClose} className="bg-gray-200 text-gray-800 px-5 py-2 rounded-md">Cancelar</button>
          <button onClick={handleSubmit} className="bg-green-600 text-white px-5 py-2 rounded-md hover:bg-green-700">Registrar</button>
        </div>
      </div>
    </div>
  );
};

export default ModalAgregarPlan;
