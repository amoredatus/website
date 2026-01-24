import Link from "next/link";
import { getAllPosts } from "@/lib/blog";

export default function Blog() {
  const posts = getAllPosts();

  return (
    <div className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="text-3xl font-heading font-bold uppercase tracking-wide text-primary-light mb-4">
        blog
      </h1>
      <p className="text-muted mb-12">
        Thoughts on data, analytics, and engineering.
      </p>

      {posts.length === 0 ? (
        <p className="text-muted italic">No posts yet. Check back soon.</p>
      ) : (
        <div className="space-y-8">
          {posts.map((post) => (
            <article
              key={post.slug}
              className="p-6 bg-surface rounded-lg border border-surface-hover hover:border-primary/50 transition-colors"
            >
              <Link
                href={`/blog/${post.slug}`}
                className="no-underline"
              >
                <h2 className="text-lg font-heading font-semibold text-foreground mb-2 hover:text-primary-light transition-colors">
                  {post.title}
                </h2>
              </Link>
              <p className="text-muted text-sm mb-3">{post.description}</p>
              <div className="flex items-center gap-4">
                <span className="text-muted text-xs">{post.date}</span>
                <div className="flex gap-2">
                  {post.tags.map((tag) => (
                    <span
                      key={tag}
                      className="px-2 py-0.5 text-xs bg-primary/20 text-primary-light rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>
      )}
    </div>
  );
}
