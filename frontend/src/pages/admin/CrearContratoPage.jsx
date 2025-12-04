import React, { useEffect, useState } from "react";
import { ScrollText, Wifi, RadioTower, MapPin } from "lucide-react";
import MapaUbicacionContrato from "../../components/Contrato/MapaUbicacionContrato";
import GoogleMapLoader from "../../components/GoogleMapLoader"; // asegúrate de importar bien
import { toast } from "react-toastify";
import Swal from "sweetalert2";


const CrearContratoPage = () => {
  const [empresa, setEmpresa] = useState(null);
  const [clientes, setClientes] = useState([]);
  const [planes, setPlanes] = useState([]);
  
  const [onus, setOnus] = useState([]);
  const [form, setForm] = useState({ lat: "", lng: "" });
  const [cajaSeleccionada, setCajaSeleccionada] = useState(null);
  const [nombreUbicacion, setNombreUbicacion] = useState("");


  const [clienteSeleccionado, setClienteSeleccionado] = useState(null);
  const [planSeleccionado, setPlanSeleccionado] = useState(null);
  const [onuSeleccionada, setOnuSeleccionada] = useState(null);
  const [busquedaCliente, setBusquedaCliente] = useState("");
  const [ubicacionSeleccionada, setUbicacionSeleccionada] = useState(null);
  const [clienteBloqueado, setClienteBloqueado] = useState(false);
  const [planBloqueado, setPlanBloqueado] = useState(false);
  const [onuBloqueado, setOnuBloqueado] = useState(false);


  useEffect(() => {
    obtenerEmpresa();
    obtenerClientes();
    obtenerPlanes();
    obtenerOnus();
  }, []);

  const obtenerEmpresa = async () => {
    const res = await fetch("http://localhost:5002/api/empresa");
    const data = await res.json();
    if (res.ok) setEmpresa(data[0]);
  };

  const obtenerClientes = async () => {
  const res = await fetch("http://localhost:5001/clientes");
  const data = await res.json();

  if (res.ok && Array.isArray(data)) {
    setClientes(data);  // ✅ si ya es un array
  } else if (res.ok && Array.isArray(data.data)) {
    setClientes(data.data);  // ✅ si viene como { data: [...] }
  } else {
    console.error("❌ Formato inesperado en la respuesta de clientes:", data);
    toast.error("Error al cargar la lista de clientes");
    setClientes([]);  // para evitar fallos posteriores
  }
};


  const obtenerPlanes = async () => {
  try {
    const res = await fetch("http://localhost:5005/planes");
    const data = await res.json();

    console.log("Respuesta planes:", data);

    if (res.ok && Array.isArray(data.data)) {
      setPlanes(data.data); // ✅ Aquí accedes al array real
    } else {
      console.error("Respuesta inesperada de planes:", data);
    }
  } catch (err) {
    console.error("Error al obtener planes:", err);
  }
};

  const obtenerOnus = async () => {
    const res = await fetch("http://localhost:5004/onus/disponibles");
    const data = await res.json();
    if (res.ok) setOnus(data);
  };

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
  try {
    if (!ubicacionSeleccionada || !clienteSeleccionado || !planSeleccionado || !onuSeleccionada) {
      toast.warning("⚠️ Complete todos los campos antes de continuar.");
      return;
    }

    const payload = {
      id_empresa: 1,
      id_cliente: parseInt(form.id_cliente),
      id_plan: parseInt(form.id_plan),
      id_onu: parseInt(form.id_onu),
      lat: ubicacionSeleccionada.lat,
      lng: ubicacionSeleccionada.lng,
    };

    // Mostrar animación de espera
    Swal.fire({
      title: "Creando contrato...",
      text: "Por favor espera unos segundos",
      allowOutsideClick: false,
      didOpen: () => {
        Swal.showLoading();
      },
    });

    const res = await fetch("http://localhost:5006/contratos", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (res.ok) {
      Swal.fire({
        icon: "success",
        title: "Contrato creado exitosamente",
        showConfirmButton: false,
        timer: 2000,
      });

      // Limpiar campos después del éxito
      setForm({ lat: "", lng: "" });
      setClienteSeleccionado(null);
      setPlanSeleccionado(null);
      setOnuSeleccionada(null);
      setUbicacionSeleccionada(null);
    } else {
      Swal.fire({
        icon: "error",
        title: "Error al crear contrato",
        text: data.message || "Ocurrió un error inesperado.",
      });
    }
  } catch (error) {
    console.error("Error:", error);
    Swal.fire({
      icon: "error",
      title: "Error de red",
      text: "No se pudo conectar con el servidor.",
    });
  }
};



  return (
    <div className="w-[97%] mx-auto mt-4 min-h-[85vh] bg-white p-6 rounded-2xl shadow-2xl border-l-4 border-green-600">
      <h2 className="text-3xl font-bold mb-8 flex items-center gap-3 text-green-700">
        <ScrollText className="w-7 h-7" />
        Crear Contrato
      </h2>

      {/* Sección Empresa */}
      <section className="mb-8 bg-gray-50 p-4 rounded-xl shadow-sm border">
        <h3 className="text-xl font-semibold text-gray-800 flex items-center gap-2 mb-2">
          <i className="fa fa-building text-base"></i> Información de la Empresa
        </h3>
        {empresa ? (
          <div className="text-sm text-gray-700 grid grid-cols-1 sm:grid-cols-2 gap-2 pl-4">
            <p><strong>Nombre:</strong> {empresa.nombre}</p>
            <p><strong>Representante:</strong> {empresa.representante}</p>
            <p><strong>Dirección:</strong> {empresa.direccion}</p>
            <p><strong>RUC:</strong> {empresa.ruc}</p>
            <p><strong>Teléfonos:</strong> {empresa.telefonos?.map(t => `${t.telefono} (${t.tipo})`).join(", ")}</p>
            <p><strong>Correos:</strong> {empresa.correos?.map(c => `${c.correo} (${c.tipo})`).join(", ")}</p>
          </div>
        ) : (
          <p className="text-sm text-gray-500 pl-4">Cargando datos de empresa...</p>
        )}
      </section>

      {/* Sección Cliente */}
      <section className="mb-8 bg-gray-50 p-4 rounded-xl shadow-sm border">
  <h3 className="text-xl font-semibold text-gray-800 flex items-center gap-2 mb-2">
    <i className="fa fa-user text-base"></i> Datos del Cliente
    {clienteSeleccionado && <span className="text-green-600 text-sm ml-2">✅ Seleccionado</span>}
  </h3>

  {/* Solo se muestra si aún NO hay cliente seleccionado */}
  {!clienteSeleccionado && (
    <>
      <input
        className="w-full border px-3 py-2 rounded-md mb-3 text-sm shadow-sm"
        placeholder="Buscar por nombre o cédula"
        onChange={(e) => setBusquedaCliente(e.target.value)}
      />

      <select
        name="id_cliente"
        value={form.id_cliente || ""}
        onChange={(e) => {
          const c = clientes.find(c => c.id_cliente === parseInt(e.target.value));
          setForm({ ...form, id_cliente: e.target.value });
          setClienteSeleccionado(c);
        }}
        className="w-full border px-3 py-2 rounded-md text-sm shadow-sm"
      >
        <option value="">Seleccione un cliente</option>
        {clientes
          .filter(c =>
            `${c.persona?.nombre} ${c.persona?.apellido} ${c.persona?.cedula_ruc}`
              .toLowerCase()
              .includes(busquedaCliente.toLowerCase())
          )
          .map(c => (
            <option key={c.id_cliente} value={c.id_cliente}>
              {c.persona?.nombre} {c.persona?.apellido} - {c.persona?.cedula_ruc}
            </option>
          ))}
      </select>
    </>
  )}

  {/* Si ya hay cliente seleccionado, mostramos resumen */}
  {clienteSeleccionado && (
    <div className="text-sm mt-2 text-gray-700 bg-white p-3 rounded-md shadow-inner space-y-1">
      <p><strong>Nombre:</strong> {clienteSeleccionado.persona?.nombre} {clienteSeleccionado.persona?.apellido}</p>
      <p><strong>Cédula:</strong> {clienteSeleccionado.persona?.cedula_ruc}</p>
      <p><strong>Teléfono:</strong> {clienteSeleccionado.persona?.telefono}</p>
      <p><strong>Correo:</strong> {clienteSeleccionado.persona?.correo}</p>

      <button
        className="mt-2 text-blue-600 text-sm hover:underline"
        onClick={() => {
          setClienteSeleccionado(null);
          setForm({ ...form, id_cliente: "" });
        }}
      >
        Cambiar cliente
      </button>
    </div>
  )}
</section>



      {/* Sección Plan */}
      <section className="mb-8 bg-gray-50 p-4 rounded-xl shadow-sm border">
        <h3 className="text-xl font-semibold text-gray-800 flex items-center gap-2 mb-2">
          <Wifi className="w-5 h-5" /> Datos del Plan de Internet
          {planSeleccionado && <span className="text-green-600 text-sm ml-2">✅ Seleccionado</span>}
        </h3>

        {/* Mostrar select SOLO si aún no se ha seleccionado */}
        {!planSeleccionado && (
          <select
            name="id_plan"
            value={form.id_plan || ""}
            onChange={(e) => {
              const plan = planes.find(p => p.id_plan === parseInt(e.target.value));
              setForm({ ...form, id_plan: e.target.value });
              setPlanSeleccionado(plan);
            }}
            className="w-full border rounded-md px-3 py-2 text-sm shadow-sm"
          >
            <option value="">Seleccione un plan</option>
            {planes.map((plan) => (
              <option key={plan.id_plan} value={plan.id_plan}>
                {plan.nombre_plan} - ${plan.precio}
              </option>
            ))}
          </select>
        )}

        {/* Mostrar resumen SOLO si ya hay plan seleccionado */}
        {planSeleccionado && (
          <div className="text-sm mt-2 text-gray-700 bg-white p-3 rounded-md shadow-inner space-y-1">
            <p><strong>Nombre del plan:</strong> {planSeleccionado.nombre_plan}</p>
            <p><strong>Velocidad:</strong> ↓ {planSeleccionado.velocidad_bajada} Mbps / ↑ {planSeleccionado.velocidad_subida} Mbps</p>
            <p><strong>Precio:</strong> ${planSeleccionado.precio}</p>

            <button
              className="mt-2 text-blue-600 text-sm hover:underline"
              onClick={() => {
                setPlanSeleccionado(null);
                setForm({ ...form, id_plan: "" });
              }}
            >
              Cambiar plan
            </button>
          </div>
        )}
      </section>


      {/* Sección ONU */}
      <section className="mb-8 bg-gray-50 p-4 rounded-xl shadow-sm border">
        <h3 className="text-xl font-semibold text-gray-800 flex items-center gap-2 mb-2">
          <RadioTower className="w-5 h-5" /> Seleccionar ONU
          {onuSeleccionada && <span className="text-green-600 text-sm ml-2">✅ Seleccionada</span>}
        </h3>

        {/* Mostrar select solo si aún no se ha seleccionado */}
        {!onuSeleccionada && (
          <select
            name="id_onu"
            value={form.id_onu || ""}
            onChange={(e) => {
              const onu = onus.find(o => o.id_onu === parseInt(e.target.value));
              setForm({ ...form, id_onu: e.target.value });
              setOnuSeleccionada(onu);
            }}
            className="w-full border rounded-md px-3 py-2 text-sm shadow-sm"
          >
            <option value="">Seleccione una ONU</option>
            {onus.map(o => (
              <option key={o.id_onu} value={o.id_onu}>
                {o.serial} - {o.modelo_onu}
              </option>
            ))}
          </select>
        )}

        {/* Mostrar resumen si ya fue seleccionada */}
        {onuSeleccionada && (
          <div className="text-sm mt-2 text-gray-700 bg-white p-3 rounded-md shadow-inner space-y-1">
            <p><strong>Serial:</strong> {onuSeleccionada.serial}</p>
            <p><strong>Modelo:</strong> {onuSeleccionada.modelo_onu}</p>

            <button
              className="mt-2 text-blue-600 text-sm hover:underline"
              onClick={() => {
                setOnuSeleccionada(null);
                setForm({ ...form, id_onu: "" });
              }}
            >
              Cambiar ONU
            </button>
          </div>
        )}
      </section>


      {/* Mapa Ubicación */}
      <section className="mb-8 bg-gray-50 p-4 rounded-xl shadow-sm border">
        <h3 className="text-xl font-semibold mb-2 text-gray-800 flex items-center gap-2">
          <MapPin className="w-5 h-5" /> Ubicación de Instalación
        </h3>

        <GoogleMapLoader>
          <MapaUbicacionContrato
            ubicacionSeleccionada={ubicacionSeleccionada}
            setUbicacionSeleccionada={setUbicacionSeleccionada}
            setNombreUbicacion={setNombreUbicacion}
          />
        </GoogleMapLoader>

        {ubicacionSeleccionada && (
        <div className="mt-4 bg-white p-4 rounded-lg shadow-inner border text-sm text-gray-700 space-y-2">
          <p className="font-semibold text-gray-800">📍 Ubicación seleccionada:</p>
          <p>Latitud: {ubicacionSeleccionada.lat?.toFixed(6)}</p>
          <p>Longitud: {ubicacionSeleccionada.lng?.toFixed(6)}</p>
          <p>Dirección: {nombreUbicacion || 'Cargando...'}</p>
        </div>
      )}

      </section>


      <button
        className="w-full bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 text-white font-semibold py-3 px-4 rounded-xl shadow-lg transition-all duration-300"
        onClick={handleSubmit}
      >
        Crear Contrato
      </button>
    </div>
  );
};

export default CrearContratoPage;
