import React, { useState, useEffect } from "react";

const SeleccionCliente = ({ onClienteSeleccionado }) => {
  const [clientes, setClientes] = useState([]);
  const [busqueda, setBusqueda] = useState("");

  useEffect(() => {
    fetch("http://localhost:5001/clientes")
      .then((res) => res.json())
      .then((data) => setClientes(data));
  }, []);

  const filtrados = clientes.filter((c) =>
    c.persona.nombre.toLowerCase().includes(busqueda.toLowerCase())
  );

  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold mb-2">👤 Cliente</h2>
      <input
        type="text"
        placeholder="Buscar cliente..."
        value={busqueda}
        onChange={(e) => setBusqueda(e.target.value)}
        className="border p-2 rounded w-full mb-2"
      />
      <select
        className="w-full border p-2 rounded"
        onChange={(e) =>
          onClienteSeleccionado(clientes.find((c) => c.id_cliente == e.target.value))
        }
      >
        <option value="">-- Selecciona un cliente --</option>
        {filtrados.map((cliente) => (
          <option key={cliente.id_cliente} value={cliente.id_cliente}>
            {cliente.persona.nombre} {cliente.persona.apellido}
          </option>
        ))}
      </select>
    </div>
  );
};

export default SeleccionCliente;
