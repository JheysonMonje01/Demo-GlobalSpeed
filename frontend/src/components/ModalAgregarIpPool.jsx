import React, { useEffect, useState } from "react";
import { PlusCircle } from "lucide-react";
import { toast } from "react-toastify";
import isIP from "validator/lib/isIP";
import ipaddr from "ipaddr.js";

const ModalAgregarIpPool = ({ visible, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    nombre: "",
    rango_inicio: "",
    rango_fin: "",
    mascara_subred: "255.255.255.0",
    gateway: "",
    dns_servidor: "",
    descripcion: "",
    id_mikrotik: ""
  });

  const [mikrotiks, setMikrotiks] = useState([]);

  useEffect(() => {
    const fetchMikrotiks = async () => {
      try {
        const res = await fetch("http://localhost:5002/mikrotik/configuraciones");
        const data = await res.json();
        setMikrotiks(data);
      } catch (error) {
        console.error("Error al cargar MikroTiks", error);
      }
    };
    if (visible) fetchMikrotiks();
  }, [visible]);

  const esIPValida = (ip) => {
    const regex = /^(25[0-5]|2[0-4][0-9]|1\d{2}|[1-9]?\d)(\.(?!$)|$){4}$/;
    return regex.test(ip);
  };

  const esMascaraValida = (mascara) => {
    const validas = [
      "255.0.0.0", "255.128.0.0", "255.192.0.0", "255.224.0.0",
      "255.240.0.0", "255.248.0.0", "255.252.0.0", "255.254.0.0",
      "255.255.0.0", "255.255.128.0", "255.255.192.0", "255.255.224.0",
      "255.255.240.0", "255.255.248.0", "255.255.252.0", "255.255.254.0",
      "255.255.255.0", "255.255.255.128", "255.255.255.192", "255.255.255.224",
      "255.255.255.240", "255.255.255.248", "255.255.255.252", "255.255.255.254"
    ];
    return validas.includes(mascara);
  };

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  function esIpValida(ip) {
  try {
    return ipaddr.isValid(ip.trim());
  } catch {
    return false;
  }
}

function estaEnLaMismaSubred(ip1, ip2, mascara) {
  try {
    const addr1 = ipaddr.parse(ip1);
    const addr2 = ipaddr.parse(ip2);
    const mask = ipaddr.parse(mascara);

    const red1 = addr1.toByteArray().map((b, i) => b & mask.toByteArray()[i]);
    const red2 = addr2.toByteArray().map((b, i) => b & mask.toByteArray()[i]);

    return JSON.stringify(red1) === JSON.stringify(red2);
  } catch {
    return false;
  }
}

const handleSubmit = async () => {
  const {
    nombre,
    rango_inicio,
    rango_fin,
    mascara_subred,
    gateway,
    dns_servidor,
    descripcion,
    id_mikrotik
  } = formData;

  // Campos requeridos
  if (!nombre || !rango_inicio || !rango_fin || !mascara_subred || !gateway || !id_mikrotik) {
    toast.error("Todos los campos obligatorios deben estar completos.");
    return;
  }

  // Validaciones de IP
  if (!esIpValida(rango_inicio)) {
    toast.error("La IP de inicio no es válida.");
    return;
  }
  if (!esIpValida(rango_fin)) {
    toast.error("La IP final no es válida.");
    return;
  }
  if (!esIpValida(gateway)) {
    toast.error("El gateway no es válido.");
    return;
  }
  if (dns_servidor && !esIpValida(dns_servidor)) {
    toast.error("El DNS ingresado no es válido.");
    return;
  }

  // Validación de subred
  if (!estaEnLaMismaSubred(rango_inicio, gateway, mascara_subred)) {
    toast.error("El gateway no pertenece al mismo segmento que la IP de inicio.");
    return;
  }

  // Enviar
  try {
    const res = await fetch("http://localhost:5004/pools/ip_pools", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formData)
    });

    const result = await res.json();

    if (res.ok) {
      toast.success("IP Pool creado correctamente.");
      onSuccess();
      onClose();
    } else {
      toast.error(result.message || "Error al crear el IP Pool.");
    }
  } catch (err) {
    toast.error("Error de conexión al servidor.");
    console.error(err);
  }
};

  if (!visible) return null;

  return (
    <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-50 px-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg p-6 border-t-4 border-green-700">
        <div className="flex items-center gap-2 mb-4">
          <PlusCircle className="text-emerald-600" size={26} />
          <h2 className="text-xl font-semibold text-emerald-700">Agregar Nuevo IP Pool</h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="text-sm font-medium">Nombre</label>
            <input name="nombre" onChange={handleChange} className="w-full border rounded px-3 py-2 focus:outline-emerald-400" />
          </div>
          <div>
            <label className="text-sm font-medium">MikroTik</label>
            <select
              name="id_mikrotik"
              onChange={handleChange}
              className="w-full border rounded px-3 py-2 focus:outline-emerald-400"
            >
              <option value="">Seleccione</option>
              {mikrotiks.map((m) => (
                <option key={m.id_mikrotik} value={m.id_mikrotik}>{m.nombre}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-sm font-medium">Rango inicio</label>
            <input name="rango_inicio" onChange={handleChange} className="w-full border rounded px-3 py-2 focus:outline-emerald-400" />
          </div>
          <div>
            <label className="text-sm font-medium">Rango fin</label>
            <input name="rango_fin" onChange={handleChange} className="w-full border rounded px-3 py-2 focus:outline-emerald-400" />
          </div>
          <div>
            <label className="text-sm font-medium">Máscara subred</label>
            <input name="mascara_subred" value={formData.mascara_subred} onChange={handleChange} className="w-full border rounded px-3 py-2 focus:outline-emerald-400" />
          </div>
          <div>
            <label className="text-sm font-medium">Gateway</label>
            <input name="gateway" onChange={handleChange} className="w-full border rounded px-3 py-2 focus:outline-emerald-400" />
          </div>
          <div className="md:col-span-2">
            <label className="text-sm font-medium">DNS Servidor</label>
            <input name="dns_servidor" onChange={handleChange} className="w-full border rounded px-3 py-2 focus:outline-emerald-400" />
          </div>
          <div className="md:col-span-2">
            <label className="text-sm font-medium">Descripción</label>
            <textarea name="descripcion" onChange={handleChange} className="w-full border rounded px-3 py-2 focus:outline-emerald-400" />
          </div>
        </div>

        <div className="mt-6 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-md border border-gray-300 text-gray-700 hover:bg-gray-100"
          >
            Cancelar
          </button>
          <button
            onClick={handleSubmit}
            className="bg-emerald-600 text-white px-5 py-2 rounded-md hover:bg-emerald-700"
          >
            Guardar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ModalAgregarIpPool;