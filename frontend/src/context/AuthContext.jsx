import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { authService } from '@/services/authService';
import { STORAGE_KEYS } from '@/utils/constants';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const navigate = useNavigate();

  // Initialise from localStorage
  useEffect(() => {
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
    const storedUser = localStorage.getItem(STORAGE_KEYS.USER);
    if (token && storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch {
        localStorage.removeItem(STORAGE_KEYS.USER);
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await authService.login(email, password);
    const profile = data.user || (await authService.getProfile());
    setUser(profile);
    localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(profile));
    toast.success(`Welcome back, ${profile.full_name || profile.email}!`);
    navigate('/home');
    return data;
  }, [navigate]);

  const register = useCallback(async (formData) => {
    const data = await authService.register(formData);
    toast.success('Account created! Please log in.');
    navigate('/login');
    return data;
  }, [navigate]);

  const logout = useCallback(async () => {
    await authService.logout();
    setUser(null);
    toast.success('Signed out successfully.');
    navigate('/login');
  }, [navigate]);

  const updateUser = useCallback((updates) => {
    setUser((prev) => {
      const updated = { ...prev, ...updates };
      localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(updated));
      return updated;
    });
  }, []);

  return (
    <AuthContext.Provider value={{ user, isLoading, isAuthenticated: !!user, login, register, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider');
  return ctx;
}
