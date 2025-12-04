import React, { useEffect, useState } from "react";
import { Pencil, Trash } from "lucide-react";
import ModalAgregarIpPool from "./ModalAgregarIpPool";

const TablaIpPools = () => {
  const [pools, setPools] = useState([]);
  const [filtro, setFiltro] = useState("");
  const [visibleModal, setVisibleModal] = useState(false);
  const [pagina, setPagina] = useState(1);
  const [porPagina] = useState(5);

  const obtenerPools = async () => {
    try {
      const res = await fetch("http://localhost:5004/pools");
      const data = await res.json();
      setPools(data);
    } catch (error) {
      console.error("Error al cargar IP Pools:", error);
    }
  };

  useEffect(() => {
    obtenerPools();
  }, []);

  const poolsFiltrados = pools.filter((p) =>
    p.nombre.toLowerCase().includes(filtro.toLowerCase())
  );

  const totalPaginas = Math.ceil(poolsFiltrados.length / porPagina);
  const inicio = (pagina - 1) * porPagina;
  const poolsPaginados = poolsFiltrados.slice(inicio, inicio + porPagina);

  return (
    <div className="p-6 bg-gradient-to-br from-white via-gray-50 to-gray-100 shadow-md rounded-2xl border border-gray-200">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-semibold text-gray-800">Gestión de IP Pools</h2>
        <button
          onClick={() => setVisibleModal(true)}
          className="bg-emerald-600 text-white px-5 py-2 rounded-md hover:bg-emerald-700 shadow-md transition"
        >
          + Nuevo IP Pool
        </button>
      </div>

      <div className="mb-5">
        <input
          type="text"
          placeholder="Buscar por nombre..."
          value={filtro}
          onChange={(e) => {
            setFiltro(e.target.value);
            setPagina(1);
          }}
          className="border border-gray-300 px-4 py-2 rounded-md w-full md:w-1/3 focus:outline-none focus:ring-2 focus:ring-emerald-400"
        />
      </div>

      <div className="overflow-x-auto rounded-xl border border-gray-100 bg-white">
        <table className="min-w-full text-sm text-gray-800">
          <thead className="bg-emerald-100 text-emerald-800">
            <tr>
              <th className="text-left px-5 py-3">NOMBRE</th>
              <th className="text-left px-5 py-3">RANGO</th>
              <th className="text-left px-5 py-3">GATEWAY</th>
              <th className="text-left px-5 py-3">DNS</th>
              <th className="text-center px-5 py-3">ACCIONES</th>
            </tr>
          </thead>
          <tbody>
            {poolsPaginados.map((pool) => (
              <tr key={pool.id_pool} className="border-b hover:bg-emerald-50">
                <td className="px-5 py-4 font-semibold text-emerald-700">{pool.nombre}</td>
                <td className="px-5 py-4">{pool.rango_inicio} - {pool.rango_fin}</td>
                <td className="px-5 py-4">{pool.gateway}</td>
                <td className="px-5 py-4">{pool.dns_servidor}</td>
                <td className="px-5 py-4 text-center space-x-2">
                  <button className="text-emerald-600 hover:text-emerald-800">
                    <Pencil size={18} />
                  </button>
                  <button className="text-red-500 hover:text-red-700">
                    <Trash size={18} />
                  </button>
                </td>
              </tr>
            ))}
            {poolsPaginados.length === 0 && (
              <tr>
                <td colSpan="5" className="text-center py-6 text-gray-400">
                  No se encontraron resultados.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {totalPaginas > 1 && (
        <div className="flex justify-center mt-6 space-x-2">
          {Array.from({ length: totalPaginas }, (_, i) => (
            <button
              key={i}
              onClick={() => setPagina(i + 1)}
              className={`px-3 py-1 rounded-md border text-sm transition font-medium ${
                pagina === i + 1
                  ? "bg-emerald-600 text-white border-emerald-600"
                  : "bg-white text-emerald-700 border-emerald-300 hover:bg-emerald-100"
              }`}
            >
              {i + 1}
            </button>
          ))}
        </div>
      )}

      <ModalAgregarIpPool
        visible={visibleModal}
        onClose={() => setVisibleModal(false)}
        onSuccess={obtenerPools}
      />
    </div>
  );
};

export default TablaIpPools;