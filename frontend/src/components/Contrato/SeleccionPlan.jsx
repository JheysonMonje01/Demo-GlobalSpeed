import React, { useState, useEffect } from "react";

const SeleccionPlan = ({ onPlanSeleccionado }) => {
  const [planes, setPlanes] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5005/planes")
      .then((res) => res.json())
      .then((data) => setPlanes(data));
  }, []);

  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold mb-2">🌐 Plan de Internet</h2>
      <select
        className="w-full border p-2 rounded"
        onChange={(e) =>
          onPlanSeleccionado(planes.find((p) => p.id === parseInt(e.target.value)))
        }
      >
        <option value="">-- Selecciona un plan --</option>
        {planes.map((plan) => (
          <option key={plan.id} value={plan.id}>
            {plan.nombre_plan} - ${plan.precio}
          </option>
        ))}
      </select>
    </div>
  );
};

export default SeleccionPlan;
