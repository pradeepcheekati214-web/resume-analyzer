import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import LoadingSpinner from './LoadingSpinner';

function PublicRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <div className="min-h-screen flex items-center justify-center bg-slate-50"><LoadingSpinner size="lg" /></div>;
  if (isAuthenticated) return <Navigate to="/home" replace />;
  return <Outlet />;
}

export default PublicRoute;
