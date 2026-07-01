import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import {
  FiUser, FiMail, FiSave, FiLock, FiEye, FiEyeOff,
  FiShield, FiTrash2, FiCamera
} from 'react-icons/fi';
import toast from 'react-hot-toast';
import { useAuth } from '@/context/AuthContext';
import { authService } from '@/services/authService';
import { getInitials, formatDate } from '@/utils/formatters';
import { checkPasswordStrength } from '@/utils/validators';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ConfirmModal from '@/components/common/ConfirmModal';

function ProfilePage() {
  const { user, updateUser } = useAuth();
  const [activeTab, setActiveTab]       = useState('profile');
  const [saving, setSaving]             = useState(false);
  const [showCurrent, setShowCurrent]   = useState(false);
  const [showNew, setShowNew]           = useState(false);
  const [pwValue, setPwValue]           = useState('');
  const [showDeleteModal, setShowDeleteModal] = useState(false);

  // Profile form
  const {
    register: regProfile,
    handleSubmit: handleProfile,
    reset: resetProfile,
    formState: { errors: profileErrors, isDirty: profileDirty },
  } = useForm({ defaultValues: { full_name: user?.full_name || '', email: user?.email || '' } });

  // Password form
  const {
    register: regPw,
    handleSubmit: handlePw,
    reset: resetPw,
    watch: watchPw,
    formState: { errors: pwErrors },
  } = useForm();

  useEffect(() => {
    resetProfile({ full_name: user?.full_name || '', email: user?.email || '' });
  }, [user, resetProfile]);

  const onSaveProfile = async (data) => {
    setSaving(true);
    try {
      const updated = await authService.updateProfile(data);
      updateUser(updated);
      toast.success('Profile updated!');
      resetProfile(data);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  const onChangePassword = async (data) => {
    setSaving(true);
    try {
      await authService.changePassword(data.current_password, data.new_password);
      toast.success('Password changed successfully!');
      resetPw();
      setPwValue('');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to change password.');
    } finally {
      setSaving(false);
    }
  };

  const pwStrength = checkPasswordStrength(pwValue);
  const TABS = [
    { id: 'profile',  label: 'Profile',  icon: FiUser },
    { id: 'security', label: 'Security', icon: FiShield },
  ];

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="section-title">Account Settings</h1>
        <p className="text-slate-500 text-sm mt-0.5">Manage your profile and account preferences</p>
      </div>

      {/* Avatar card */}
      <div className="card flex items-center gap-5">
        <div className="relative">
          <div className="w-20 h-20 rounded-2xl bg-primary-600 text-white flex items-center justify-center text-2xl font-bold select-none">
            {getInitials(user?.full_name || user?.email || 'U')}
          </div>
          <button className="absolute -bottom-1 -right-1 w-7 h-7 bg-white rounded-full border-2 border-slate-200 flex items-center justify-center hover:bg-slate-50 shadow-sm"
            onClick={() => toast('Avatar upload coming soon!')} aria-label="Change avatar">
            <FiCamera className="w-3.5 h-3.5 text-slate-500" />
          </button>
        </div>
        <div>
          <p className="text-lg font-semibold text-slate-900">{user?.full_name || 'User'}</p>
          <p className="text-sm text-slate-500">{user?.email}</p>
          <p className="text-xs text-slate-400 mt-1">
            Member since {formatDate(user?.created_at || new Date().toISOString())}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-slate-100 rounded-xl w-fit">
        {TABS.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-150
              ${activeTab === id ? 'bg-white text-primary-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'}`}
          >
            <Icon className="w-3.5 h-3.5" /> {label}
          </button>
        ))}
      </div>

      {/* Profile tab */}
      {activeTab === 'profile' && (
        <div className="card animate-fade-in">
          <h2 className="font-semibold text-slate-900 mb-5 flex items-center gap-2">
            <FiUser className="w-4 h-4 text-primary-600" /> Personal Information
          </h2>
          <form onSubmit={handleProfile(onSaveProfile)} noValidate className="space-y-4">
            <div>
              <label className="label" htmlFor="full_name">Full name</label>
              <div className="relative">
                <FiUser className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input id="full_name" type="text"
                  className={`input pl-10 ${profileErrors.full_name ? 'input-error' : ''}`}
                  {...regProfile('full_name', { required: 'Name is required', minLength: { value: 2, message: 'Min. 2 characters' } })}
                />
              </div>
              {profileErrors.full_name && <p className="error-message">{profileErrors.full_name.message}</p>}
            </div>

            <div>
              <label className="label" htmlFor="email">Email address</label>
              <div className="relative">
                <FiMail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input id="email" type="email"
                  className={`input pl-10 ${profileErrors.email ? 'input-error' : ''}`}
                  {...regProfile('email', {
                    required: 'Email is required',
                    pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: 'Invalid email' },
                  })}
                />
              </div>
              {profileErrors.email && <p className="error-message">{profileErrors.email.message}</p>}
            </div>

            <div className="pt-2 flex justify-end">
              <button type="submit" disabled={saving || !profileDirty} className="btn-primary">
                {saving ? <><LoadingSpinner size="sm" /> Saving…</> : <><FiSave className="w-4 h-4" /> Save Changes</>}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Security tab */}
      {activeTab === 'security' && (
        <div className="space-y-4 animate-fade-in">
          <div className="card">
            <h2 className="font-semibold text-slate-900 mb-5 flex items-center gap-2">
              <FiLock className="w-4 h-4 text-primary-600" /> Change Password
            </h2>
            <form onSubmit={handlePw(onChangePassword)} noValidate className="space-y-4">
              <div>
                <label className="label" htmlFor="current_password">Current password</label>
                <div className="relative">
                  <FiLock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input id="current_password" type={showCurrent ? 'text' : 'password'}
                    className={`input pl-10 pr-10 ${pwErrors.current_password ? 'input-error' : ''}`}
                    {...regPw('current_password', { required: 'Current password is required' })}
                  />
                  <button type="button" onClick={() => setShowCurrent((v) => !v)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    aria-label="Toggle visibility">
                    {showCurrent ? <FiEyeOff className="w-4 h-4" /> : <FiEye className="w-4 h-4" />}
                  </button>
                </div>
                {pwErrors.current_password && <p className="error-message">{pwErrors.current_password.message}</p>}
              </div>

              <div>
                <label className="label" htmlFor="new_password">New password</label>
                <div className="relative">
                  <FiLock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input id="new_password" type={showNew ? 'text' : 'password'}
                    className={`input pl-10 pr-10 ${pwErrors.new_password ? 'input-error' : ''}`}
                    {...regPw('new_password', {
                      required: 'New password is required',
                      minLength: { value: 8, message: 'Min. 8 characters' },
                      onChange: (e) => setPwValue(e.target.value),
                    })}
                  />
                  <button type="button" onClick={() => setShowNew((v) => !v)}
                    className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
                    aria-label="Toggle visibility">
                    {showNew ? <FiEyeOff className="w-4 h-4" /> : <FiEye className="w-4 h-4" />}
                  </button>
                </div>
                {pwErrors.new_password && <p className="error-message">{pwErrors.new_password.message}</p>}
                {pwValue && (
                  <div className="mt-2">
                    <div className="flex gap-1 mb-1">
                      {[1,2,3,4,5].map((n) => (
                        <div key={n} className={`h-1 flex-1 rounded-full transition-colors ${n <= pwStrength.score ? pwStrength.color : 'bg-slate-200'}`} />
                      ))}
                    </div>
                    <p className="text-xs text-slate-500">{pwStrength.label}</p>
                  </div>
                )}
              </div>

              <div>
                <label className="label" htmlFor="confirm_new_password">Confirm new password</label>
                <div className="relative">
                  <FiLock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input id="confirm_new_password" type={showNew ? 'text' : 'password'}
                    className={`input pl-10 ${pwErrors.confirm_new_password ? 'input-error' : ''}`}
                    {...regPw('confirm_new_password', {
                      required: 'Please confirm your new password',
                      validate: (v) => v === watchPw('new_password') || 'Passwords do not match',
                    })}
                  />
                </div>
                {pwErrors.confirm_new_password && <p className="error-message">{pwErrors.confirm_new_password.message}</p>}
              </div>

              <div className="pt-2 flex justify-end">
                <button type="submit" disabled={saving} className="btn-primary">
                  {saving ? <><LoadingSpinner size="sm" /> Updating…</> : <><FiShield className="w-4 h-4" /> Update Password</>}
                </button>
              </div>
            </form>
          </div>

          {/* Danger zone */}
          <div className="card border-danger-200">
            <h2 className="font-semibold text-danger-700 mb-2 flex items-center gap-2">
              <FiTrash2 className="w-4 h-4" /> Danger Zone
            </h2>
            <p className="text-sm text-slate-500 mb-4">
              Permanently delete your account and all associated data. This action cannot be undone.
            </p>
            <button onClick={() => setShowDeleteModal(true)} className="btn-danger btn-sm">
              Delete Account
            </button>
          </div>
        </div>
      )}

      <ConfirmModal
        isOpen={showDeleteModal}
        title="Delete Account"
        message="All your data including analyses and uploaded resumes will be permanently deleted. This cannot be undone."
        confirmLabel="Yes, Delete My Account"
        onConfirm={() => { setShowDeleteModal(false); toast.error('Account deletion coming soon!'); }}
        onCancel={() => setShowDeleteModal(false)}
        danger
      />
    </div>
  );
}

export default ProfilePage;
