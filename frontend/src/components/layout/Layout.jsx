import { Outlet } from 'react-router-dom';
import { useState } from 'react';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  return (
    <div className="min-h-screen bg-slate-50 flex">
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 py-6 animate-fade-in">
          <div className="page-container"><Outlet /></div>
        </main>
        <footer className="py-4 border-t border-slate-100 bg-white">
          <div className="page-container text-center text-xs text-slate-400">
            © {new Date().getFullYear()} Resume Analyzer — Built with React &amp; FastAPI
          </div>
        </footer>
      </div>
      {sidebarOpen && (
        <div className="fixed inset-0 bg-black/40 z-20 lg:hidden" onClick={() => setSidebarOpen(false)} />
      )}
    </div>
  );
}

export default Layout;
