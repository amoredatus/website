export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-heading font-bold uppercase tracking-wide text-primary-light mb-8">
        about
      </h1>

      <div className="space-y-6 text-foreground/80 leading-relaxed">
        <p>
          Hi, I&apos;m Jordan. I&apos;m a data professional passionate about turning
          complex datasets into clear, actionable insights.
        </p>

        <p>
          With experience spanning data engineering, analytics, and business intelligence,
          I help organizations make better decisions through data. Whether it&apos;s building
          scalable data pipelines, creating interactive dashboards, or uncovering patterns
          in messy datasets — I love the challenge.
        </p>

        <h2 className="text-xl font-heading font-semibold uppercase tracking-wide text-primary-light pt-4">what I do</h2>
        <ul className="list-none space-y-3">
          {[
            "Data Engineering — ETL pipelines, data modeling, cloud infrastructure",
            "Analytics & BI — dashboards, reporting, statistical analysis",
            "Consulting — helping teams build data-driven cultures",
          ].map((item) => (
            <li key={item} className="flex items-start gap-3">
              <span className="text-primary-light mt-1">&#x2022;</span>
              <span>{item}</span>
            </li>
          ))}
        </ul>

        <h2 className="text-xl font-heading font-semibold uppercase tracking-wide text-primary-light pt-4">tools & technologies</h2>
        <div className="flex flex-wrap gap-2">
          {["Python", "SQL", "Spark", "Azure", "Power BI", "React", "TypeScript", "Git"].map(
            (tool) => (
              <span
                key={tool}
                className="px-3 py-1 bg-surface text-muted text-sm rounded-full border border-surface-hover"
              >
                {tool}
              </span>
            )
          )}
        </div>
      </div>
    </div>
  );
}
