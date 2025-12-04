// utils/validaciones.js

// Validar cédula ecuatoriana
export function validarCedula(cedula) {
  if (!/^\d{10}$/.test(cedula)) return false;

  const provincia = parseInt(cedula.substring(0, 2), 10);
  if (provincia < 1 || provincia > 24) return false;

  const digitoVerificador = parseInt(cedula.charAt(9));
  let suma = 0;

  for (let i = 0; i < 9; i++) {
    let valor = parseInt(cedula.charAt(i));
    if (i % 2 === 0) {
      valor *= 2;
      if (valor > 9) valor -= 9;
    }
    suma += valor;
  }

  const modulo = suma % 10;
  const resultado = modulo === 0 ? 0 : 10 - modulo;
  return resultado === digitoVerificador;
}

// Validar RUC ecuatoriano (personas naturales, públicas o jurídicas)
export function validarRuc(ruc) {
  if (!/^\d{13}$/.test(ruc)) return false;

  const cedulaParte = ruc.slice(0, 10);
  const sufijo = ruc.slice(10);

  // El RUC debe tener como prefijo una cédula válida y terminar en "001"
  return validarCedula(cedulaParte) && sufijo === '001';
}

export function validarTelefonoEcuatoriano(telefono) {
  return /^09\d{8}$/.test(telefono);
}