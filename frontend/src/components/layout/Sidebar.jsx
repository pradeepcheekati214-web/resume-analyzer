import { NavLink, Link } from 'react-router-dom';
import { FiHome, FiUser, FiFileText, FiX, FiUpload, FiTarget, FiCpu, FiMessageCircle } from 'react-icons/fi';
import { HiOutlineChartBar, HiOutlineSparkles } from 'react-icons/hi';
import clsx from 'clsx';

const NAV_ITEMS = [
  { to: '/home',                icon: FiHome,            label: 'Home' },
  { to: '/dashboard',           icon: HiOutlineChartBar, label: 'Dashboard' },
  { divider: true, label: 'AI Features' },
  { to: '/chatbot',             icon: FiMessageCircle,   label: 'AI Chatbot' },
  { to: '/job-match',           icon: FiTarget,          label: 'Job Match' },
  { to: '/interview/questions', icon: FiCpu,             label: 'Interview Prep' },
  { to: '/interview/history',   icon: HiOutlineChartBar, label: 'Interview History' },
  { divider: true, label: 'Account' },
  { to: '/profile',             icon: FiUser,            label: 'Profile' },
];

function SidebarContent({ onNavClick }) {
  return (
    <div className="flex flex-col flex-1 py-4 overflow-y-auto scrollbar-thin">
      {/* Logo (desktop only) */}
      <div className="hidden lg:flex items-center gap-2 px-4 mb-6">
        <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
          <FiFileText className="w-4 h-4 text-white" />
        </div>
        <span className="font-bold text-slate-900 text-sm">Resume Analyzer</span>
      </div>

      <nav className="flex-1 px-3 space-y-0.5">
        {NAV_ITEMS.map((item, i) => {
          if (item.divider) {
            return (
              <p key={i} className="text-xs font-semibold text-slate-400 uppercase tracking-wider px-3 pt-4 pb-1.5">
                {item.label}
              </p>
            );
          }
          const Icon = item.icon;
          return (
            <NavLink key={item.to} to={item.to} onClick={onNavClick}
              className={({ isActive }) => clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors duration-150 no-underline',
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              )}>
              {({ isActive }) => (
                <>
                  <Icon className={clsx('w-4 h-4 shrink-0', isActive ? 'text-primary-600' : 'text-slate-400')} />
                  {item.label}
                </>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* CTA card */}
      <div className="px-4 mt-4">
        <div className="bg-gradient-to-br from-primary-600 to-secondary-600 rounded-xl p-4 text-white">
          <HiOutlineSparkles className="w-5 h-5 mb-2 opacity-90" />
          <p className="text-sm font-semibold">AI Resume Coach</p>
          <p className="text-xs opacity-75 mt-0.5 mb-3">Upload your resume and get AI-powered improvements</p>
          <NavLink to="/home" onClick={onNavClick}
            className="block w-full text-center bg-white text-primary-700 text-xs font-semibold py-1.5 rounded-lg hover:bg-primary-50 no-underline transition-colors">
            Upload Resume
          </NavLink>
        </div>
      </div>
    </div>
  );
}

function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {/* Desktop */}
      <aside className="hidden lg:flex flex-col w-56 bg-white border-r border-slate-100 shrink-0">
        <SidebarContent />
      </aside>

      {/* Mobile drawer */}
      <aside className={clsx(
        'fixed inset-y-0 left-0 z-30 w-64 bg-white border-r border-slate-100 flex flex-col lg:hidden transform transition-transform duration-300',
        isOpen ? 'translate-x-0' : '-translate-x-full'
      )}>
        <div className="flex items-center justify-between px-4 h-16 border-b border-slate-100">
          <Link to="/home" className="flex items-center gap-2 no-underline" onClick={onClose}>
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <FiFileText className="w-4 h-4 text-white" />
            </div>
            <span className="font-bold text-slate-900">Resume Analyzer</span>
          </Link>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-slate-100">
            <FiX className="w-5 h-5" />
          </button>
        </div>
        <SidebarContent onNavClick={onClose} />
      </aside>
    </>
  );
}

export default Sidebar;
