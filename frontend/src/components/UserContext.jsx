import { createContext, useState, useEffect } from 'react';

export const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [usuario, setUsuario] = useState(null);

  const actualizarUsuario = async () => {
    const id_usuario = localStorage.getItem("id_usuario");
    const id_rol = localStorage.getItem("rol");

    if (!id_usuario) return;

    try {
      const res = await fetch(`http://localhost:5001/api/personas-filtros?id_usuario=${id_usuario}`);
      const data = await res.json(); // ✅ esta es la línea que estaba faltando
      const dataPersona = Array.isArray(data) ? data : [];

      console.log("Respuesta persona:", dataPersona);

      let nombreRol = "Usuario";
      if (id_rol) {
        const resRol = await fetch(`http://localhost:5000/api/roles/filtrado?id_rol=${id_rol}`);
        const dataRol = await resRol.json();
        if (Array.isArray(dataRol) && dataRol.length > 0) {
          nombreRol = dataRol[0].nombre_rol;
        }
      }

      const personaFiltrada = dataPersona.find(p => String(p.id_usuario) === String(id_usuario));
      if (personaFiltrada) {
        setUsuario({ ...personaFiltrada, rol: nombreRol });
      } else {
        console.warn("No se encontró usuario con id_usuario:", id_usuario);
      }

    } catch (err) {
      console.error("Error al obtener usuario:", err);
    }
  };


  useEffect(() => {
  actualizarUsuario(); // Solo una vez al montar
}, []);



  return (
    <UserContext.Provider value={{ usuario, actualizarUsuario, setUsuario }}>
      {children}
    </UserContext.Provider>
  );
};
