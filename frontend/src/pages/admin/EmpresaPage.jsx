import React, { useEffect, useState, useContext } from 'react';
import {
  FaEnvelope, FaPhone, FaMapMarkerAlt, FaIdCard,
  FaUserTie, FaBuilding, FaUpload,FaPen, FaTrashAlt 
} from 'react-icons/fa';
import { Trash2} from 'lucide-react';
import { toast } from 'react-toastify';
import { EmpresaContext } from '../../components/EmpresaContext';
import ModalAgregarTelefono from '../../components/ModalAgregarTelefono';
import ModalAgregarCorreo from '../../components/ModalAgregarCorreo';
import ModalAgregarInformacionPago from '../../components/ModalAgregarInformacionPago';
import ModalEditarInfoPago from '../../components/ModalEditarInfoPago';
import Swal from 'sweetalert2';
import withReactContent from 'sweetalert2-react-content';


const EmpresaPage = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [empresa, setEmpresa] = useState({});
  const [logoPreview, setLogoPreview] = useState(null);
  const { cargarEmpresa } = useContext(EmpresaContext);
  const [mostrarModalTelefono, setMostrarModalTelefono] = useState(false);
  const [mostrarModalCorreo, setMostrarModalCorreo] = useState(false);
  const [mostrarModalPago, setMostrarModalPago] = useState(false);
  const [metodosPago, setMetodosPago] = useState([]); 
  const [informacionPago, setInformacionPago] = useState([]);
  const [modalEditar, setModalEditar] = useState(false);
const [idSeleccionado, setIdSeleccionado] = useState(null);




  const { fecha_creacion, fecha_modificacion, id_empresa, ...payload } = empresa;
  const fetchInformacionPago = async () => {
  try {
    const res = await fetch("http://localhost:5008/informacion_metodos_pago");
    const data = await res.json();
    setInformacionPago(data);
  } catch (error) {
    console.error("Error al obtener información de métodos de pago", error);
  }
};

useEffect(() => {
  fetchInformacionPago();
}, []);



const MySwal = withReactContent(Swal);

const handleEliminar = async (id) => {
  const result = await MySwal.fire({
    title: '¿Estás seguro?',
    text: 'Esta acción eliminará el método de pago.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#d33',
    cancelButtonColor: '#3085d6',
    confirmButtonText: 'Sí, eliminar',
    cancelButtonText: 'Cancelar',
  });

  if (result.isConfirmed) {
    try {
      const res = await fetch(`http://localhost:5008/informacion_metodos_pago/${id}`, {
        method: 'DELETE',
      });

      if (!res.ok) throw new Error('Error al eliminar');

      Swal.fire('¡Eliminado!', 'El método ha sido eliminado.', 'success');
      await fetchInformacionPago(); // ✅ aquí va la función que sí tienes declarada
    } catch (err) {
      console.error(err);
      Swal.fire('Error', 'No se pudo eliminar el método de pago.', 'error');
    }
  }
};




  useEffect(() => {
    const fetchEmpresa = async () => {
      try {
        const res = await fetch("http://localhost:5002/api/empresa");
        const data = await res.json();

        if (Array.isArray(data) && data.length > 0) {
          const emp = data[0];
          setEmpresa({
            ...emp,
            telefonos: emp.telefonos || [],
            correos: emp.correos || [],
          });

          if (emp.logo) {
            setLogoPreview(`data:image/jpeg;base64,${emp.logo}`);
          }
        } else {
          toast.error("No se encontró la empresa.");
        }
      } catch (err) {
        toast.error("Error al obtener la información de la empresa");
        console.error(err);
      }
    };

    fetchEmpresa();
  }, []);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setEmpresa(prev => ({ ...prev, [name]: value }));
  };

  const [logoFile, setLogoFile] = useState(null); // nuevo estado

