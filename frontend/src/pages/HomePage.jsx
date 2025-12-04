import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { FaWifi, FaRocket, FaUserShield, FaSignInAlt, FaHome, FaGlobe, FaMapMarkedAlt,FaCheck, FaPhone, FaUsers, FaMapMarkerAlt, FaPhoneAlt,FaFacebookF, FaInstagram, FaWhatsapp, FaEnvelope } from "react-icons/fa";
import { motion } from "framer-motion";
import { Link as ScrollLink } from 'react-scroll';
import GoogleMapContacto from "../components/GoogleMapContacto";
import VerificacionCoberturaPublica from "../components/CoberturaHome";
import { useJsApiLoader } from '@react-google-maps/api';
import { googleMapsOptions } from '../utils/googleMapsOptions';
import ChatbotWidget from "../components/ChatbotWidget";

const HomePage = () => {
  const [empresa, setEmpresa] = useState(null);
  const { isLoaded } = useJsApiLoader(googleMapsOptions);
  const [planes, setPlanes] = useState([]);


  const [menuOpen, setMenuOpen] = useState(false);


  useEffect(() => {
    fetch("http://localhost:5002/api/empresa")
      .then((res) => res.json())
      .then((data) => setEmpresa(data[0]))
      .catch((err) => console.error("Error cargando la información de la empresa", err));
  }, []);

  useEffect(() => {
  fetch("http://localhost:5005/planes")
    .then((res) => res.json())
    .then((data) => {
      if (Array.isArray(data.data)) {
        setPlanes(data.data); // ✅ ahora sí es un array válido
      } else {
        console.error("Formato inesperado:", data);
        setPlanes([]); // previene errores
      }
    })
    .catch((err) => {
      console.error("Error al obtener planes:", err);
      setPlanes([]);
    });
}, []);

useEffect(() => {
  fetch("http://localhost:5002/api/empresa")
    .then((res) => res.json())
    .then((data) => {
      if (data.length > 0) {
        setEmpresa(data[0]);
      }
    })
    .catch((err) =>
      console.error("Error cargando la información de la empresa", err)
    );
}, []);





  const navItems = [
    { label: "INICIO", to: "inicio", icon: <FaHome /> },
    { label: "PLANES DE INTERNET", to: "planes", icon: <FaGlobe /> },
    { label: "QUIENES SOMOS", to: "quienes", icon: <FaUsers /> },
    { label: "COBERTURA", to: "cobertura", icon: <FaMapMarkedAlt /> },
    { label: "CONTACTOS", to: "contacto", icon: <FaPhone /> },
  ];


  const getButtonColor = (color) => {
    switch (color) {
      case "green":
        return "bg-green-500 hover:bg-green-600";
      case "blue":
        return "bg-blue-500 hover:bg-blue-600";
      case "purple":
        return "bg-purple-500 hover:bg-purple-600";
      default:
        return "bg-gray-500 hover:bg-gray-600";
    }
  };


  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-green-100 font-sans scroll-smooth">
    {/* NAVBAR */}
      <nav className="bg-gradient-to-r from-green-700 to-green-900 backdrop-blur-sm fixed top-0 left-0 right-0 z-50 py-4 px-6 flex justify-between items-center shadow-md">
        <div className="flex items-center gap-4">
          <img src="/imagenes/logo.png" alt="Logo" className="w-10 h-10 rounded-full shadow-md" />
          <span className="text-white font-bold text-lg tracking-wide">
            {empresa?.nombre || ""}
          </span>
        </div>

        {/* Centro con navegación */}
        <div className="absolute left-1/2 transform -translate-x-1/2">
          <div className="hidden md:flex gap-10 items-center text-sm text-white font-medium">
            {navItems.map((item, idx) => (
              <ScrollLink
                key={idx}
                to={item.to}
                smooth={true}
                duration={900}
                className="relative group flex items-center gap-2 hover:text-white transition duration-300 cursor-pointer"
              >
                {item.icon}
                {item.label}
                <span className="absolute bottom-[-6px] left-1/2 w-0 h-0.5 bg-white transition-all duration-300 ease-in-out group-hover:left-0 group-hover:w-full"></span>
              </ScrollLink>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Link
            to="/login"
            className="flex items-center gap-2 bg-green-600 hover:bg-green-700 text-white font-semibold px-4 py-2 rounded-full shadow-md transition duration-300"
          >
            <FaSignInAlt className="text-white text-base" />
            Iniciar Sesión
          </Link>
        </div>
      </nav>

      {/* HEADER */}
      <header id="inicio" className="pt-32 relative h-[100vh] w-full">
        <img
          src="/imagenes/riobamba.jpg"
          alt="Riobamba"
          className="absolute inset-0 w-full h-full object-cover z-0"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-black/60 to-black/30 z-10"></div>

        <div className="relative z-20 h-full flex items-center justify-center px-6 md:px-20">
          <div className="flex flex-col md:flex-row items-center md:items-start justify-between w-full gap-8">
            <motion.div
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <img
                src="/imagenes/logo-global-speed.png"
                alt="Logo Global Speed"
                className="w-100 md:w-100"
              />
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="text-white text-center md:text-left flex flex-col justify-center items-center md:ml-30 md:mt-30"
            >
              <h1 className="text-3xl md:text-5xl font-extrabold mb-4">
                El mejor internet Home de alta velocidad
              </h1>
              <ScrollLink
                to="contacto"
                smooth={true}
                duration={500}
                className="mt-2 bg-green-600 hover:bg-green-700 text-white py-3 px-6 rounded-full font-semibold shadow-md transition duration-300 cursor-pointer"
              >
                Sé parte de Global Speed
              </ScrollLink>
            </motion.div>
          </div>
        </div>
      </header>
      {/* PLANES */}
    <section id="planes" className="relative text-center my-20 px-4">
  {/* Encabezado */}
  <motion.div
    initial={{ opacity: 0, y: -10 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
    className="flex justify-center items-center gap-2 mb-4"
  >
    <div className="w-10 h-0.5 bg-green-600 rounded-full"></div>
    <FaGlobe className="text-green-600 text-2xl" />
    <div className="w-10 h-0.5 bg-green-600 rounded-full"></div>
  </motion.div>

  <motion.h2
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.6 }}
    className="text-4xl md:text-5xl font-extrabold text-green-700 mb-4 tracking-tight"
  >
    Planes de Internet por Fibra Óptica
  </motion.h2>

  <motion.p
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.2, duration: 0.6 }}
    className="text-gray-600 text-base md:text-lg max-w-2xl mx-auto leading-relaxed"
  >
    Elige el plan ideal para ti: hogar, streaming, videojuegos o negocios. Conéctate con velocidad, estabilidad y soporte de primera.
  </motion.p>

  <motion.div
    initial={{ opacity: 0, y: -5 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.5, duration: 0.5 }}
    className="mt-6 flex justify-center"
  >
    <div className="w-24 h-1 rounded-full bg-green-500"></div>
  </motion.div>

  {/* Contenido dinámico */}
  {planes.length === 0 ? (
    <div className="mt-16 text-gray-500 text-lg font-medium">
      No hay planes disponibles por el momento.
    </div>
  ) : (
    <div
      className={`mt-14 grid gap-10 px-4 mx-auto ${
        planes.length === 1
          ? "max-w-md"
          : planes.length === 2
          ? "grid-cols-1 md:grid-cols-2 max-w-4xl"
          : "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 max-w-6xl"
      }`}
    >
      {planes.map((plan, idx) => {
        const colores = ["green", "blue", "purple"];
        const color = colores[idx % colores.length];

        const icono =
          color === "green" ? (
            <FaWifi className="text-green-600 text-5xl mb-4 mx-auto" />
          ) : color === "blue" ? (
            <FaRocket className="text-blue-600 text-5xl mb-4 mx-auto" />
          ) : (
            <FaUserShield className="text-purple-600 text-5xl mb-4 mx-auto" />
          );

        return (
          <motion.div
            key={plan.id_plan}
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.4, delay: idx * 0.2 }}
            className={`relative bg-white p-8 rounded-2xl shadow-xl border-l-8 border-${color}-500 hover:shadow-2xl transform transition hover:-translate-y-2 duration-300`}
          >
            <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-white rounded-full shadow-md p-4">
              {icono}
            </div>
            <h3 className={`mt-10 text-2xl font-extrabold text-${color}-700 mb-2`}>
              {plan.nombre_plan}
            </h3>
            <p className="text-sm text-gray-500">{plan.velocidad_bajada} Mbps</p>
            <p className="text-4xl font-bold text-gray-800 my-4">
              ${plan.precio}
              <span className="text-base font-normal text-gray-500">/mes</span>
            </p>
            <ul className="text-left space-y-3 mb-6 px-4">
              <li className="flex items-center text-gray-600 text-sm">
                <FaCheck className={`text-${color}-500 mr-3`} />
                Internet Estable y rápido
              </li>
              <li className="flex items-center text-gray-600 text-sm">
                <FaCheck className={`text-${color}-500 mr-3`} />
                Conexión por fibra óptica
              </li>
              <li className="flex items-center text-gray-600 text-sm">
                <FaCheck className={`text-${color}-500 mr-3`} />
                Soporte técnico 24/7
              </li>
            </ul>
            <button
              className={`w-full py-3 rounded-xl text-white font-bold text-sm tracking-wide shadow-inner transition duration-300 ${getButtonColor(
                color
              )} hover:scale-105`}
            >
              Contratar Plan
            </button>
          </motion.div>
        );
      })}
    </div>
  )}
