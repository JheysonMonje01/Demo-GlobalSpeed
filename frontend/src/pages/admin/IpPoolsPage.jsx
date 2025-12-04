import React, { useEffect, useState } from "react";
import IpPoolTable from "../../components/IpPoolTable";
import ModalAgregarIpPool from "../../components/ModalAgregarIpPool";

const IpPoolsPage = () => {
  const [ipPools, setIpPools] = useState([]);
  const [mostrarModal, setMostrarModal] = useState(false);

  const cargarPools = async () => {
    try {
      const res = await fetch("http://localhost:5004/pools"); // Ajusta si necesitas paginación
      const data = await res.json();
      setIpPools(data);
    } catch (error) {
      console.error("Error al cargar pools:", error);
    }
  };

  useEffect(() => {
    cargarPools();
  }, []);

  return (
    <div className="p-6">
      

      <IpPoolTable data={ipPools} recargar={cargarPools} />
      <ModalAgregarIpPool
        visible={mostrarModal}
        onClose={() => setMostrarModal(false)}
        onSuccess={cargarPools}
      />
    </div>
  );
};

export default IpPoolsPage;
