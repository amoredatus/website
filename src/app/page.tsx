export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-6">
      <div className="text-center">
        <h1 className="text-5xl md:text-7xl font-heading font-bold tracking-wide text-primary-light mb-2">
          amoredatus
        </h1>
        <p className="text-xl md:text-2xl font-heading font-medium tracking-widest uppercase text-muted mb-12">
          lovedata
        </p>
        <p className="text-foreground/80 max-w-lg mx-auto text-lg leading-relaxed">
          Data analytics, engineering, and consulting.
          Turning raw data into meaningful insight.
        </p>
      </div>

      <div className="mt-16 flex gap-6">
        <a
          href="/portfolio"
          className="px-6 py-3 bg-primary text-foreground rounded-md text-sm font-medium uppercase tracking-wider no-underline hover:bg-primary-light hover:text-background transition-colors"
        >
          view work
        </a>
        <a
          href="/contact"
          className="px-6 py-3 border border-surface-hover text-muted rounded-md text-sm font-medium uppercase tracking-wider no-underline hover:border-primary-light hover:text-primary-light transition-colors"
        >
          get in touch
        </a>
      </div>
    </div>
  );
}