</section>


    {/* Quienes Somos */}
    <section id="quienes" className="relative py-20 bg-gray-100 overflow-hidden">
        {/* Fondo decorativo SVG */}
        <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none z-0">
            <svg className="w-full h-full" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="gradient" x1="0" x2="1" y1="1" y2="0">
                <stop offset="0%" stopColor="#10B981" />
                <stop offset="100%" stopColor="#34D399" />
                </linearGradient>
            </defs>
            <rect width="100%" height="100%" fill="url(#gradient)" />
            </svg>
        </div>

        <div className="relative z-10 max-w-7xl mx-auto px-4 grid grid-cols-1 md:grid-cols-2 gap-10 items-center">
            
            {/* Imagen animada con logo */}
            <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            className="relative w-full h-[320px] md:h-[400px] rounded-2xl overflow-hidden shadow-2xl border border-gray-200"
            >
            <motion.img
                src="/imagenes/riobamba-noche.jpg"
                alt="Ciudad de noche"
                className="w-full h-full object-cover"
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ repeat: Infinity, duration: 10, ease: "easeInOut" }}
            />

            <img
                src="/imagenes/logo-global-speed.png"
                alt="Logo Global Speed"
                className="absolute top-0 right-0 w-55 md:w-55 drop-shadow-lg"
            />
            </motion.div>

            {/* Texto animado */}
            <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.3 }}
            >
            {/* Ícono decorativo y título */}
            <div className="flex items-center gap-2 mb-2">
                <div className="w-1.5 h-6 bg-green-500 rounded"></div>
                <h2 className="text-3xl md:text-4xl font-extrabold text-green-700">
                ¿Quiénes Somos?
                </h2>
            </div>

            <p className="text-gray-700 mb-6 leading-relaxed text-base md:text-lg">
                <strong className="text-green-700">Global Speed</strong> es un Proveedor de Servicios de Internet (ISP), legalmente autorizado por el ente regulador de telecomunicaciones del Ecuador (ARCOTEL). Nuestro objetivo es ofrecer acceso a internet de alta velocidad, estable y con atención personalizada. Nos enfocamos en hogares, negocios y comunidades en crecimiento.
            </p>

            <h3 className="text-2xl font-bold text-green-700 mb-2">
                ¿Dónde tenemos cobertura?
            </h3>
            <p className="text-gray-700 leading-relaxed text-base md:text-lg">
                <span className="font-semibold text-gray-900">Zona Centro y Sur de Riobamba:</span> La Estación, La Politécnica, Sultana, El Cisne, Terminal Terrestre, Panamericana Sur, La Matriz, San Alfonso, Bellavista, Yaruquíes, entre otros.
            </p>
            </motion.div>
        </div>
    </section>

      {/* FUTURA SECCIÓN */}
      <section id="cobertura" className="py-20 text-center text-gray-500">
        <VerificacionCoberturaPublica isLoaded={isLoaded} />
      </section>

      {/* CONTACTO */}
    <section id="contacto" className="bg-white py-20 px-4">
        <div className="text-center mb-12">
        <h2 className="text-4xl font-extrabold text-green-700 mb-2">
            ¡Estamos aquí para ayudarte!
        </h2>
        <p className="text-gray-600 text-sm md:text-base max-w-xl mx-auto">
            Contáctanos por cualquier consulta o requerimiento. Nuestro equipo estará encantado de atenderte lo antes posible.
        </p>
        </div>
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-10 items-stretch">

            {/* Formulario de contacto */}
        <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7 }}
            className="flex-1 max-w-[550px] bg-white p-8 rounded-2xl shadow-xl border border-green-100 "
        >
        <h2 className="text-3xl font-extrabold text-green-700 mb-2">Contáctanos</h2>
        <p className="text-gray-500 mb-6 text-sm">
            Déjanos tus inquietudes y te responderemos lo antes posible.
        </p>

        <form className="space-y-4 text-sm">
            {[
            { label: "Nombres*", type: "text", name: "nombres" },
            { label: "E-mail*", type: "email", name: "email" },
            { label: "Teléfono*", type: "tel", name: "telefono" },
            { label: "Ciudad*", type: "text", name: "ciudad" },
            ].map((field, idx) => (
            <div key={idx}>
                <label className="block text-gray-700 font-medium mb-1">{field.label}</label>
                <input
                type={field.type}
                name={field.name}
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-400 transition"
                />
            </div>
            ))}

            <div>
            <label className="block text-gray-700 font-medium mb-1">Mensaje</label>
            <textarea
                rows="4"
                name="mensaje"
                className="w-full border border-gray-300 rounded-md px-4 py-2 focus:outline-none focus:ring-2 focus:ring-green-400 transition"
            />
            </div>

            <button
            type="submit"
            className="w-full mt-4 bg-green-600 hover:bg-green-700 text-white font-bold py-3 rounded-lg shadow-md transition"
            >
            ENVIAR
            </button>
        </form>
        </motion.div>


            {/* Mapa */}
        <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.7 }}
            className="flex-1 min-h-[450px] rounded-2xl overflow-hidden shadow-lg border border-gray-200" // 👈 importante este height
        >
            <GoogleMapContacto isLoaded={isLoaded} />
        </motion.div>

        </div>
    </section>

    {/* Footer */}
        <footer className="bg-green-700 text-gray-300 mt-20">
            <div className="max-w-7xl mx-auto px-6 py-10 grid grid-cols-1 md:grid-cols-2 gap-8">
                
                {/* Contacto */}
                <div>
  <h3 className="text-lg font-bold text-white mb-4">CONTACTO</h3>

  {/* Dirección */}
  <p className="flex items-center gap-2 mb-2">
    <FaMapMarkerAlt className="text-white-500" />
    {empresa?.direccion || "Calle Espejo y Primera constituyente, Segundo Piso oficina 204."}
  </p>

  {/* Teléfonos */}
  <p className="flex items-start gap-2 mb-2">
    <FaPhoneAlt className="text-white-500 mt-1" />
    {empresa?.telefonos?.length > 0
      ? empresa.telefonos.map(t => t.telefono).join(" - ")
      : "0963210011 - 0998969818"}
  </p>

  {/* Correos */}
  <p className="flex items-start gap-2">
    <FaEnvelope className="text-white-500 mt-1" />
    {empresa?.correos?.length > 0
      ? empresa.correos.map(c => c.correo).join(" - ")
      : "globalspeeds.a.s@gmail.com "}
  </p>
