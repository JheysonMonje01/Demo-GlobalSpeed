import { NavLink, useLocation } from 'react-router-dom';
import {
  FaUserCog, FaUsers, FaFileContract, FaNetworkWired,
  FaChevronDown, FaAngleDoubleRight, FaBuilding, FaServer,FaList,
  FaTools, FaClipboardList, FaEye, FaCoins, FaHome, FaUserPlus,FaWifi, FaEthernet, FaCogs, FaClipboardCheck
} from 'react-icons/fa';
import { MdAccountBalanceWallet } from 'react-icons/md';
import { Menu, ScrollText  } from 'lucide-react';
import { useEffect, useState, useContext } from 'react';
import { EmpresaContext } from './EmpresaContext';
import { MdManageHistory } from "react-icons/md";
import { IoDocumentTextOutline } from "react-icons/io5";
import { CgDollar } from "react-icons/cg";

const SidebarTecnico = ({ isCollapsed, toggleCollapse, isMobile, showMobileSidebar, closeMobileSidebar }) => {
  const location = useLocation();
  const [openMenu, setOpenMenu] = useState(null);

  const { empresa, logoPreview } = useContext(EmpresaContext);

  const toggleSubmenu = (menu) => {
    setOpenMenu((prev) => (prev === menu ? null : menu));
  };

  const isParentActive = (submenu) =>
    submenu?.some((sub) => location.pathname === sub.path);

  const sections = [
    {
      title: 'General',
      items: [
        { title: 'Dashboard', icon: FaHome, path: '/tecnico/dashboard' },
    
        //{ title: 'Configuración', icon: FaTools, path: '/admin/configuracion' },
        //{ title: 'Cobertura', icon: FaWifi, path: '/admin/cobertura' },
      ]
    },
    {
      title: 'Gestión',
      items: [
        {
          title: 'Clientes', icon: FaUsers, path: '/tecnico/clientes'
        },
        { title: 'Planes', icon: FaClipboardList, path: '/tecnico/planes' },
        {
          title: 'Red / Equipos', icon: FaNetworkWired, submenu: [
            { title: 'NAPs', icon: FaAngleDoubleRight, path: '/tecnico/red/naps' },
          ]
        },
        { title: 'Ordenes Instalaciones', icon: IoDocumentTextOutline, path: '/tecnico/ordenes' },
        { title: 'Monitoreo', icon: FaEye, path: '/tecnico/monitoreo' },
      ]
    },
  ];

  useEffect(() => {
    const found = sections.flatMap(s => s.items).find(item =>
      item.submenu?.some(sub => sub.path === location.pathname)
    );
    if (found) setOpenMenu(found.title);
    else setOpenMenu(null);
  }, [location.pathname]);

  return (
    <aside
      className={`bg-green-800 text-white h-screen fixed top-0 left-0 z-40 transition-all duration-300 shadow-lg overflow-y-auto
        ${isMobile ? (showMobileSidebar ? 'translate-x-0 w-64' : '-translate-x-full') : (isCollapsed ? 'w-15' : 'w-63')}`}
    >
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {!isCollapsed && (
              <img
                src={logoPreview || "/imagenes/logo-default.png"}
                alt="Logo"
                className="h-8 w-8 object-cover rounded-full"
              />
            )}
            {!isCollapsed && (
              <h1 className="text-lg font-bold text-green-700">
                {empresa?.nombre || "N/N"}
              </h1>
            )}
          </div>
          {!isMobile && (
            <button onClick={toggleCollapse} className="text-green-700">
              <Menu size={20} />
            </button>
          )}
        </div>
      </div>

      {/* Navegación */}
      <nav className="px-2 pt-4 text-[15px] space-y-1">
        {sections.map((section, sIdx) => (
          <div key={sIdx} className="space-y-1">
            {!isCollapsed && (
              <h4 className="text-xs font-semibold text-white/70 px-3 pt-4 pb-1 tracking-wide">
                {section.title}
              </h4>
            )}
            {section.items.map((item, index) => {
              const Icon = item.icon;
              const activeSub = isParentActive(item.submenu);
              return (
                <div key={index} className="relative">
                  {!item.submenu ? (
                    <NavLink
                      to={item.path}
                      className={({ isActive }) =>
                        `flex items-center gap-3 px-3 py-2 rounded-md transition-all relative
                        ${isActive ? 'bg-green-200/30 font-medium' : 'hover:bg-green-700/70'}`
                      }
                      onClick={isMobile ? closeMobileSidebar : undefined}
                    >
                      {({ isActive }) => (
                        <>
                          {(isActive || activeSub) && (
                            <div className="absolute left-0 top-0 h-full w-1 bg-green-400 rounded-r-md" />
                          )}
                          <Icon className="text-base" />
                          {!isCollapsed && <span className="text-sm">{item.title}</span>}
                        </>
                      )}
                    </NavLink>
                  ) : (
                    <>
                      <div
                        onClick={() => toggleSubmenu(item.title)}
                        className={`flex items-center justify-between gap-2 px-3 py-2 rounded-md cursor-pointer transition-all relative
                          ${openMenu === item.title || activeSub ? 'bg-green-700' : 'hover:bg-green-700/70'}`}
                      >
                        {(openMenu === item.title || activeSub) && (
                          <span className="absolute left-0 top-0 h-full w-1 bg-green-400 rounded-r-md" />
                        )}
                        <div className="flex items-center gap-3">
                          <Icon className="text-base" />
                          {!isCollapsed && <span className="text-sm">{item.title}</span>}
                        </div>
                        {!isCollapsed && (
                          <FaChevronDown
                            className={`transition-transform duration-300 text-xs ${openMenu === item.title ? 'rotate-180' : ''}`}
                          />
                        )}
                      </div>
                      <div
                        className={`transition-all duration-300 overflow-hidden
                        ${openMenu === item.title ? 'max-h-[500px]' : 'max-h-0'}`}
                      >
                        {!isCollapsed && (
                          <ul className="ml-9 mt-1 space-y-1 text-sm">
                            {item.submenu.map((sub, i) => {
                              const SubIcon = sub.icon || FaAngleDoubleRight;
                              const isActive = location.pathname === sub.path;
                              return (
                                <li key={i} className="relative">
                                  <NavLink
                                    to={sub.path}
                                    className={`flex items-center gap-2 relative px-2 py-2 rounded-md transition-all
                                      ${isActive ? 'bg-green-200/30 font-medium text-white' : 'hover:bg-green-700/70 text-white/90'}`}
                                    onClick={isMobile ? closeMobileSidebar : undefined}
                                  >
                                    {isActive && (
                                      <span className="absolute left-0 top-0 h-full w-1 bg-green-400 rounded-r-md" />
                                    )}
                                    <SubIcon className="text-sm" />
                                    <span>{sub.title}</span>
                                  </NavLink>
                                </li>
                              );
                            })}
                          </ul>
                        )}
                      </div>
                    </>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </nav>
    </aside>
  );
};

export default SidebarTecnico;
