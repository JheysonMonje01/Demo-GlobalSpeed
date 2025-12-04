import { useState, createContext, useContext } from "react";
import { Eye, EyeOff, Home, Lock, Mail, CheckCircle, XCircle } from "lucide-react";
import { useNavigate } from "react-router-dom";

/**
 * Mock context (reemplaza por tu contexto real en producción)
 */
const UserContext = createContext({
  actualizarUsuario: async () => {
    console.log("Mock: actualizarUsuario()");
    return true;
  },
});
const useUser = () => useContext(UserContext);

/**
 * LoginPage - Responsive, accesible y optimizada para producción
 */
const LoginPage = () => {
  const navigate = useNavigate();
  const { actualizarUsuario } = useUser();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showForgot, setShowForgot] = useState(false);
  const [message, setMessage] = useState(null); // { text, type }
  const [loading, setLoading] = useState(false);

  const displayMessage = (text, type = "error", duration = 4000) => {
    setMessage({ text, type });
    if (duration) setTimeout(() => setMessage(null), duration);
  };

  const validateForm = () => {
    if (!email) {
      displayMessage("Por favor ingresa tu correo.", "error");
      return false;
    }
    if (!password) {
      displayMessage("Por favor ingresa tu contraseña.", "error");
      return false;
    }
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    setLoading(true);
    setMessage(null);

    try {
      // Nota: Mantener el fetch en el cliente es solo para propósitos de demostración.
      // Asegúrate de que tu backend esté corriendo en http://localhost:5000/auth/login
      const response = await fetch("http://localhost:5000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correo: email, contrasena: password }),
      });

      const data = await response.json();

      if (!response.ok) {
        sessionStorage.setItem("correo_temporal", email);
        sessionStorage.setItem("permitido_recuperar", "true");
        displayMessage(data?.error || "Error al iniciar sesión", "error");
        setPassword("");
        setShowForgot(true);
        setLoading(false);
        return;
      }

      const { token, mensaje } = data;
      localStorage.setItem("token", token);

      // Decodificar payload JWT (simple)
      const payload = JSON.parse(atob(token.split(".")[1]));
      let usuario = payload.sub;
      if (typeof usuario === "string") usuario = JSON.parse(usuario);
      const rol = parseInt(usuario.rol, 10);
      const id_usuario = usuario.id;

      localStorage.setItem("id_usuario", String(id_usuario));
      localStorage.setItem("rol", String(rol));

      await actualizarUsuario();

      displayMessage(mensaje || "¡Inicio de sesión exitoso! Redirigiendo...", "success");
      setTimeout(() => {
        if (rol === 1) navigate("/admin/dashboard");
        else if (rol === 2) navigate("/tecnico/dashboard");
        else if (rol === 3) navigate("/cliente/dashboard");
        else navigate("/");
      }, 900);
    } catch (err) {
      console.error("Login error:", err);
      displayMessage("Error de conexión con el servidor", "error");
    } finally {
      setLoading(false);
    }
  };

  const CustomMessage = ({ text, type }) => {
    if (!text) return null;
    const isSuccess = type === "success";
    const bg = isSuccess ? "bg-emerald-50 border-emerald-300 text-emerald-800" : "bg-red-50 border-red-300 text-red-800";
    const Icon = isSuccess ? CheckCircle : XCircle;
    return (
      // Borde redondeado de los mensajes también reducido a 'rounded-md'
      <div role="status" aria-live="polite" className={`p-3 mb-4 border rounded-md ${bg} flex items-start gap-2`}>
        <Icon className="w-5 h-5 mt-0.5" />
        <p className="text-sm font-medium">{text}</p>
      </div>
    );
  };

  return (
    <main className="min-h-screen w-full font-sans bg-gray-50">
      <div className="min-h-screen grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-0">
        
        <aside
          aria-hidden="true"
          className="hidden md:block md:col-span-1 lg:col-span-2 relative bg-center bg-no-repeat bg-cover p-8 shadow-2xl z-10"
          style={{
            backgroundImage: "url('/imagenes/page-login.png')",
            backgroundColor: "#0d9488",
            minHeight: "100vh",
          }}
        >
          <div className="absolute inset-0 bg-black/10 pointer-events-none" /> 
        </aside>

        <section className="col-span-1 md:col-span-1 lg:col-span-3 flex items-center justify-center p-6 sm:p-10 lg:p-16 bg-gray-50 relative">
          {/* CAMBIO 1: Aumentar el ancho máximo del contenedor del formulario */}
          <div className="w-full max-w-md sm:max-w-lg">
            {/* CAMBIO 2: Reducir el borde redondeado del formulario a 'rounded-lg' y aumentar el padding */}
            <div className="bg-white border border-gray-200 rounded-lg shadow-xl p-10 sm:p-12 transition relative">
              
              <button
                type="button"
                aria-label="Ir a inicio"
                onClick={() => navigate("/")}
                className="absolute top-6 right-6 text-gray-400 hover:text-emerald-700 inline-flex"
                title="Página principal"
              >
                <Home size={20} />
              </button>

              <header className="mb-8 text-center">
                <div className="flex items-center justify-center mb-6">
                  <img
                    src="/imagenes/global-speed.png"
                    alt="Global Speed"
                    className="w-48 h-auto"
                    width={160}
                    height="auto"
                    loading="eager"
                  />
                </div>
                
                <h1 className="text-3xl font-bold text-gray-800 tracking-tight">Acceso a la Plataforma</h1>
                <p className="text-sm text-gray-500 mt-2">Bienvenido. Introduce tus datos</p>
              </header>

              <form onSubmit={handleSubmit} className="space-y-6" noValidate>
                <CustomMessage text={message?.text} type={message?.type} />

                {/* Email Input */}
                <label className="block">
                  <span className="sr-only">Correo electrónico</span>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                      <Mail size={18} />
                    </span>
                    <input
                      type="email"
                      name="email"
                      autoComplete="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="Correo electrónico"
                      aria-label="Correo electrónico"
                      // Borde redondeado del input reducido a 'rounded-md'
                      className="w-full pl-10 pr-4 py-3 rounded-md border border-gray-300 text-gray-800 placeholder-gray-400
                                 focus:outline-none focus:border-emerald-600 focus-visible:ring-2 focus-visible:ring-emerald-200 focus-visible:ring-offset-0"
                    />
                  </div>
                </label>

                {/* Password Input */}
                <label className="block">
                  <span className="sr-only">Contraseña</span>
                  <div className="relative">
                    <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                      <Lock size={18} />
                    </span>
                    <input
                      type={showPassword ? "text" : "password"}
                      name="password"
                      autoComplete="current-password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Contraseña"
                      aria-label="Contraseña"
                      // Borde redondeado del input reducido a 'rounded-md'
                      className="w-full pl-10 pr-12 py-3 rounded-md border border-gray-300 text-gray-800 placeholder-gray-400
                                 focus:outline-none focus:border-emerald-600 focus-visible:ring-2 focus-visible:ring-emerald-200 focus-visible:ring-offset-0"
                    />
                    <button
                      type="button"
                      aria-label={showPassword ? "Ocultar contraseña" : "Mostrar contraseña"}
                      onClick={() => setShowPassword((s) => !s)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-emerald-700"
                      tabIndex={0}
                    >
                      {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                    </button>
                  </div>
                </label>

                {/* Submit Button & Forgot Password */}
                <div className="flex flex-col items-center pt-2">
                  <button
                    type="submit"
                    disabled={loading}
                    // Borde redondeado del botón reducido a 'rounded-md'
                    className="w-full inline-flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-800
                               text-white font-semibold py-3 rounded-md shadow-md hover:shadow-lg disabled:opacity-60 disabled:cursor-wait transition duration-300"
                  >
                    {loading ? "Validando..." : "INICIAR SESIÓN"}
                  </button>

                  {showForgot && (
                    <button
                      type="button"
                      onClick={() => navigate("/recuperar")}
                      className="mt-4 text-sm text-emerald-600 hover:text-emerald-700 hover:underline font-medium"
                    >
                      ¿Olvidaste tu contraseña?
                    </button>
                  )}
                </div>
              </form>
            </div>

            <div className="mt-8 text-center text-xs text-gray-400">
              © {new Date().getFullYear()} Global Speed — Acceso seguro.
            </div>
          </div>
        </section>
      </div>
    </main>
  );
};

export default LoginPage;