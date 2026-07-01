import { Link } from 'react-router-dom';
import { useState, useRef, useEffect } from 'react';
import { HiMenu, HiBell, HiChevronDown } from 'react-icons/hi';
import { FiFileText } from 'react-icons/fi';
import { useAuth } from '@/context/AuthContext';
import { getInitials } from '@/utils/formatters';

function Navbar({ onMenuClick }) {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    const handler = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  return (
    <header className="sticky top-0 z-10 bg-white border-b border-slate-100 shadow-sm">
      <div className="page-container">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <button onClick={onMenuClick} className="lg:hidden p-2 rounded-lg hover:bg-slate-100" aria-label="Open menu">
              <HiMenu className="w-5 h-5" />
            </button>
            <Link to="/home" className="flex items-center gap-2 no-underline">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <FiFileText className="w-4 h-4 text-white" />
              </div>
              <span className="font-bold text-slate-900 hidden sm:block">Resume Analyzer</span>
            </Link>
          </div>

          <div className="flex items-center gap-2">
            <button className="p-2 rounded-lg hover:bg-slate-100 relative" aria-label="Notifications">
              <HiBell className="w-5 h-5 text-slate-500" />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-primary-500 rounded-full" />
            </button>

            <div className="relative" ref={ref}>
              <button
                onClick={() => setOpen((o) => !o)}
                className="flex items-center gap-2 pl-2 pr-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                <div className="w-8 h-8 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-semibold select-none">
                  {getInitials(user?.full_name || user?.email || 'U')}
                </div>
                <div className="hidden sm:block text-left">
                  <p className="text-sm font-medium text-slate-800 leading-none">{user?.full_name || 'User'}</p>
                  <p className="text-xs text-slate-400 mt-0.5 truncate max-w-[120px]">{user?.email}</p>
                </div>
                <HiChevronDown className={`w-4 h-4 text-slate-400 transition-transform duration-150 ${open ? 'rotate-180' : ''}`} />
              </button>

              {open && (
                <div className="absolute right-0 top-full mt-1.5 w-48 bg-white rounded-xl shadow-lg border border-slate-100 py-1 animate-fade-in z-50">
                  <Link to="/profile" onClick={() => setOpen(false)} className="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 no-underline">Profile Settings</Link>
                  <Link to="/dashboard" onClick={() => setOpen(false)} className="flex items-center gap-2 px-4 py-2.5 text-sm text-slate-700 hover:bg-slate-50 no-underline">My Dashboard</Link>
                  <div className="border-t border-slate-100 my-1" />
                  <button onClick={() => { setOpen(false); logout(); }} className="w-full text-left px-4 py-2.5 text-sm text-danger-600 hover:bg-danger-50 transition-colors">
                    Sign Out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Navbar;
