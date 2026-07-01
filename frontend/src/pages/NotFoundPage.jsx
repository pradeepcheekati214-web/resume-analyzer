import { Link } from 'react-router-dom';
import { FiHome, FiAlertCircle } from 'react-icons/fi';

function NotFoundPage() {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center p-4">
      <div className="text-center max-w-md">
        <div className="w-20 h-20 bg-primary-50 rounded-3xl flex items-center justify-center mx-auto mb-6">
          <FiAlertCircle className="w-10 h-10 text-primary-400" />
        </div>
        <h1 className="text-7xl font-extrabold text-primary-600 mb-2">404</h1>
        <h2 className="text-2xl font-bold text-slate-900 mb-2">Page not found</h2>
        <p className="text-slate-500 mb-8">
          The page you're looking for doesn't exist or has been moved.
        </p>
        <Link to="/home" className="btn-primary btn-lg">
          <FiHome className="w-4 h-4" /> Go Home
        </Link>
      </div>
    </div>
  );
}

export default NotFoundPage;
