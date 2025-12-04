import React, { useEffect, useState } from "react";

const EmpresaInfo = ({ idEmpresa }) => {
  const [empresa, setEmpresa] = useState(null);

  useEffect(() => {
    const fetchEmpresa = async () => {
      const res = await fetch(`http://localhost:5002/api/empresa`);
      const data = await res.json();
      if (data.status === "success") setEmpresa(data.data);
    };
    fetchEmpresa();
  }, [idEmpresa]);

  if (!empresa) return <p>Cargando empresa...</p>;

  return (
    <div className="bg-white p-4 shadow-md rounded-xl border mb-6">
      <h2 className="text-xl font-bold mb-2">🏢 Empresa</h2>
      <p><strong>Nombre:</strong> {empresa.nombre}</p>
      <p><strong>RUC:</strong> {empresa.ruc}</p>
      <p><strong>Dirección:</strong> {empresa.direccion}</p>
      <p><strong>Representante:</strong> {empresa.representante}</p>
    </div>
  );
};

export default EmpresaInfo;
