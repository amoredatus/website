const projects = [
  {
    title: "Skill Analytics Pipeline",
    description:
      "End-to-end medallion architecture data pipeline for workforce skill analytics. Bronze, silver, and gold layer transformations with incremental processing.",
    tags: ["Python", "Spark", "Delta Lake", "Azure"],
  },
  {
    title: "Interactive Dashboard",
    description:
      "Business intelligence dashboard providing real-time insights into key organizational metrics and workforce trends.",
    tags: ["Power BI", "SQL", "DAX"],
  },
  {
    title: "Data Quality Framework",
    description:
      "Automated data quality checks and monitoring across multiple data sources, ensuring pipeline reliability and data integrity.",
    tags: ["Python", "Great Expectations", "CI/CD"],
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
        {projects.map((project) => (
          <div
            key={project.title}
            className="p-6 bg-surface rounded-lg border border-surface-hover hover:border-primary/50 transition-colors"
          >
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
          </div>
        ))}
      </div>
    </div>
  );
}
