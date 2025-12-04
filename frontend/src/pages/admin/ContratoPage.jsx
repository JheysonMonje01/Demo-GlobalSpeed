import React, { useEffect, useState } from "react";
import { Save, FilePlus } from "lucide-react";
import { BsFillCloudDownloadFill } from "react-icons/bs";
import { toast } from "react-toastify";

const ContratosPage = () => {
  const [contratos, setContratos] = useState([]);
  const [clientesCache, setClientesCache] = useState({});
  const [planesCache, setPlanesCache] = useState({});
  const [filtroNombre, setFiltroNombre] = useState("");
  const [filtroPlan, setFiltroPlan] = useState("");
  const [pagina, setPagina] = useState(1);
  const contratosPorPagina = 7;

  useEffect(() => {
    cargarContratos();
  }, []);

  const cargarContratos = async () => {
    try {
      const res = await fetch("http://localhost:5006/contratos");
      const data = await res.json();

      // Ordenar por id descendente (más reciente primero)
      const ordenados = [...data].sort((a, b) => b.id_contrato - a.id_contrato);
      setContratos(ordenados);

      for (const contrato of ordenados) {
        if (!clientesCache[contrato.id_cliente]) {
          const resCliente = await fetch(`http://localhost:5001/clientes/${contrato.id_cliente}`);
          const clienteData = await resCliente.json();
          setClientesCache((prev) => ({ ...prev, [contrato.id_cliente]: clienteData }));
        }

        if (!planesCache[contrato.id_plan]) {
          const resPlan = await fetch(`http://localhost:5005/planes/${contrato.id_plan}`);
          const planData = await resPlan.json();
          setPlanesCache((prev) => ({ ...prev, [contrato.id_plan]: planData }));
        }
      }
    } catch (error) {
      toast.error("❌ Error al cargar contratos.");
    }
  };

  const handleReemplazarPDF = (id_contrato) => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = "application/pdf";
    input.onchange = async (e) => {
      const archivo = e.target.files[0];
      if (!archivo) return;

      const formData = new FormData();
      formData.append("archivo", archivo);

      try {
        const res = await fetch(`http://localhost:5006/contratos/${id_contrato}/reemplazar-pdf`, {
          method: "PUT",
          body: formData,
        });

        const data = await res.json();
        if (res.ok) {
          toast.success("✅ Contrato PDF actualizado");
          cargarContratos(); // recargar lista
        } else {
          toast.error(`❌ Error: ${data.message}`);
        }
      } catch (err) {
        toast.error("❌ Error al subir el nuevo PDF");
      }
    };
    input.click();
  };

  const contratosFiltrados = contratos.filter((contrato) => {
    const cliente = clientesCache[contrato.id_cliente];
    const plan = planesCache[contrato.id_plan];
    const nombreCompleto = cliente
      ? `${cliente.persona?.nombre} ${cliente.persona?.apellido}`.toLowerCase()
      : "";
    const nombreIncluye = nombreCompleto.includes(filtroNombre.toLowerCase());
    const planCoincide = filtroPlan ? plan?.nombre_plan === filtroPlan : true;
    return nombreIncluye && planCoincide;
  });

  const totalPaginas = Math.ceil(contratosFiltrados.length / contratosPorPagina);
  const contratosMostrados = contratosFiltrados.slice(
    (pagina - 1) * contratosPorPagina,
    pagina * contratosPorPagina
  );

  const cambiarPagina = (nueva) => {
    if (nueva >= 1 && nueva <= totalPaginas) setPagina(nueva);
  };

  const planesUnicos = Array.from(
    new Set(
      Object.values(planesCache)
        .filter((p) => p?.nombre_plan)
        .map((p) => p.nombre_plan)
    )
  );

  return (
    <div className="p-6">
      <div className="bg-white/80 backdrop-blur-md border-t-8 border-green-700 rounded-3xl shadow-xl px-8 py-6 max-w-7xl mx-auto">
        <h1 className="text-4xl font-extrabold text-green-800 mb-6 flex items-center gap-3">
          📑 Gestión de Contratos
        </h1>

        {/* Filtros */}
        <div className="flex flex-col md:flex-row gap-4 mb-6">
          <input
            type="text"
            placeholder="🔍 Buscar por cliente..."
            value={filtroNombre}
            onChange={(e) => {
              setFiltroNombre(e.target.value);
              setPagina(1);
            }}
            className="border px-4 py-2 rounded-lg shadow-sm w-full md:w-1/2 focus:outline-none focus:ring-2 focus:ring-green-500"
          />
          <select
            value={filtroPlan}
            onChange={(e) => {
              setFiltroPlan(e.target.value);
              setPagina(1);
            }}
            className="border px-4 py-2 rounded-lg shadow-sm w-full md:w-1/2 focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            <option value="">Filtrar por plan</option>
            {planesUnicos.map((plan) => (
              <option key={plan} value={plan}>
                {plan}
              </option>
            ))}
          </select>
        </div>

        {/* Tabla */}
        <div className="overflow-x-auto rounded-xl border shadow-sm">
          <table className="w-full text-sm text-left border-collapse">
            <thead className="bg-green-600 text-white text-base">
              <tr>
                <th className="px-4 py-3">Cliente</th>
                <th className="px-4 py-3">Plan</th>
                <th className="px-4 py-3">Precio</th>
                <th className="px-4 py-3">Ubicación</th>
                <th className="px-4 py-3">Fin Contrato</th>
                <th className="px-4 py-3 text-center">Acciones</th>
              </tr>
            </thead>
            <tbody>
              {contratosMostrados.map((contrato) => {
                const cliente = clientesCache[contrato.id_cliente];
                const plan = planesCache[contrato.id_plan];
                return (
                  <tr key={contrato.id_contrato} className="border-b hover:bg-gray-50">
                    <td className="px-4 py-3">
                      {cliente
                        ? `${cliente.persona?.nombre} ${cliente.persona?.apellido}`
                        : "Cargando..."}
                    </td>
                    <td className="px-4 py-3">{plan?.nombre_plan || "-"}</td>
                    <td className="px-4 py-3">${Number(plan?.precio).toFixed(2) || "-"}</td>
                    <td className="px-4 py-3">{contrato.ubicacion}</td>
                    <td className="px-4 py-3">{contrato.fecha_fin_contrato?.slice(0, 10)}</td>
                    <td className="px-4 py-3 flex justify-center gap-4">
                      {/* Descargar */}
                      <a
                        href={contrato.url_archivo}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-green-600 hover:text-green-800 transition-transform hover:scale-110"
                        title="Descargar contrato PDF"
                      >
                        <BsFillCloudDownloadFill className="w-6 h-6" />
                      </a>

                      {/* Reemplazar PDF */}
                      <button
                        onClick={() => handleReemplazarPDF(contrato.id_contrato)}
                        className="text-blue-600 hover:text-blue-800 transition-transform hover:scale-110"
                        title="Reemplazar contrato PDF"
                      >
                        <FilePlus className="w-6 h-6" />
                      </button>
                    </td>
                  </tr>
                );
              })}
              {contratosMostrados.length === 0 && (
                <tr>
                  <td colSpan="6" className="text-center py-6 text-gray-500 italic">
                    No se encontraron contratos.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Paginación */}
        <div className="mt-8 flex justify-center items-center gap-4">
          <button
            onClick={() => cambiarPagina(pagina - 1)}
            disabled={pagina <= 1}
            className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-lg shadow-sm disabled:opacity-40"
          >
            ⬅️
          </button>
          <span className="font-semibold text-gray-700">
            Página {pagina} de {totalPaginas || 1}
          </span>
          <button
            onClick={() => cambiarPagina(pagina + 1)}
            disabled={pagina >= totalPaginas}
            className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-lg shadow-sm disabled:opacity-40"
          >
            ➡️
          </button>
        </div>
      </div>
    </div>
  );
};

export default ContratosPage;
