// src/components/EmpresaContext.jsx
import { createContext, useState, useEffect } from 'react';

const EmpresaContext = createContext();

function EmpresaProvider({ children }) {
  const [empresa, setEmpresa] = useState(null);
  const [logoPreview, setLogoPreview] = useState(null);

  const cargarEmpresa = async () => {
    try {
      const res = await fetch("http://localhost:5002/api/empresa");
      const data = await res.json();

      const datosEmpresa = Array.isArray(data) ? data[0] : data;

      if (datosEmpresa && datosEmpresa.nombre) {
        setEmpresa(datosEmpresa);
        setLogoPreview(
          datosEmpresa.logo ? `data:image/jpeg;base64,${datosEmpresa.logo}` : null
        );
      } else {
        setEmpresa(null);
        setLogoPreview(null);
      }
    } catch (error) {
      console.error("❌ Error al obtener empresa:", error);
      setEmpresa(null);
      setLogoPreview(null);
    }
  };

  useEffect(() => {
    cargarEmpresa();
  }, []);

  return (
    <EmpresaContext.Provider
      value={{ empresa, setEmpresa, logoPreview, setLogoPreview, cargarEmpresa }}
    >
      {children}
    </EmpresaContext.Provider>
  );
}

export { EmpresaContext, EmpresaProvider };
