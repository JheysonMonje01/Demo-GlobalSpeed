import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App.jsx';
import { ToastContainer } from 'react-toastify';
import { UserProvider } from './components/UserContext.jsx'; // Asegúrate de tener este archivo creado
import { EmpresaProvider } from './components/EmpresaContext';


ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <UserProvider>
      <EmpresaProvider> {/* Contexto de empresa disponible globalmente */}
        <App />
        <ToastContainer
          position="top-right"
          autoClose={3000}
          hideProgressBar={false}
          newestOnTop={false}
          closeOnClick
          pauseOnFocusLoss
          draggable
          pauseOnHover
          style={{
            fontSize: "13px",
            padding: "6px 1px",
            minHeight: "30px",
            lineHeight: "1.1",
            width: "100px"
          }}
          theme="colored"
        />
      </EmpresaProvider>
    </UserProvider>
  </React.StrictMode>
);
