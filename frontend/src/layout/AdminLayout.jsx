import React, { useState, useEffect } from "react";
import Sidebar from "../components/Sidebar";
import Navbar from "../components/Navbar";
import { Outlet } from "react-router-dom";

const AdminLayout = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [showMobileSidebar, setShowMobileSidebar] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };

    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  const toggleSidebar = () => {
    if (isMobile) {
      setShowMobileSidebar(!showMobileSidebar);
    } else {
      setIsCollapsed(!isCollapsed);
    }
  };

  const closeMobileSidebar = () => {
    if (isMobile) setShowMobileSidebar(false);
  };

  return (
    <div className="flex min-h-screen bg-gray-100">
      {/* Sidebar */}
      <Sidebar
        isCollapsed={isCollapsed}
        toggleCollapse={toggleSidebar}
        isMobile={isMobile}
        showMobileSidebar={showMobileSidebar}
        closeMobileSidebar={closeMobileSidebar}
      />

      {/* Fondo oscuro móvil */}
      {isMobile && showMobileSidebar && (
        <div
          className="fixed inset-0 bg-black opacity-50 z-30"
          onClick={closeMobileSidebar}
        />
      )}

      {/* Contenedor derecho */}
      <div
        className={`flex flex-col transition-all duration-300 w-full ${
          isMobile ? "ml-0" : isCollapsed ? "ml-15" : "ml-57"
        }`}
      >
        <Navbar toggleSidebar={toggleSidebar} />
        <main className="flex-1 p-6 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default AdminLayout;
