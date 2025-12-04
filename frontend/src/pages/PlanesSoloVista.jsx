import React, { useEffect, useState } from "react";
import { Wifi, CheckCircle, Search } from "lucide-react";

const PlanesSoloVista = () => {
  const [planes, setPlanes] = useState([]);
  const [filtroNombre, setFiltroNombre] = useState("");
  const [precioSeleccionado, setPrecioSeleccionado] = useState("");
  const [velocidadSeleccionada, setVelocidadSeleccionada] = useState("");
  const [paginaActual, setPaginaActual] = useState(1);
  const planesPorPagina = 6;

  useEffect(() => {
    fetchPlanes();
  }, []);

  const fetchPlanes = async () => {
    try {
      const res = await fetch("http://localhost:5005/planes");
      const data = await res.json();
      setPlanes(data.data || []);
    } catch (error) {
      console.error("Error al cargar planes:", error);
    }
  };

  const preciosUnicos = [...new Set(planes.map((p) => Number(p.precio)))].sort((a, b) => a - b);
  const velocidadesUnicas = [...new Set(planes.map((p) => Number(p.velocidad_bajada)))].sort((a, b) => a - b);

  const planesFiltrados = planes.filter((plan) => {
    const coincideNombre = plan.nombre_plan.toLowerCase().includes(filtroNombre.toLowerCase());
    const coincidePrecio = precioSeleccionado === "" || Number(plan.precio) === Number(precioSeleccionado);
    const coincideVelocidad = velocidadSeleccionada === "" || Number(plan.velocidad_bajada) === Number(velocidadSeleccionada);
    return coincideNombre && coincidePrecio && coincideVelocidad;
  });

  const totalPaginas = Math.ceil(planesFiltrados.length / planesPorPagina);
  const inicio = (paginaActual - 1) * planesPorPagina;
  const planesPaginados = planesFiltrados.slice(inicio, inicio + planesPorPagina);

  return (
    <div className="max-w-7xl mx-auto bg-white rounded-2xl shadow-lg border border-gray-200 p-11">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-center text-green-700 mb-12">Planes de Internet</h1>

        {/* Filtros */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
          <div className="relative">
            <Search className="absolute top-3 left-3 text-gray-400" />
            <input
              type="text"
              placeholder="Buscar por nombre"
              value={filtroNombre}
              onChange={(e) => setFiltroNombre(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-300 shadow-sm focus:ring-2 focus:ring-green-400 bg-white"
            />
          </div>

          <select
            value={precioSeleccionado}
            onChange={(e) => setPrecioSeleccionado(e.target.value)}
            className="w-full px-4 py-2 rounded-xl border border-gray-300 shadow-sm focus:ring-2 focus:ring-green-400 bg-white"
          >
            <option value="">Filtrar por precio</option>
            {preciosUnicos.map((precio) => (
              <option key={precio} value={precio}>${precio.toFixed(2)}</option>
            ))}
          </select>

          <select
            value={velocidadSeleccionada}
            onChange={(e) => setVelocidadSeleccionada(e.target.value)}
            className="w-full px-4 py-2 rounded-xl border border-gray-300 shadow-sm focus:ring-2 focus:ring-green-400 bg-white"
          >
            <option value="">Filtrar por velocidad</option>
            {velocidadesUnicas.map((vel) => (
              <option key={vel} value={vel}>{vel} Mbps</option>
            ))}
          </select>
        </div>

        {/* Tarjetas */}
        <div className="grid gap-10 grid-cols-1 sm:grid-cols-2 xl:grid-cols-3">
          {planesPaginados.map((plan) => (
            <div
              key={plan.id_plan}
              className="relative bg-white rounded-2xl shadow-xl border border-gray-200 flex overflow-hidden group hover:shadow-green-300 transition-all duration-300"
            >
              {/* Borde izquierdo decorativo */}
              <div className="w-3 bg-green-500 rounded-l-2xl"></div>

              {/* Contenido */}
              <div className="flex-1 p-8 text-center flex flex-col items-center">
                <div className="bg-green-100 w-20 h-20 rounded-full flex items-center justify-center shadow-md mb-4">
                  <Wifi className="text-green-600 w-8 h-8" />
                </div>

                <h2 className="text-xl font-bold text-green-800 uppercase mb-2">
                  {plan.nombre_plan}
                </h2>

                <p className="text-base text-gray-600 font-medium mb-2">
                  {plan.velocidad_bajada} Mbps bajada / {plan.velocidad_subida} Mbps subida
                </p>

                <p className="text-3xl font-extrabold text-gray-800 mb-4">
                  ${Number(plan.precio).toFixed(2)} <span className="text-sm font-normal text-gray-500">/mes</span>
                </p>

                <div className="text-sm text-gray-700 space-y-1 mt-auto">
                  <div className="flex items-center justify-center gap-2">
                    <CheckCircle className="text-green-500 w-4 h-4" />
                    <span>Internet estable y rápido</span>
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <CheckCircle className="text-green-500 w-4 h-4" />
                    <span>Conexión por fibra óptica</span>
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <CheckCircle className="text-green-500 w-4 h-4" />
                    <span>Soporte técnico 24/7</span>
                  </div>
                </div>
              </div>
            </div>
          ))}
          {planesPaginados.length === 0 && (
  <div className="col-span-full flex flex-col items-center justify-center text-center py-16 text-gray-500">
    <Wifi className="w-12 h-12 text-gray-400 mb-4" />
    <p className="text-lg font-semibold">No hay planes disponibles</p>
    <p className="text-sm">Intenta ajustar los filtros o vuelve más tarde.</p>
  </div>
)}

        </div>

        {/* Paginación */}
        {totalPaginas > 1 && (
          <div className="mt-12 flex justify-center gap-2">
            {[...Array(totalPaginas)].map((_, index) => (
              <button
                key={index}
                onClick={() => setPaginaActual(index + 1)}
                className={`px-4 py-2 rounded-xl border text-sm font-medium ${
                  paginaActual === index + 1
                    ? "bg-green-600 text-white"
                    : "bg-white text-gray-700 border-gray-300"
                } hover:bg-green-500 hover:text-white transition-all`}
              >
                {index + 1}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PlanesSoloVista;
