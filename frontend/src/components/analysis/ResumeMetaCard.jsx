import { FiFileText, FiUser, FiMail, FiPhone, FiMapPin, FiCalendar, FiExternalLink } from 'react-icons/fi';
import { formatDate, formatFileSize } from '@/utils/formatters';

function MetaRow({ icon: Icon, label, value }) {
  if (!value) return null;
  return (
    <div className="flex items-start gap-3 py-2.5 border-b border-slate-50 last:border-0">
      <Icon className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
      <div className="min-w-0">
        <p className="text-xs text-slate-400 uppercase tracking-wider font-medium">{label}</p>
        <p className="text-sm text-slate-700 font-medium truncate">{value}</p>
      </div>
    </div>
  );
}

function ResumeMetaCard({ analysis }) {
  const { resume_metadata: meta, contact_info: contact } = analysis || {};

  return (
    <div className="space-y-4">
      {/* File info */}
      <div className="card">
        <div className="flex items-center gap-2 mb-3">
          <FiFileText className="w-4 h-4 text-primary-600" />
          <h3 className="font-semibold text-slate-900 text-sm">Resume File</h3>
        </div>
        <MetaRow icon={FiFileText} label="File Name"   value={analysis?.file_name} />
        <MetaRow icon={FiCalendar} label="Analyzed"    value={formatDate(analysis?.created_at)} />
        <MetaRow icon={FiFileText} label="File Size"   value={meta?.file_size ? formatFileSize(meta.file_size) : null} />
        <MetaRow icon={FiFileText} label="File Type"   value={meta?.file_type?.toUpperCase()} />
        <MetaRow icon={FiFileText} label="Word Count"  value={meta?.word_count ? `${meta.word_count} words` : null} />
        <MetaRow icon={FiFileText} label="Page Count"  value={meta?.page_count ? `${meta.page_count} page${meta.page_count > 1 ? 's' : ''}` : null} />

        {analysis?.s3_url && (
          <a
            href={analysis.s3_url}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-3 btn-secondary btn-sm w-full no-underline flex items-center justify-center gap-1.5"
          >
            <FiExternalLink className="w-3.5 h-3.5" /> View Original
          </a>
        )}
      </div>

      {/* Contact info */}
      {contact && (
        <div className="card">
          <div className="flex items-center gap-2 mb-3">
            <FiUser className="w-4 h-4 text-primary-600" />
            <h3 className="font-semibold text-slate-900 text-sm">Contact Detected</h3>
          </div>
          <MetaRow icon={FiUser}   label="Name"     value={contact.name} />
          <MetaRow icon={FiMail}   label="Email"    value={contact.email} />
          <MetaRow icon={FiPhone}  label="Phone"    value={contact.phone} />
          <MetaRow icon={FiMapPin} label="Location" value={contact.location} />
        </div>
      )}

      {/* Quick score summary */}
      <div className="card bg-primary-50 border-primary-100">
        <h3 className="font-semibold text-slate-900 text-sm mb-3">Quick Tips</h3>
        <ul className="space-y-2 text-xs text-slate-600">
          <li className="flex items-start gap-2">
            <span className="w-4 h-4 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">1</span>
            Tailor your resume for each job application.
          </li>
          <li className="flex items-start gap-2">
            <span className="w-4 h-4 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">2</span>
            Use keywords from the job description naturally.
          </li>
          <li className="flex items-start gap-2">
            <span className="w-4 h-4 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">3</span>
            Quantify achievements with numbers where possible.
          </li>
          <li className="flex items-start gap-2">
            <span className="w-4 h-4 rounded-full bg-primary-100 text-primary-700 flex items-center justify-center text-xs font-bold shrink-0 mt-0.5">4</span>
            Keep formatting simple for better ATS parsing.
          </li>
        </ul>
      </div>
    </div>
  );
}

export default ResumeMetaCard;
