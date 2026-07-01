import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider }     from '@/context/AuthContext';
import { AnalysisProvider } from '@/context/AnalysisContext';
import ProtectedRoute from '@/components/common/ProtectedRoute';
import PublicRoute    from '@/components/common/PublicRoute';
import Layout     from '@/components/layout/Layout';
import AuthLayout from '@/components/layout/AuthLayout';

// Auth pages
import LoginPage    from '@/pages/LoginPage';
import RegisterPage from '@/pages/RegisterPage';

// Core pages
import HomePage     from '@/pages/HomePage';
import AnalysisPage from '@/pages/AnalysisPage';
import DashboardPage from '@/pages/DashboardPage';
import ProfilePage   from '@/pages/ProfilePage';
import NotFoundPage  from '@/pages/NotFoundPage';

// AI feature pages
import AISuggestionsPage      from '@/pages/AISuggestionsPage';
import JobMatchPage            from '@/pages/JobMatchPage';
import InterviewQuestionsPage  from '@/pages/InterviewQuestionsPage';
import MockInterviewPage       from '@/pages/MockInterviewPage';
import InterviewResultPage     from '@/pages/InterviewResultPage';
import InterviewHistoryPage    from '@/pages/InterviewHistoryPage';

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <AnalysisProvider>
          <Routes>
            {/* Public */}
            <Route element={<PublicRoute />}>
              <Route element={<AuthLayout />}>
                <Route path="/login"    element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
              </Route>
            </Route>

            {/* Protected */}
            <Route element={<ProtectedRoute />}>
              <Route element={<Layout />}>
                <Route path="/"         element={<Navigate to="/home" replace />} />
                <Route path="/home"     element={<HomePage />} />
                <Route path="/analysis/:id" element={<AnalysisPage />} />
                <Route path="/dashboard"    element={<DashboardPage />} />
                <Route path="/profile"      element={<ProfilePage />} />

                {/* AI Features */}
                <Route path="/ai/suggestions/:analysisId" element={<AISuggestionsPage />} />
                <Route path="/job-match"                  element={<JobMatchPage />} />
                <Route path="/interview/questions"        element={<InterviewQuestionsPage />} />
                <Route path="/interview/:interviewId"     element={<MockInterviewPage />} />
                <Route path="/interview/:interviewId/result" element={<InterviewResultPage />} />
                <Route path="/interview/history"          element={<InterviewHistoryPage />} />
              </Route>
            </Route>

            <Route path="*" element={<NotFoundPage />} />
          </Routes>

          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1e293b', color: '#f8fafc',
                fontSize: '0.875rem', borderRadius: '0.75rem', padding: '12px 16px',
              },
              success: { iconTheme: { primary: '#22c55e', secondary: '#f8fafc' } },
              error:   { iconTheme: { primary: '#ef4444', secondary: '#f8fafc' } },
            }}
          />
        </AnalysisProvider>
      </AuthProvider>
    </Router>
  );
}

export default App;