const handleFileChange = (e) => {
  const file = e.target.files[0];
  if (!file) return;

  setLogoFile(file); // se usará en FormData

  const reader = new FileReader();
  reader.onloadend = () => {
    const base64Logo = reader.result.split(',')[1];
    setEmpresa(prev => ({ ...prev, logo: base64Logo }));
    setLogoPreview(reader.result);
  };
  reader.readAsDataURL(file);
};

  const handleTelefonoChange = (index, value) => {
    // Solo permite dígitos
    if (!/^\d*$/.test(value)) return;

    const nuevos = [...empresa.telefonos];

    // Validar duplicados (ignorar el mismo índice)
    const existe = nuevos.some((t, i) => t.telefono === value && i !== index);
    if (existe) {
      toast.error("Este número ya está registrado");
      return;
    }

    nuevos[index].telefono = value;
    setEmpresa({ ...empresa, telefonos: nuevos });
  };

  const validarEmail = (email) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

const handleCorreoChange = (index, value) => {
  const nuevos = [...empresa.correos];

  // Validación de formato
  if (value && !validarEmail(value)) {
    toast.error("Correo inválido");
    return;
  }

  // Validar duplicados (ignorar el mismo índice)
  const existe = nuevos.some((c, i) => c.correo === value && i !== index);
  if (existe) {
    toast.error("Este correo ya está registrado");
    return;
  }

  nuevos[index].correo = value;
  setEmpresa({ ...empresa, correos: nuevos });
};

  const agregarTelefono = () => {
    setEmpresa(prev => ({
      ...prev,
      telefonos: [...(prev.telefonos || []), { numero: "" }]
    }));
  };

  const agregarCorreo = () => {
    setEmpresa(prev => ({
      ...prev,
      correos: [...(prev.correos || []), { correo: "" }]
    }));
  };

  const eliminarTelefono = (index) => {
  const actuales = empresa.telefonos || [];
  if (actuales.length <= 1) {
    toast.error("Debe haber al menos un número de teléfono.");
    return;
  }

  const nuevos = actuales.filter((_, i) => i !== index);
  setEmpresa({ ...empresa, telefonos: nuevos });
};

