import Link from "next/link";

const projects = [
  {
    title: "Edmonton's Snow Clearing Crisis",
    description:
      "Interactive data story analyzing 209,000+ snow complaints, budget trends, and neighborhood patterns. Reveals how Edmonton's snow clearing service has declined despite population growth.",
    tags: ["Python", "Plotly.js", "Data Visualization", "Open Data"],
    href: "/projects/edmonton-snow-crisis.html",
    featured: true,
  },
];

export default function Portfolio() {
  return (
    <div className="max-w-5xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-heading font-bold uppercase tracking-wide text-primary-light mb-4">
        portfolio
      </h1>
      <p className="text-muted mb-12">
        A selection of projects and analyses.
      </p>

      <div className="grid gap-6 md:grid-cols-2">
        {projects.map((project) => {
          const CardContent = (
            <>
              {project.featured && (
                <span className="inline-block px-2 py-0.5 text-xs bg-primary text-background rounded mb-3">
                  Featured
                </span>
              )}
              <h3 className="text-lg font-heading font-semibold text-foreground mb-3">
                {project.title}
              </h3>
              <p className="text-muted text-sm leading-relaxed mb-4">
                {project.description}
              </p>
              <div className="flex flex-wrap gap-2">
                {project.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-2 py-0.5 text-xs bg-primary/20 text-primary-light rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
              {project.href && (
                <div className="mt-4 text-primary-light text-sm font-medium">
                  View Project →
                </div>
              )}
            </>
          );

          if (project.href) {
            return (
              <Link
                key={project.title}
                href={project.href}
                target="_blank"
                className="block p-6 bg-surface rounded-lg border border-surface-hover hover:border-primary transition-colors"
              >
                {CardContent}
              </Link>
            );
          }

          return (
            <div
              key={project.title}
              className="p-6 bg-surface rounded-lg border border-surface-hover hover:border-primary/50 transition-colors"
            >
              {CardContent}
            </div>
          );
        })}
      </div>
    </div>
  );
}
