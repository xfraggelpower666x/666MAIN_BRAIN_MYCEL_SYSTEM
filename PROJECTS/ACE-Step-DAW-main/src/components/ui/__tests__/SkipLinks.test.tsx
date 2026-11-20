import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { SkipLinks } from '../SkipLinks';

describe('SkipLinks', () => {
  it('only links to targets in the active DAW workspace', () => {
    render(<SkipLinks workspace="daw" />);
    expect(screen.getByRole('link', { name: 'Skip to main content' })).toHaveAttribute('href', '#main-content');
    expect(screen.getByRole('link', { name: 'Skip to timeline' })).toHaveAttribute('href', '#timeline-region');
    expect(screen.getByRole('link', { name: 'Skip to mixer' })).toHaveAttribute('href', '#mixer-region');
    expect(screen.queryByRole('link', { name: 'Skip to ComfyUI workspace' })).not.toBeInTheDocument();
  });

  it('links to the visible ComfyUI workspace instead of hidden DAW targets', () => {
    render(<SkipLinks workspace="comfy" />);
    expect(screen.getByRole('link', { name: 'Skip to ComfyUI workspace' })).toHaveAttribute('href', '#comfy-workspace');
    expect(screen.queryByRole('link', { name: 'Skip to timeline' })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Skip to mixer' })).not.toBeInTheDocument();
  });
});
