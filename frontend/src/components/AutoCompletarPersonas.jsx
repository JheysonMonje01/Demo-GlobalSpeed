import React, { useEffect, useState } from 'react';

const AutocompletarPersonas = ({ onSelectPersona, reset}) => {
  const [input, setInput] = useState('');
  const [sugerencias, setSugerencias] = useState([]);
  const [mostrarLista, setMostrarLista] = useState(false);

  // Limpia el campo cuando se activa `reset`
  useEffect(() => {
    if (reset) {
      setInput('');
      setSugerencias([]);
      setMostrarLista(false);
    }
  }, [reset]);

  useEffect(() => {
    const buscar = async () => {
      if (input.length >= 2) {
        try {
          const res = await fetch(`http://localhost:5001/api/personas-filtros?cedula_ruc=${input}&rol=cliente`);
          const data = await res.json();
          setSugerencias(data);
          setMostrarLista(true);
        } catch (error) {
          console.error('❌ Error al buscar personas');
          setSugerencias([]);
        }
      } else {
        setSugerencias([]);
        setMostrarLista(false);
      }
    };

    buscar();
  }, [input]);

  const handleSeleccion = (persona) => {
    setInput(`${persona.nombre} ${persona.apellido} - ${persona.cedula_ruc}`);
    setMostrarLista(false);
    setSugerencias([]);
    onSelectPersona(persona);
  };

  return (
    <div className="relative">
      <input
        type="text"
        className="border p-2 w-full rounded focus:outline-none focus:ring focus:border-green-500"
        placeholder="Buscar cliente por cédula o nombre"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onFocus={() => input.length >= 2 && setMostrarLista(true)}
      />

      {mostrarLista && sugerencias.length > 0 && (
        <ul className="absolute z-10 bg-white border border-gray-300 rounded w-full mt-1 max-h-48 overflow-y-auto shadow-lg">
          {sugerencias.map((persona) => (
            <li
              key={persona.id_persona}
              onClick={() => handleSeleccion(persona)}
              className="p-2 hover:bg-green-100 cursor-pointer"
            >
              {persona.nombre} {persona.apellido} - {persona.cedula_ruc}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AutocompletarPersonas;