const eliminarCorreo = (index) => {
  const actuales = empresa.correos || [];
  if (actuales.length <= 1) {
    toast.error("Debe haber al menos un correo.");
    return;
  }

  const nuevos = actuales.filter((_, i) => i !== index);
  setEmpresa({ ...empresa, correos: nuevos });
};


  const handleSubmit = async () => {
  try {
    const formData = new FormData();

    formData.append('nombre', empresa.nombre);
    formData.append('representante', empresa.representante);
    formData.append('ruc', empresa.ruc);
    formData.append('direccion', empresa.direccion);

    // Solo si seleccionó un nuevo logo
    if (logoFile) {
      formData.append('logo', logoFile);
    }

    // Estos campos deben serializarse como JSON
    formData.append('telefonos', JSON.stringify(empresa.telefonos));
    formData.append('correos', JSON.stringify(empresa.correos));

    const res = await fetch(`http://localhost:5002/api/empresa/${empresa.id_empresa}`, {
      method: 'PUT',
      body: formData, // sin headers manuales
    });

    const result = await res.json();

    if (res.ok) {
      toast.success("Empresa actualizada correctamente");
      setIsEditing(false);
      await cargarEmpresa();
    } else {
      toast.error(result.message || "Error al actualizar la empresa");
    }
  } catch (error) {
    toast.error("Error al conectar con el servidor");
    console.error(error);
  }
};


  const inputStyle = `mt-1 w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-green-400`;

  return (
    <div className="min-h-[calc(92vh-4rem)] w-full bg-white shadow rounded-lg p-6 md:p-8 text-[15px]">
      <div className="flex justify-between items-center border-b pb-4 mb-6">
        <h2 className="text-2xl font-semibold text-gray-800">Información de la Empresa</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-700 font-medium">Modo de edición</span>
          <div
            onClick={() => setIsEditing(!isEditing)}
            className={`w-12 h-6 flex items-center rounded-full p-1 cursor-pointer transition duration-300 ${isEditing ? 'bg-green-500' : 'bg-gray-300'}`}
          >
            <div
              className={`bg-white w-4 h-4 rounded-full shadow-md transform transition-transform duration-300 ${isEditing ? 'translate-x-6' : 'translate-x-0'}`}
            />
          </div>
        </div>
        {/* Botón agregar info pago */}
  {isEditing && (
    <button
      onClick={() => setMostrarModalPago(true)}
      className="bg-green-600 hover:bg-green-700 text-white text-sm px-4 py-2 rounded-md shadow"
    >
      + Añadir información de pago
    </button>
  )}

      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-green-50 p-6 rounded-lg flex flex-col items-center">
          <div className="w-28 h-28 rounded-full overflow-hidden border shadow">
            <img src={logoPreview || "/imagenes/logo-default.png"} alt="Logo" className="object-cover w-full h-full" />
          </div>
          <h3 className="mt-4 text-lg font-semibold text-gray-900">{empresa.nombre || "N/N"}</h3>
          <p className="text-sm text-gray-600">Proveedor de Servicios de Internet</p>

          {isEditing && (
            <>
              <label className="mt-3 text-sm font-medium text-gray-800">Cambiar logo</label>
              <label className="mt-1 flex items-center gap-2 bg-green-200 text-green-900 px-3 py-1 rounded cursor-pointer hover:bg-green-300 transition text-sm">
                <FaUpload /> Seleccionar archivo
                <input type="file" accept="image/*" onChange={handleFileChange} className="hidden" />
              </label>
            </>
          )}
        </div>

        <div className="md:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaBuilding /> Nombre de la empresa</label>
            <input
              name="nombre"
              value={empresa.nombre || ''}
              onChange={handleChange}
              disabled={!isEditing}
              className={`${inputStyle} ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
            />
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaUserTie /> Representante Legal</label>
            <input
              name="representante"
              value={empresa.representante || ''}
              onChange={handleChange}
              disabled={!isEditing}
              className={`${inputStyle} ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
            />
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaIdCard /> RUC</label>
            <input
              name="ruc"
              value={empresa.ruc || ''}
              onChange={handleChange}
              disabled={!isEditing}
              className={`${inputStyle} ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
            />
          </div>
          <div>
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaMapMarkerAlt /> Dirección</label>
            <input
              name="direccion"
              value={empresa.direccion || ''}
              onChange={handleChange}
              disabled={!isEditing}
              className={`${inputStyle} ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
            />
          </div>

          {/* Teléfonos múltiples */}
          <div className="md:col-span-2">
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaPhone /> Teléfonos</label>
            {empresa.telefonos?.map((tel, i) => (
              <div key={i} className="flex gap-2 mt-1 items-center">
                <input
                  value={tel.telefono || ''}
                  onChange={e => handleTelefonoChange(i, e.target.value)}
                  disabled={!isEditing}
                  className={`${inputStyle} flex-1 ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
                  placeholder={`Teléfono ${i + 1}`}
                />
                {isEditing && (
                  <button
                    onClick={() => eliminarTelefono(i)}
                    className="p-1 text-red-600 hover:text-red-800"
                    title="Eliminar teléfono"
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>
            ))}


            {isEditing && (
              <button onClick={() => setMostrarModalTelefono(true)} className="text-sm mt-1 text-green-700 hover:underline">
                + Añadir teléfono
              </button>
            )}
          </div>

          {/* Correos múltiples */}
          <div className="md:col-span-2">
            <label className="flex items-center gap-2 text-sm font-bold text-black"><FaEnvelope /> Correos</label>
            {empresa.correos?.map((corr, i) => (
              <div key={i} className="flex gap-2 mt-1 items-center">
                <input
                  value={corr.correo || ''}
                  onChange={e => handleCorreoChange(i, e.target.value)}
                  disabled={!isEditing}
                  className={`${inputStyle} flex-1 ${isEditing ? 'bg-white' : 'bg-gray-100'}`}
                  placeholder={`Correo ${i + 1}`}
                />
                {isEditing && (
                  <button
                    onClick={() => eliminarCorreo(i)}
                    className="p-1 text-red-600 hover:text-red-800"
                    title="Eliminar correo"
                  >
                    <Trash2 size={18} />
                  </button>
                )}
              </div>
            ))}


            {isEditing && (
              <button onClick={() => setMostrarModalCorreo(true)} className="text-sm mt-1 text-green-700 hover:underline">
                + Añadir correo
              </button>

            )}
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
      {/* INFORMACIÓN DE PAGO EN TARJETAS */}
<div className="mt-10">
  <h2 className="text-xl font-semibold text-gray-800 mb-4">Información de Pago</h2>

  {informacionPago.length === 0 ? (
    <p className="text-gray-600">No hay información de métodos de pago registrada.</p>
  ) : (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {informacionPago && informacionPago.map((item, index) => (
        <div
  key={index}
  className="relative border border-gray-200 rounded-2xl shadow-md p-6 bg-white hover:shadow-lg transition duration-300"
>
          {/* Acciones */}
        
<div className="absolute top-3 right-3 flex space-x-3">
  <button
    onClick={() => {
    setIdSeleccionado(item.id_info); // o como se llame el campo
    setModalEditar(true);
  }}
    className="text-blue-600 hover:text-blue-800 transition"
    title="Editar"
  >
    <FaPen size={16} />
  </button>
  <button
    onClick={() => handleEliminar(item.id_info)}
    className="text-red-600 hover:text-red-800 transition"
    title="Eliminar"
  >
    <FaTrashAlt size={16} />
  </button>
</div>



          {/* Información */}
          <p className="mb-2"><span className="font-semibold">Entidad financiera:</span> {item.entidad_financiera}</p>
          <p className="mb-2"><span className="font-semibold">Tipo de cuenta:</span> {item.tipo_cuenta}</p>
          <p className="mb-2"><span className="font-semibold">Número de cuenta:</span> {item.numero_cuenta}</p>
          <p className="mb-2"><span className="font-semibold">Beneficiario:</span> {item.nombre_beneficiario}</p>
          <p className="mb-2"><span className="font-semibold">Instrucciones:</span> {item.instrucciones}</p>

          {/* Estado */}
          <div className="mt-3 flex items-center space-x-2">
            <span
              className={`h-3 w-3 rounded-full ${
                item.estado ? 'bg-green-500' : 'bg-red-500'
              }`}
            ></span>
            <span className="text-sm text-gray-800 font-medium">
              {item.estado ? 'Activo' : 'Inactivo'}
            </span>
          </div>
        </div>
      ))}
    </div>
  )}
</div>


      <ModalAgregarTelefono
        visible={mostrarModalTelefono}
        onClose={() => setMostrarModalTelefono(false)}
        idEmpresa={empresa.id_empresa}
        telefonosExistentes={empresa.telefonos || []}
        onSuccess={async () => {
          const res = await fetch("http://localhost:5002/api/empresa");
          const data = await res.json();
          if (data.length > 0) {
            setEmpresa(prev => ({
              ...data[0],
              telefonos: data[0].telefonos || [],
              correos: data[0].correos || [],
            }));
          }
        }}
      />

      <ModalAgregarCorreo
  visible={mostrarModalCorreo}
  onClose={() => setMostrarModalCorreo(false)}
  idEmpresa={empresa.id_empresa}
  correosExistentes={empresa.correos || []}
  onSuccess={async () => {
    const res = await fetch("http://localhost:5002/api/empresa");
    const data = await res.json();
    if (data.length > 0) {
      setEmpresa({
        ...data[0],
        telefonos: data[0].telefonos || [],
        correos: data[0].correos || [],
      });
    }
  }}
/>
{mostrarModalPago && (
  <ModalAgregarInformacionPago
    onClose={() => setMostrarModalPago(false)}
    onSuccess={fetchInformacionPago}
  />
)}
{modalEditar && (
  <ModalEditarInfoPago
    idInfo={idSeleccionado}
    onClose={() => setModalEditar(false)}
    onSuccess={fetchInformacionPago}
  />
)}



    </div>
  );
};

export default EmpresaPage;
