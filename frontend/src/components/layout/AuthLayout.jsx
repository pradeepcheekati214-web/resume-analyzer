import { Outlet, Link } from 'react-router-dom';
import { FiFileText } from 'react-icons/fi';

function AuthLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-900 via-primary-800 to-secondary-700 flex flex-col items-center justify-center p-4 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-600 rounded-full opacity-20" />
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-secondary-600 rounded-full opacity-20" />
      </div>

      <Link to="/login" className="flex items-center gap-3 mb-8 no-underline group z-10">
        <div className="w-12 h-12 bg-white rounded-2xl flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-200">
          <FiFileText className="w-6 h-6 text-primary-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Resume Analyzer</h1>
          <p className="text-primary-200 text-sm">AI-Powered ATS Optimization</p>
        </div>
      </Link>

      <div className="w-full max-w-md z-10"><Outlet /></div>

      <p className="mt-8 text-primary-300 text-xs text-center z-10">
        © {new Date().getFullYear()} Resume Analyzer. All rights reserved.
      </p>
    </div>
  );
}

export default AuthLayout;
