// src/pages/Dashboard.jsx
// 👈 Asegúrate que esto está así
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
import { Wrench, CheckCircle, Hourglass } from "lucide-react";

const data = [
  { name: "Ene", completadas: 10, pendientes: 5 },
  { name: "Feb", completadas: 15, pendientes: 3 },
  { name: "Mar", completadas: 12, pendientes: 4 },
  { name: "Abr", completadas: 18, pendientes: 2 },
];

const TecnicoDashboard = () => {
  return (
    <>
      {/* Tarjetas informativas */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white shadow rounded-lg p-4 border-l-4 border-yellow-500">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-semibold text-gray-500">Órdenes Asignadas</h4>
              <p className="text-2xl font-bold text-yellow-600">12</p>
            </div>
            <Hourglass className="text-yellow-500" />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-4 border-l-4 border-green-500">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-semibold text-gray-500">Instalaciones Completadas</h4>
              <p className="text-2xl font-bold text-green-600">34</p>
            </div>
            <CheckCircle className="text-green-500" />
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-4 border-l-4 border-blue-500">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="text-sm font-semibold text-gray-500">Total Actividades</h4>
              <p className="text-2xl font-bold text-blue-600">46</p>
            </div>
            <Wrench className="text-blue-500" />
          </div>
        </div>
      </div>

      {/* Gráfica de actividad */}
      <div className="bg-white shadow rounded-lg p-4 mb-6">
        <h4 className="text-lg font-semibold mb-4 text-gray-700">Actividad Mensual</h4>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="completadas" fill="#10B981" name="Completadas" />
            <Bar dataKey="pendientes" fill="#F59E0B" name="Pendientes" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
};

export default TecnicoDashboard;