</div>



            {/* Redes Sociales */}
            <div className="flex flex-col md:items-end">
            <h3 className="text-lg font-bold text-white mb-4">SÍGUENOS</h3>
            <div className="flex gap-4 text-2xl">
                <a
                href="https://www.facebook.com/p/GlobalSpeed-SAS-100072400118633/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-white-500 hover:text-white transition"
                >
                <FaFacebookF />
                </a>
                <a
                href="https://instagram.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-white-500 hover:text-white transition"
                >
                <FaInstagram />
                </a>
                <a
                href="https://wa.me/593963210011"
                target="_blank"
                rel="noopener noreferrer"
                className="text-white-500 hover:text-white transition"
                >
                <FaWhatsapp />
                </a>
                <a
                href={`mailto:${empresa?.correo || "globalspeeds.a.s@gmail.com"}`}
                className="text-white-500 hover:text-white transition"
                >
                <FaEnvelope />
                </a>
            </div>
            </div>
        </div>

        {/* Línea inferior */}
        <div className="border-t border-white-700 text-center text-sm text-white-500 py-4">
            &copy; {new Date().getFullYear()} {empresa?.nombre || "Global Speed"}. Todos los derechos reservados.
        </div>
    </footer>

    {/* Chatbot flotante */}
    <ChatbotWidget />
    
    </div>
  );
};

export default HomePage;
