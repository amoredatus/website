export default function About() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-heading font-bold uppercase tracking-wide text-primary-light mb-8">
        about
      </h1>

      <div className="space-y-6 text-foreground/80 leading-relaxed">
        <p>
          Nice to meet you, I&apos;m Jordan. I&apos;m passionate about data science and
          people analytics. I live to find insights in data that can drive meaningful
          and impactful change.
        </p>

        <h2 className="text-xl font-heading font-semibold uppercase tracking-wide text-primary-light pt-4">tools & technologies</h2>
        <div className="flex flex-wrap gap-2">
          {["Python", "SQL", "Azure", "Power BI", "Tableau", "React", "Git", "AI", "LLMs", "UKG", "Workday", "Greenhouse", "Oracle"].map(
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
