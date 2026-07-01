import { FiUploadCloud, FiCpu } from 'react-icons/fi';

function UploadProgress({ isUploading, isAnalyzing, progress }) {
  return (
    <div className="rounded-xl bg-primary-50 border border-primary-100 p-4 space-y-3">
      {/* Upload step */}
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 transition-colors
          ${isUploading ? 'bg-primary-600 text-white' : 'bg-success-500 text-white'}`}>
          <FiUploadCloud className="w-4 h-4" />
        </div>
        <div className="flex-1">
          <div className="flex justify-between mb-1">
            <span className="text-xs font-medium text-slate-700">
              {isUploading ? 'Uploading resume…' : 'Upload complete'}
            </span>
            {isUploading && <span className="text-xs text-primary-600 font-semibold">{progress}%</span>}
          </div>
          <div className="h-1.5 rounded-full bg-primary-100 overflow-hidden">
            <div
              className="h-full bg-primary-600 rounded-full transition-all duration-300"
              style={{ width: isUploading ? `${progress}%` : '100%' }}
            />
          </div>
        </div>
      </div>

      {/* Analysis step */}
      <div className="flex items-center gap-3">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 transition-colors
          ${isAnalyzing ? 'bg-primary-600 text-white animate-pulse' : 'bg-slate-200 text-slate-400'}`}>
          <FiCpu className="w-4 h-4" />
        </div>
        <div className="flex-1">
          <span className="text-xs font-medium text-slate-700">
            {isAnalyzing ? 'Analyzing with AI…' : 'Waiting to analyze…'}
          </span>
          {isAnalyzing && (
            <div className="h-1.5 rounded-full bg-primary-100 overflow-hidden mt-1">
              <div className="h-full bg-primary-600 rounded-full animate-pulse w-3/4" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default UploadProgress;
