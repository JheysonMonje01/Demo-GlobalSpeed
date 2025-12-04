import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { toast } from "react-toastify";
import PasswordFieldWithValidation from "../components/PasswordFieldWithValidation";
import ConfirmarContrasena from "../components/ConfirmarContrasena";

const RestablecerContraseña = () => {
  const [nueva, setNueva] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const navigate = useNavigate();
  const location = useLocation();
  const token = new URLSearchParams(location.search).get("token");

  // Validar acceso autorizado desde sesión
  useEffect(() => {
    const permitido = sessionStorage.getItem("permitido_restablecer");
    if (!token) {
      navigate("/unauthorized");
    }
  }, [navigate, token]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (nueva !== confirmar) {
      toast.error("Las contraseñas no coinciden");
      return;
    }

    try {
      const response = await fetch(`http://192.168.1.4:5000/auth/restablecer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          token,
          nueva_contrasena: nueva,
          confirmar_contrasena: confirmar,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        toast.success("Contraseña actualizada correctamente");

        // Limpieza de sesión
        sessionStorage.removeItem("permitido_restablecer");

        navigate("/");
      } else {
        toast.error(data.error || "Error al restablecer la contraseña");
      }
    } catch (error) {
      toast.error("Error de conexión con el servidor.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center px-4">
      <div className="bg-white rounded-lg shadow-md p-8 w-full max-w-md">
        <div className="flex flex-col items-center mb-6">
          <img
            src="/imagenes/logo.png"
            alt="Logo Global Speed"
            className="h-16 w-auto mb-2"
          />
          <span className="text-2xl font-bold text-center text-green-700">GLOBAL SPEED</span>
          <hr />
          <hr />
          <h2 className="text-2xl font-bold text-center text-gray-700">
            Restablecer contraseña
          </h2>
          
        </div>

        <form onSubmit={handleSubmit} className="space-y-5">
          <PasswordFieldWithValidation
            label="Nueva contraseña"
            value={nueva}
            onChange={(e) => setNueva(e.target.value)}
          />

          <ConfirmarContrasena
            original={nueva}
            value={confirmar}
            onChange={(e) => setConfirmar(e.target.value)}
          />

          <button
            type="submit"
            className="w-full bg-green-600 hover:bg-green-700 text-white py-2 rounded-lg transition"
          >
            Guardar nueva contraseña
          </button>

          <div className="text-center mt-4">
            <button
              type="button"
              onClick={() => navigate("/")}
              className="text-sm text-green-600 hover:underline"
            >
              Volver al inicio de sesión
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RestablecerContraseña;
