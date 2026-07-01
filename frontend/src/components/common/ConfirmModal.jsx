import { useEffect, useRef } from 'react';
import { FiAlertTriangle } from 'react-icons/fi';

function ConfirmModal({ isOpen, title, message, confirmLabel = 'Confirm', onConfirm, onCancel, danger = false }) {
  const cancelRef = useRef(null);

  useEffect(() => {
    if (isOpen) cancelRef.current?.focus();
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 animate-fade-in">
      <div className="bg-white rounded-2xl shadow-xl max-w-sm w-full p-6 animate-slide-up">
        <div className={`w-12 h-12 rounded-full flex items-center justify-center mb-4 mx-auto
                         ${danger ? 'bg-danger-50' : 'bg-warning-50'}`}>
          <FiAlertTriangle className={`w-6 h-6 ${danger ? 'text-danger-500' : 'text-warning-500'}`} />
        </div>
        <h3 className="text-lg font-semibold text-slate-900 text-center mb-1">{title}</h3>
        <p className="text-slate-500 text-sm text-center mb-6">{message}</p>
        <div className="flex gap-3">
          <button ref={cancelRef} onClick={onCancel} className="btn-secondary flex-1">Cancel</button>
          <button onClick={onConfirm} className={`flex-1 btn ${danger ? 'btn-danger' : 'btn-primary'}`}>
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}

export default ConfirmModal;
