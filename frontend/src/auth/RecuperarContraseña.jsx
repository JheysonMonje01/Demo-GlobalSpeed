import { useEffect, useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { toast } from "react-toastify";

const RecuperarContraseña = () => {
  const [correo, setCorreo] = useState("");
  const [enviado, setEnviado] = useState(false);
  const [errorCorreo, setErrorCorreo] = useState("");
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const permitido = sessionStorage.getItem("permitido_recuperar");
    if (!permitido) {
      navigate("/unauthorized");
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const correoTemporal = sessionStorage.getItem("correo_temporal");

    if (correo !== correoTemporal) {
      setErrorCorreo("Debe ingresar el mismo correo que usó anteriormente");
      return;
    }

    try {
      const response = await fetch("http://192.168.1.4:5000/auth/recuperar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ correo }),
      });

      const data = await response.json();

      if (response.ok) {
        setEnviado(true);
        toast.success("Correo enviado con instrucciones");

        sessionStorage.removeItem("permitido_recuperar");
        sessionStorage.removeItem("correo_temporal");
      } else {
        toast.error(data.error || "Error al enviar el correo");
      }
    } catch (error) {
      toast.error("Error de conexión con el servidor");
    }
  };

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    if (params.has("token")) {
      const accesoRestablecer = sessionStorage.getItem("permitido_restablecer");
      if (!accesoRestablecer) {
        navigate("/unauthorized");
      }
    }
  }, [location, navigate]);

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg p-10 w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <img
            src="/imagenes/logo.png"
            alt="Logo Global Speed"
            className="h-16 w-auto mb-2"
          />
          <span className="text-2xl font-bold text-center text-green-700">GLOBAL SPEED</span>
        
          {!enviado && (
            <>
              <h2 className="text-2xl font-bold text-center text-gray-700">
                Recuperar contraseña
              </h2>
              <p className="text-gray-500 text-sm mt-1 text-center max-w-sm">
                Ingresa tu correo electrónico asociado a tu cuenta y te enviaremos un enlace para restablecer tu contraseña.
              </p>
            </>
          )}
        </div>

        {enviado ? (
          <div className="text-center">
            <h3 className="text-xl font-semibold text-gray-700 mb-2">Mensaje</h3>
            <p className="text-gray-600 text-base">
              Si el correo está registrado, recibirás un enlace para restablecer tu contraseña.
            </p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm text-gray-700 font-medium mb-1">
                Correo electrónico
              </label>
              <input
                type="email"
                value={correo}
                onChange={(e) => {
                  setCorreo(e.target.value);
                  setErrorCorreo("");
                }}
                placeholder="ejemplo@correo.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-gray-700 focus:outline-none focus:ring-2 focus:ring-green-400"
                required
              />
              {errorCorreo && (
                <p className="text-sm text-red-500 mt-1">{errorCorreo}</p>
              )}
            </div>

            <button
              type="submit"
              className="w-full bg-green-600 hover:bg-green-700 text-white py-3 text-lg rounded-lg transition"
            >
              Enviar correo
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default RecuperarContraseña;
