import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import ATSScoreRing from '@/components/analysis/ATSScoreRing';

describe('ATSScoreRing', () => {
  it('renders the score value', () => {
    render(<ATSScoreRing score={75} />);
    expect(screen.getByText('75')).toBeInTheDocument();
  });

  it('shows Excellent label for score >= 80', () => {
    render(<ATSScoreRing score={85} />);
    expect(screen.getByText('Excellent')).toBeInTheDocument();
  });

  it('shows Good label for score 60-79', () => {
    render(<ATSScoreRing score={65} />);
    expect(screen.getByText('Good')).toBeInTheDocument();
  });

  it('shows Fair label for score 40-59', () => {
    render(<ATSScoreRing score={50} />);
    expect(screen.getByText('Fair')).toBeInTheDocument();
  });

  it('shows Needs Work label for score < 40', () => {
    render(<ATSScoreRing score={25} />);
    expect(screen.getByText('Needs Work')).toBeInTheDocument();
  });
});
