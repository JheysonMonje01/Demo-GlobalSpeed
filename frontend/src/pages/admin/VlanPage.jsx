import React, { useEffect, useState } from 'react';
import { toast } from 'react-toastify';
import { PlusCircle, Pencil, Trash2, Network } from 'lucide-react';
import ModalCrearVlan from '../../components/ModalCrearVlan';

const VlanPage = () => {
  const [vlans, setVlans] = useState([]);
  const [mikrotikCache, setMikrotikCache] = useState({});
  const [mostrarModal, setMostrarModal] = useState(false);
  const [filtro, setFiltro] = useState("");

  useEffect(() => {
    cargarVlans();
  }, []);

  const cargarVlans = async () => {
    try {
      const res = await fetch('http://localhost:5004/api/vlans/todas');
      const data = await res.json();

      if (res.ok) {
        const datosConRouters = await Promise.all(
          data.map(async (vlan) => {
            if (!vlan.id_mikrotik) return { ...vlan, router_info: "N/A" };

            if (mikrotikCache[vlan.id_mikrotik]) {
              return {
                ...vlan,
                router_info: mikrotikCache[vlan.id_mikrotik]
              };
            }

            try {
              const r = await fetch(`http://localhost:5002/mikrotik/configuraciones/${vlan.id_mikrotik}`);
              const json = await r.json();

              if (r.ok) {
                const info = `${json.nombre} (${json.host})`;
                setMikrotikCache(prev => ({ ...prev, [vlan.id_mikrotik]: info }));
                return { ...vlan, router_info: info };
              } else {
                return { ...vlan, router_info: "No encontrado" };
              }
            } catch {
              return { ...vlan, router_info: "Error conexión" };
            }
          })
        );

        setVlans(datosConRouters);
      } else {
        toast.error("No se pudieron obtener las VLANs");
      }
    } catch (err) {
      toast.error("Error al conectar con el backend");
      console.error(err);
    }
  };

  const vlansFiltradas = vlans.filter((v) => {
    const f = filtro.toLowerCase();
    return (
      v.numero_vlan.toString().includes(f) ||
      v.nombre?.toLowerCase().includes(f) ||
      v.interface_destino?.toLowerCase().includes(f) ||
      v.router_info?.toLowerCase().includes(f)
    );
  });

  return (
    <div className="p-6 bg-white rounded-xl shadow-xl text-sm">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-semibold text-green-800 flex items-center gap-2">
          <Network size={22} /> Lista de VLANs
        </h2>
        <button
          onClick={() => setMostrarModal(true)}
          className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded shadow"
        >
          <PlusCircle size={18} /> Añadir VLAN
        </button>
      </div>

      <div className="flex justify-end mb-4">
        <input
          type="text"
          placeholder="Buscar VLAN..."
          value={filtro}
          onChange={(e) => setFiltro(e.target.value)}
          className="border px-4 py-2 rounded-md bg-green-50 focus:outline-none focus:ring-2 focus:ring-green-400 w-full max-w-xs"
        />
      </div>

      <div className="overflow-x-auto border rounded-lg">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-green-100 text-green-800">
            <tr>
              <th className="py-2 px-4">#</th>
              <th className="py-2 px-4">Número</th>
              <th className="py-2 px-4">Nombre</th>
              <th className="py-2 px-4">Interfaz</th>
              <th className="py-2 px-4">MikroTik</th>
              <th className="py-2 px-4 text-center">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {vlansFiltradas.map((vlan, index) => (
              <tr key={vlan.id_vlan} className="hover:bg-green-50 border-t">
                <td className="py-2 px-4">{index + 1}</td>
                <td className="py-2 px-4">{vlan.numero_vlan}</td>
                <td className="py-2 px-4">{vlan.nombre || '-'}</td>
                <td className="py-2 px-4">{vlan.interface_destino}</td>
                <td className="py-2 px-4">{vlan.router_info || '...'}</td>
                <td className="py-2 px-4 text-center">
                  <div className="flex justify-center gap-2">
                    <button className="text-blue-600 hover:text-blue-800">
                      <Pencil size={18} />
                    </button>
                    <button className="text-red-600 hover:text-red-800">
                      <Trash2 size={18} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {vlansFiltradas.length === 0 && (
              <tr>
                <td colSpan="6" className="py-4 px-4 text-center text-gray-500">
                  No se encontraron VLANs.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <ModalCrearVlan
        visible={mostrarModal}
        onClose={() => setMostrarModal(false)}
        onSuccess={() => {
          setMostrarModal(false);
          cargarVlans();
        }}
      />
    </div>
  );
};

export default VlanPage;