// ✅ Solo una vez en todo tu frontend (fuera de cualquier componente)
export const googleMapsOptions = {
  id: 'google-map-script',
  googleMapsApiKey: import.meta.env.VITE_GOOGLE_MAPS_API_KEY,
  libraries: ['places', 'geometry'],
  language: 'es',
  region: 'EC'
};
