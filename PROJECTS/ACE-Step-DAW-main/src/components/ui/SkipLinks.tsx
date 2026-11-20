/**
 * Skip navigation links — visually hidden until focused (WCAG 2.4.1).
 * Renders anchor links that let keyboard users jump past the toolbar
 * directly to the active workspace and its key regions.
 */
export function SkipLinks({ workspace = 'daw' }: { workspace?: 'daw' | 'comfy' }) {
  return (
    <nav aria-label="Skip navigation">
      <a
        href={workspace === 'daw' ? '#main-content' : '#comfy-workspace'}
        className="sr-only focus:not-sr-only focus:fixed focus:top-1 focus:left-1 focus:z-[9999] focus:px-3 focus:py-1.5 focus:rounded focus:bg-daw-accent focus:text-zinc-900 focus:text-xs focus:font-medium focus:outline-none focus:ring-2 focus:ring-daw-bg"
      >
        {workspace === 'daw' ? 'Skip to main content' : 'Skip to ComfyUI workspace'}
      </a>
      {workspace === 'daw' && (
        <>
          <a
            href="#timeline-region"
            className="sr-only focus:not-sr-only focus:fixed focus:top-1 focus:left-40 focus:z-[9999] focus:px-3 focus:py-1.5 focus:rounded focus:bg-daw-accent focus:text-zinc-900 focus:text-xs focus:font-medium focus:outline-none focus:ring-2 focus:ring-daw-bg"
          >
            Skip to timeline
          </a>
          <a
            href="#mixer-region"
            className="sr-only focus:not-sr-only focus:fixed focus:top-1 focus:left-72 focus:z-[9999] focus:px-3 focus:py-1.5 focus:rounded focus:bg-daw-accent focus:text-zinc-900 focus:text-xs focus:font-medium focus:outline-none focus:ring-2 focus:ring-daw-bg"
          >
            Skip to mixer
          </a>
        </>
      )}
    </nav>
  );
}
