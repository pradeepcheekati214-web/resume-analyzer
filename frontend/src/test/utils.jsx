import { render } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '@/context/AuthContext';
import { AnalysisProvider } from '@/context/AnalysisContext';

/**
 * Custom render that wraps components with all required providers.
 */
function renderWithProviders(ui, options = {}) {
  function Wrapper({ children }) {
    return (
      <BrowserRouter>
        <AuthProvider>
          <AnalysisProvider>
            {children}
          </AnalysisProvider>
        </AuthProvider>
      </BrowserRouter>
    );
  }
  return render(ui, { wrapper: Wrapper, ...options });
}

export * from '@testing-library/react';
export { renderWithProviders as render };
