import React, { useState, useEffect, useContext } from 'react';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {
  FaEnvelope, FaPhone, FaMapMarkerAlt, FaIdCard, FaUser, FaEdit, FaImage
} from 'react-icons/fa';
import { UserContext } from '../../components/UserContext';

const PerfilUsuarioPage = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [perfil, setPerfil] = useState({});
  const [fotoPreview, setFotoPreview] = useState(null);
  const id_usuario = localStorage.getItem('id_usuario');
  const id_rol = localStorage.getItem('rol');
  const [nombreRol, setNombreRol] = useState('');
  const { actualizarUsuario } = useContext(UserContext);

  useEffect(() => {
    const fetchPerfil = async () => {
      try {
        const response = await fetch(`http://localhost:5001/api/personas-filtros?id_usuario=${id_usuario}`);
        const data = await response.json();
        const perfilFiltrado = data.find(p => String(p.id_usuario) === String(id_usuario));
        if (perfilFiltrado) {
          setPerfil(perfilFiltrado);
          if (perfilFiltrado.foto) {
            setFotoPreview(`data:image/jpeg;base64,${perfilFiltrado.foto}`);
          }
        }


        if (id_rol) {
          const responseRol = await fetch(`http://localhost:5000/api/roles/filtrado?id_rol=${id_rol}`);
          const dataRol = await responseRol.json();
          if (Array.isArray(dataRol) && dataRol.length > 0) {
            setNombreRol(dataRol[0].nombre_rol);
          }
        }
      } catch (error) {
        console.error('Error al obtener perfil:', error);
      }
    };
    fetchPerfil();
  }, [id_usuario, id_rol]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setPerfil({ ...perfil, [name]: value });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64String = reader.result.split(',')[1];
      setPerfil({ ...perfil, foto: base64String });
      setFotoPreview(reader.result);
    };
    if (file) {
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async () => {
    const id_usuario = localStorage.getItem('id_usuario');

    const {
      cedula_ruc,
      fecha_creacion,
      fecha_modificacion,
      id_usuario: omitIdUsuario,
      id_persona: omitIdPersona,
      ...payload
    } = perfil;

    try {
      
      const response = await fetch(`http://localhost:5000/auth/usuarios-personas/${id_usuario}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      let result = {};
      try {
        result = await response.json();
      } catch (e) {
        result = {};
      }

      if (response.ok) {
        setIsEditing(false);
        await actualizarUsuario();
        toast.success('Perfil actualizado correctamente');
      } else {
        console.error("Errores de validación:", result.errores);
        toast.error('Error al actualizar perfil. Verifica los campos.');
      }
    } catch (error) {
      console.error('❌ Error en request PUT:', error);
      toast.error('Error al conectar con el servidor');
    }
  };

  const inputStyle = `mt-1 w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-green-400`;

  return (
    <div className="min-h-[calc(100vh-4rem)] w-full bg-white shadow rounded-lg p-6 md:p-8 text-[15px]">
      <div className="flex justify-between items-center border-b pb-4 mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">Mi Perfil</h2>
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 transition"
        >
          <FaEdit /> {isEditing ? 'Cancelar edición' : 'Actualizar perfil'}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-green-50 p-6 rounded-lg flex flex-col items-center">
          <div className="w-28 h-28 rounded-full overflow-hidden border shadow">
            <img
              src={fotoPreview ? fotoPreview : "/imagenes/perfil-none.avif"}
              alt="Perfil"
              className="object-cover w-full h-full"
            />
          </div>
          <h3 className="mt-4 text-lg font-semibold text-gray-900">{perfil.nombre} {perfil.apellido}</h3>
          <p className="text-sm text-gray-600">{nombreRol || 'Usuario'}</p>

          {isEditing && (
            <>
              <label className="mt-3 text-sm font-medium text-gray-800">Cambiar foto</label>
              <label className="mt-1 flex items-center gap-2 bg-green-300 text-green-800 px-3 py-1 rounded cursor-pointer hover:bg-green-200 transition text-sm">
                <FaImage /> Seleccionar imagen
                <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
              </label>
            </>
          )}
        </div>

        <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaIdCard /> Cédula</label>
            <input
              type="text"
              name="cedula_ruc"
              value={perfil.cedula_ruc || ''}
              disabled={!isEditing}
              className={`${inputStyle} ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
            />
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaUser /> Nombres</label>
            <input
              type="text"
              name="nombre"
              value={perfil.nombre || ''}
              onChange={handleChange}
              disabled={!isEditing}
              className={`${inputStyle} ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
            />
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaUser /> Apellidos</label>
            <input
              type="text"
              name="apellido"
              value={perfil.apellido || ''}
              onChange={handleChange}
              disabled={!isEditing}
              className={`${inputStyle} ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
            />
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaPhone /> Teléfono</label>
            <input
              type="text"
              name="telefono"
              value={perfil.telefono || ''}
              onChange={handleChange}
              disabled={!isEditing}
              className={`${inputStyle} ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
            />
          </div>
          <div className="md:col-span-2">
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaEnvelope /> Correo electrónico</label>
            <input
              type="email"
              name="correo"
              value={perfil.correo || ''}
              onChange={handleChange}
              disabled={!isEditing}
              className={`${inputStyle} ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
            />
          </div>
          <div className="md:col-span-2">
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaMapMarkerAlt /> Dirección domiciliaria</label>
            <input
              type="text"
              name="direccion_domiciliaria"
              value={perfil.direccion_domiciliaria || ''}
              onChange={handleChange}
              disabled={!isEditing}
              className={`${inputStyle} ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
            />
          </div>
        </div>
      </div>

      {isEditing && (
        <div className="mt-6 text-right">
          <button
            onClick={handleSubmit}
            className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-md shadow-sm"
          >
            Guardar Cambios
          </button>
        </div>
      )}
    </div>
  );
};

export default PerfilUsuarioPage;
