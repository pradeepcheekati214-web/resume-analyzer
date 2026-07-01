import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import ResumeDropzone from '@/components/resume/ResumeDropzone';
import JobDescriptionInput from '@/components/resume/JobDescriptionInput';
import UploadProgress from '@/components/resume/UploadProgress';
import RecentAnalyses from '@/components/resume/RecentAnalyses';
import { useAnalysis } from '@/context/AnalysisContext';
import { FiZap, FiTarget, FiTrendingUp } from 'react-icons/fi';

const FEATURES = [
  { icon: FiZap,        title: 'ATS Score',          desc: 'See exactly how recruiters\' systems rate your resume.' },
  { icon: FiTarget,     title: 'Keyword Matching',    desc: 'Find missing keywords and skills for your target role.' },
  { icon: FiTrendingUp, title: 'Smart Suggestions',   desc: 'Get actionable tips to improve your resume instantly.' },
];

function HomePage() {
  const navigate = useNavigate();
  const { uploadAndAnalyze, isUploading, isAnalyzing, uploadProgress } = useAnalysis();
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');

  const handleAnalyze = async () => {
    if (!file) { toast.error('Please upload a resume first.'); return; }
    try {
      const analysis = await uploadAndAnalyze(file, jobDescription);
      toast.success('Analysis complete!');
      navigate(`/analysis/${analysis.id}`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Analysis failed. Please try again.');
    }
  };

  const isProcessing = isUploading || isAnalyzing;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Hero */}
      <div className="text-center pt-4">
        <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 mb-3">
          Analyze Your Resume with AI
        </h1>
        <p className="text-slate-500 text-lg max-w-xl mx-auto">
          Upload your resume and get an instant ATS score, skills gap analysis, and personalized improvement suggestions.
        </p>
      </div>

      {/* Feature pills */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {FEATURES.map(({ icon: Icon, title, desc }) => (
          <div key={title} className="card flex items-start gap-3 p-4">
            <div className="w-9 h-9 rounded-lg bg-primary-50 flex items-center justify-center shrink-0">
              <Icon className="w-4 h-4 text-primary-600" />
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-800">{title}</p>
              <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Upload card */}
      <div className="card space-y-6">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Upload Resume</h2>
          <p className="text-slate-500 text-sm mt-0.5">Supports PDF and DOCX files up to 10 MB</p>
        </div>

        <ResumeDropzone file={file} onChange={setFile} disabled={isProcessing} />

        {file && (
          <JobDescriptionInput
            value={jobDescription}
            onChange={setJobDescription}
            disabled={isProcessing}
          />
        )}

        {isProcessing && (
          <UploadProgress
            isUploading={isUploading}
            isAnalyzing={isAnalyzing}
            progress={uploadProgress}
          />
        )}

        <button
          onClick={handleAnalyze}
          disabled={!file || isProcessing}
          className="btn-primary btn-lg w-full"
        >
          {isProcessing ? 'Processing…' : 'Analyze Resume'}
        </button>
      </div>

      {/* Recent analyses */}
      <RecentAnalyses />
    </div>
  );
}

export default HomePage;
