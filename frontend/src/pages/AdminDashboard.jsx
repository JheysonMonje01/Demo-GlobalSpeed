import React from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const data = [
  { name: "Ene", usuarios: 30, clientes: 20 },
  { name: "Feb", usuarios: 45, clientes: 35 },
  { name: "Mar", usuarios: 60, clientes: 50 },
  { name: "Abr", usuarios: 80, clientes: 65 },
];

const AdminDashboard = () => {
  return (
    <>
      {/* Tarjetas informativas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white shadow rounded-lg p-4 border-l-4 border-green-500">
          <h4 className="text-sm font-semibold text-gray-500">Total Clientes</h4>
          <p className="text-2xl font-bold text-green-700">124</p>
        </div>
        <div className="bg-white shadow rounded-lg p-4 border-l-4 border-blue-500">
          <h4 className="text-sm font-semibold text-gray-500">Total Técnicos</h4>
          <p className="text-2xl font-bold text-blue-700">16</p>
        </div>
        <div className="bg-white shadow rounded-lg p-4 border-l-4 border-purple-500">
          <h4 className="text-sm font-semibold text-gray-500">Tarjetas ISP</h4>
          <p className="text-2xl font-bold text-purple-700">48</p>
        </div>
      </div>

      {/* Gráfica informativa */}
      <div className="bg-white shadow rounded-lg p-4 mb-6">
        <h4 className="text-lg font-semibold mb-4 text-gray-700">Actividad Mensual</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="usuarios" fill="#10B981" name="Usuarios" />
            <Bar dataKey="clientes" fill="#3B82F6" name="Clientes" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default AdminDashboard;
