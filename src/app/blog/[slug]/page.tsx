import { notFound } from "next/navigation";
import { getPostBySlug, getAllPostSlugs } from "@/lib/blog";
import { Metadata } from "next";
import Markdown from "@/components/Markdown";

interface Props {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const slugs = getAllPostSlugs();
  return slugs.map((slug) => ({ slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = getPostBySlug(slug);
  if (!post) return { title: "Post Not Found" };

  return {
    title: `${post.meta.title} | amoredatus`,
    description: post.meta.description,
  };
}

export default async function BlogPost({ params }: Props) {
  const { slug } = await params;
  const post = getPostBySlug(slug);

  if (!post) {
    notFound();
  }

  return (
    <article className="max-w-3xl mx-auto px-6 py-16">
      <header className="mb-12">
        <h1 className="text-3xl font-heading font-bold text-primary-light mb-4">
          {post.meta.title}
        </h1>
        <div className="flex items-center gap-4">
          <span className="text-muted text-sm">{post.meta.date}</span>
          <div className="flex gap-2">
            {post.meta.tags.map((tag: string) => (
              <span
                key={tag}
                className="px-2 py-0.5 text-xs bg-primary/20 text-primary-light rounded"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      </header>

      <div className="prose prose-invert max-w-none">
        <Markdown content={post.content} />
      </div>
    </article>
  );
}
