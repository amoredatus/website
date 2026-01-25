export default function Contact() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-heading font-bold uppercase tracking-wide text-primary-light mb-4">
        contact
      </h1>
      <p className="text-muted mb-12">
        Want to connect? Find me here.
      </p>

      <div className="space-y-6">
        <div className="flex flex-col gap-4">
          <a
            href="https://linkedin.com/in/jordankirchner"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-4 bg-surface rounded-lg border border-surface-hover hover:border-primary/50 transition-colors no-underline"
          >
            <span className="text-primary-light text-lg">in</span>
            <div>
              <p className="text-foreground text-sm font-heading font-medium uppercase tracking-wider">linkedin</p>
              <p className="text-muted text-sm">Connect with me</p>
            </div>
          </a>

          <a
            href="https://github.com/amoredatus"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-3 p-4 bg-surface rounded-lg border border-surface-hover hover:border-primary/50 transition-colors no-underline"
          >
            <span className="text-primary-light text-lg">&lt;/&gt;</span>
            <div>
              <p className="text-foreground text-sm font-heading font-medium uppercase tracking-wider">github</p>
              <p className="text-muted text-sm">View my repositories</p>
            </div>
          </a>
        </div>
      </div>
    </div>
  );
}
