import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { FiMail, FiLock, FiUser, FiEye, FiEyeOff } from 'react-icons/fi';
import { useAuth } from '@/context/AuthContext';
import { checkPasswordStrength } from '@/utils/validators';
import LoadingSpinner from '@/components/common/LoadingSpinner';

function RegisterPage() {
  const { register: registerUser } = useAuth();
  const [showPw, setShowPw] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [serverError, setServerError] = useState('');
  const [passwordValue, setPasswordValue] = useState('');

  const { register, handleSubmit, watch, formState: { errors } } = useForm();
  const pwStrength = checkPasswordStrength(passwordValue);

  const onSubmit = async (data) => {
    setIsLoading(true);
    setServerError('');
    try {
      await registerUser({
        email: data.email,
        password: data.password,
        full_name: data.full_name,
      });
    } catch (err) {
      setServerError(err.response?.data?.detail || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl p-8 animate-slide-up">
      <h2 className="text-2xl font-bold text-slate-900 mb-1">Create an account</h2>
      <p className="text-slate-500 text-sm mb-6">Start analyzing your resume for free</p>

      {serverError && (
        <div className="mb-4 px-4 py-3 rounded-lg bg-danger-50 border border-danger-200 text-danger-700 text-sm">
          {serverError}
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)} noValidate className="space-y-4">
        <div>
          <label className="label" htmlFor="full_name">Full name</label>
          <div className="relative">
            <FiUser className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input id="full_name" type="text" placeholder="John Doe"
              className={`input pl-10 ${errors.full_name ? 'input-error' : ''}`}
              {...register('full_name', { required: 'Full name is required', minLength: { value: 2, message: 'Name must be at least 2 characters' } })}
            />
          </div>
          {errors.full_name && <p className="error-message">{errors.full_name.message}</p>}
        </div>

        <div>
          <label className="label" htmlFor="email">Email address</label>
          <div className="relative">
            <FiMail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input id="email" type="email" placeholder="you@example.com"
              className={`input pl-10 ${errors.email ? 'input-error' : ''}`}
              {...register('email', {
                required: 'Email is required',
                pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Invalid email address' },
              })}
            />
          </div>
          {errors.email && <p className="error-message">{errors.email.message}</p>}
        </div>

        <div>
          <label className="label" htmlFor="password">Password</label>
          <div className="relative">
            <FiLock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input id="password" type={showPw ? 'text' : 'password'} placeholder="Min. 8 characters"
              className={`input pl-10 pr-10 ${errors.password ? 'input-error' : ''}`}
              {...register('password', {
                required: 'Password is required',
                minLength: { value: 8, message: 'Password must be at least 8 characters' },
                onChange: (e) => setPasswordValue(e.target.value),
              })}
            />
            <button type="button" onClick={() => setShowPw((v) => !v)}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              aria-label={showPw ? 'Hide password' : 'Show password'}>
              {showPw ? <FiEyeOff className="w-4 h-4" /> : <FiEye className="w-4 h-4" />}
            </button>
          </div>
          {errors.password && <p className="error-message">{errors.password.message}</p>}
          {/* Strength bar */}
          {passwordValue && (
            <div className="mt-2">
              <div className="flex gap-1 mb-1">
                {[1,2,3,4,5].map((n) => (
                  <div key={n} className={`h-1 flex-1 rounded-full transition-colors duration-200
                    ${n <= pwStrength.score ? pwStrength.color : 'bg-slate-200'}`} />
                ))}
              </div>
              <p className="text-xs text-slate-500">{pwStrength.label}</p>
            </div>
          )}
        </div>

        <div>
          <label className="label" htmlFor="confirm_password">Confirm password</label>
          <div className="relative">
            <FiLock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input id="confirm_password" type={showPw ? 'text' : 'password'} placeholder="Repeat password"
              className={`input pl-10 ${errors.confirm_password ? 'input-error' : ''}`}
              {...register('confirm_password', {
                required: 'Please confirm your password',
                validate: (value) => value === watch('password') || 'Passwords do not match',
              })}
            />
          </div>
          {errors.confirm_password && <p className="error-message">{errors.confirm_password.message}</p>}
        </div>

        <button type="submit" disabled={isLoading} className="btn-primary w-full btn-lg mt-2">
          {isLoading ? <><LoadingSpinner size="sm" /> Creating account…</> : 'Create Account'}
        </button>
      </form>

      <p className="mt-6 text-center text-sm text-slate-500">
        Already have an account?{' '}
        <Link to="/login" className="text-primary-600 font-medium hover:text-primary-700">Sign in</Link>
      </p>
    </div>
  );
}

export default RegisterPage;
