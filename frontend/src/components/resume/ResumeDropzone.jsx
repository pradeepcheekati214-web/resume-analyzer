import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUploadCloud, FiFile, FiX, FiCheckCircle } from 'react-icons/fi';
import clsx from 'clsx';
import { validateResumeFile } from '@/utils/validators';
import { formatFileSize } from '@/utils/formatters';
import toast from 'react-hot-toast';

function ResumeDropzone({ file, onChange, disabled }) {
  const onDrop = useCallback((accepted, rejected) => {
    if (rejected.length > 0) {
      toast.error('Invalid file. Please upload a PDF or DOCX file under 10 MB.');
      return;
    }
    if (accepted.length > 0) {
      const f = accepted[0];
      const { valid, error } = validateResumeFile(f);
      if (!valid) { toast.error(error); return; }
      onChange(f);
    }
  }, [onChange]);

  const { getRootProps, getInputProps, isDragActive, isDragReject } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
    disabled,
  });

  const fileExt = file ? file.name.split('.').pop().toUpperCase() : '';

  return (
    <div>
      {/* Drop zone */}
      {!file && (
        <div
          {...getRootProps()}
          className={clsx(
            'relative border-2 border-dashed rounded-xl p-10 text-center cursor-pointer',
            'transition-all duration-200 focus:outline-none',
            isDragActive && !isDragReject && 'border-primary-400 bg-primary-50',
            isDragReject  && 'border-danger-400 bg-danger-50',
            !isDragActive && !isDragReject && 'border-slate-200 hover:border-primary-300 hover:bg-primary-50/40',
            disabled && 'opacity-50 cursor-not-allowed'
          )}
        >
          <input {...getInputProps()} aria-label="Upload resume" />

          <div className="flex flex-col items-center gap-3">
            <div className={clsx(
              'w-14 h-14 rounded-2xl flex items-center justify-center transition-colors duration-200',
              isDragActive && !isDragReject ? 'bg-primary-100' : 'bg-slate-100'
            )}>
              <FiUploadCloud className={clsx(
                'w-7 h-7 transition-colors duration-200',
                isDragActive && !isDragReject ? 'text-primary-600' : 'text-slate-400'
              )} />
            </div>

            {isDragReject ? (
              <p className="text-danger-600 font-medium text-sm">Invalid file type</p>
            ) : isDragActive ? (
              <p className="text-primary-600 font-medium text-sm">Drop it here!</p>
            ) : (
              <>
                <div>
                  <p className="font-semibold text-slate-700">
                    Drag &amp; drop your resume, or{' '}
                    <span className="text-primary-600 underline decoration-dotted">browse</span>
                  </p>
                  <p className="text-slate-400 text-xs mt-1">PDF, DOCX or DOC — max 10 MB</p>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* File preview */}
      {file && (
        <div className="flex items-center gap-4 p-4 rounded-xl border border-primary-200 bg-primary-50">
          <div className="w-12 h-12 rounded-xl bg-primary-100 flex items-center justify-center shrink-0">
            <FiFile className="w-6 h-6 text-primary-600" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <p className="font-medium text-slate-800 truncate text-sm">{file.name}</p>
              <span className="badge-blue shrink-0">{fileExt}</span>
            </div>
            <p className="text-xs text-slate-500 mt-0.5">{formatFileSize(file.size)}</p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <FiCheckCircle className="w-5 h-5 text-success-500" />
            {!disabled && (
              <button
                onClick={() => onChange(null)}
                className="w-7 h-7 rounded-lg flex items-center justify-center hover:bg-danger-50 text-slate-400 hover:text-danger-500 transition-colors"
                aria-label="Remove file"
              >
                <FiX className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default ResumeDropzone;
