import React, { useEffect, useState } from "react";
import { FaDownload, FaCheck, FaFileUpload } from "react-icons/fa";
import { format } from "date-fns";
import Swal from "sweetalert2";

const OrdenesAsignadasTecnico = () => {
  const [ordenes, setOrdenes] = useState([]);
  const [clientes, setClientes] = useState({});
  const [filtroCliente, setFiltroCliente] = useState("");
  const [filtroEstado, setFiltroEstado] = useState("");
  const [filtroFechaInicio, setFiltroFechaInicio] = useState("");
  const [filtroFechaFin, setFiltroFechaFin] = useState("");
  const [pagina, setPagina] = useState(1);
  const [ordenesFiltradas, setOrdenesFiltradas] = useState([]);
  const ordenesPorPagina = 5;

  useEffect(() => {
    const fetchOrdenes = async () => {
      try {
        const usuario = localStorage.getItem("id_usuario");
        const resTecnico = await fetch(`http://localhost:5001/tecnicos/persona/${usuario}`);
        const tecnicoData = await resTecnico.json();
        const idTecnico = tecnicoData.id_tecnico;

        const resOrdenes = await fetch(`http://localhost:5010/ordenes_instalacion/por-tecnico/${idTecnico}`);
        const dataOrdenes = await resOrdenes.json();
        setOrdenes(dataOrdenes);
        setOrdenesFiltradas(dataOrdenes);
        cargarClientes(dataOrdenes);
      } catch (error) {
        console.error("Error al cargar órdenes:", error);
      }
    };
    fetchOrdenes();
  }, []);

  const cargarClientes = async (ordenesData) => {
    try {
      const clientePromises = ordenesData.map(async (orden) => {
        const contratoRes = await fetch(`http://localhost:5006/contratos/${orden.id_contrato}`);
        const contrato = await contratoRes.json();
        const idCliente = contrato?.id_cliente;
        if (!idCliente) return null;

        const clienteRes = await fetch(`http://localhost:5001/clientes/${idCliente}`);
        const clienteData = await clienteRes.json();
        const idPersona = clienteData?.id_persona;
        if (!idPersona) return null;

        const personaRes = await fetch(`http://localhost:5001/api/personas-filtros?id_persona=${idPersona}`);
        const personaData = await personaRes.json();
        const persona = Array.isArray(personaData) ? personaData[0] : personaData;

        return {
          id_orden: orden.id_orden,
          nombre_cliente: `${(persona?.nombre || "").split(" ")[0]} ${(persona?.apellido || "").split(" ")[0]}`,
        };
      });

      const resultados = await Promise.all(clientePromises);
      const clienteMap = {};
      resultados.forEach((cliente) => {
        if (cliente) clienteMap[cliente.id_orden] = cliente.nombre_cliente;
      });
      setClientes(clienteMap);
    } catch (error) {
      console.error("Error al obtener clientes:", error);
    }
  };

  useEffect(() => {
    const filtradas = ordenes.filter((orden) => {
      const clienteNombre = clientes[orden.id_orden]?.toLowerCase() || "";
      const cumpleCliente = clienteNombre.includes(filtroCliente.toLowerCase());
      const cumpleEstado = filtroEstado ? orden.estado === filtroEstado : true;

      const fechaAsignacion = new Date(orden.fecha_asignacion);
      const desde = filtroFechaInicio ? new Date(filtroFechaInicio) : null;
      const hasta = filtroFechaFin ? new Date(filtroFechaFin) : null;

      const cumpleFechaInicio = desde ? fechaAsignacion >= desde : true;
      const cumpleFechaFin = hasta ? fechaAsignacion <= hasta : true;

      return cumpleCliente && cumpleEstado && cumpleFechaInicio && cumpleFechaFin;
    });
    setPagina(1);
    setOrdenesFiltradas(filtradas);
  }, [filtroCliente, filtroEstado, filtroFechaInicio, filtroFechaFin, clientes, ordenes]);

  const finalizarOrden = async (id) => {
    const confirm = await Swal.fire({ title: "¿Ya Finalizastes la orden de instalacion?", icon: "warning", showCancelButton: true });
    if (!confirm.isConfirmed) return;
    const res = await fetch(`http://localhost:5010/ordenes_instalacion/finalizar/${id}`, { method: "PUT" });
    if (res.ok) {
      Swal.fire("Finalizada", "La orden ha sido finalizada.", "success");
      window.location.reload();
    } else {
      Swal.fire("Error", "No se pudo finalizar.", "error");
    }
  };

  const subirDocumento = async (e, id) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("documento", file);

    const res = await fetch(`http://localhost:5010/ordenes_instalacion/documento/${id}`, {
      method: "PUT",
      body: formData,
    });
    if (res.ok) {
      Swal.fire("Éxito", "Documento subido exitosamente", "success");
    } else {
      Swal.fire("Error", "No se pudo subir el documento", "error");
    }
  };

  const descargarPDF = (id) => {
    window.open(`http://localhost:5010/ordenes_instalacion/ver-documento/${id}`, "_blank");
  };

  const paginadas = ordenesFiltradas.slice((pagina - 1) * ordenesPorPagina, pagina * ordenesPorPagina);
  const totalPaginas = Math.ceil(ordenesFiltradas.length / ordenesPorPagina);
  const cambiarPagina = (nuevaPagina) => setPagina(nuevaPagina);

  return (
    <div className="p-4 bg-white shadow-md rounded-xl ml-6">
      <h2 className="text-2xl font-bold mb-4 text-green-700">Órdenes Asignadas</h2>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3 mb-4">
        <input type="text" placeholder="Buscar por cliente..." value={filtroCliente} onChange={(e) => setFiltroCliente(e.target.value)} className="border px-4 py-2 rounded-md shadow-sm w-full" />
        <select value={filtroEstado} onChange={(e) => setFiltroEstado(e.target.value)} className="border px-4 py-2 rounded-md shadow-sm w-full">
          <option value="">Todos los estados</option>
          <option value="pendiente">Pendiente</option>
          <option value="finalizado">Finalizado</option>
        </select>
        <input type="date" value={filtroFechaInicio} onChange={(e) => setFiltroFechaInicio(e.target.value)} className="border px-4 py-2 rounded-md shadow-sm w-full" />
        <input type="date" value={filtroFechaFin} onChange={(e) => setFiltroFechaFin(e.target.value)} className="border px-4 py-2 rounded-md shadow-sm w-full" />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left border border-gray-200 shadow-md rounded-xl overflow-hidden">
          <thead className="bg-green-600 text-white text-base">
            <tr>
              <th className="px-4 py-2">Contrato</th>
              <th className="px-4 py-2">Cliente</th>
              <th className="px-4 py-2">Estado</th>
              <th className="px-4 py-2">Asignación</th>
              <th className="px-4 py-2">Instalación</th>
              <th className="px-4 py-2">Acciones</th>
            </tr>
          </thead>
          <tbody>
            {paginadas.map((orden) => (
              <tr key={orden.id_orden} className="border-b">
                <td className="px-4 py-2">{orden.id_contrato}</td>
                <td className="px-4 py-2">{clientes[orden.id_orden] || "Cargando..."}</td>
                <td className="px-4 py-2">
                  <span className={`px-2 py-1 text-xs rounded-full text-white ${orden.estado === "finalizado" ? "bg-green-600" : "bg-yellow-500"}`}>{orden.estado}</span>
                </td>
                <td className="px-4 py-2">{format(new Date(orden.fecha_asignacion), "yyyy-MM-dd")}</td>
                <td className="px-4 py-2">{format(new Date(orden.fecha_instalacion), "yyyy-MM-dd")}</td>
                <td className="px-4 py-2 space-x-2 flex items-center">
                  {orden.estado === "en_proceso" && (
                    <button onClick={() => finalizarOrden(orden.id_orden)} className="bg-red-600 hover:bg-red-700 text-white flex items-center gap-2 px-4 py-1.5 rounded-lg text-sm shadow transition duration-200">
                      <FaCheck />
                      Finalizar
                    </button>
                  )}
                  {(orden.estado === "finalizado") && (
                    <>
                      <label className="cursor-pointer bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded">
                        <FaFileUpload />
                        <input type="file" hidden onChange={(e) => subirDocumento(e, orden.id_orden)} />
                      </label>
                    </>
                  )}
                  <button onClick={() => descargarPDF(orden.id_orden)} className="bg-green-900 hover:bg-green-800 text-white px-2 py-1 rounded">
                    <FaDownload />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex justify-center mt-4">
        {Array.from({ length: totalPaginas }, (_, index) => (
          <button key={index} className={`mx-1 px-3 py-1 rounded-full ${pagina === index + 1 ? "bg-green-600 text-white" : "bg-gray-200"}`} onClick={() => cambiarPagina(index + 1)}>
            {index + 1}
          </button>
        ))}
      </div>
    </div>
  );
};

export default OrdenesAsignadasTecnico;