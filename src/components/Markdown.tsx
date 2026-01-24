import React from "react";

interface MarkdownProps {
  content: string;
}

function parseMarkdown(md: string): string {
  let html = md
    // Code blocks
    .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre class="bg-surface-hover rounded-lg p-4 overflow-x-auto my-4"><code class="text-primary-light text-sm">$2</code></pre>')
    // Inline code
    .replace(/`([^`]+)`/g, '<code class="bg-surface-hover px-1.5 py-0.5 rounded text-primary-light text-sm">$1</code>')
    // Headers
    .replace(/^### (.+)$/gm, '<h3 class="text-lg font-mono text-primary-light mt-8 mb-3">$1</h3>')
    .replace(/^## (.+)$/gm, '<h2 class="text-xl font-mono text-primary-light mt-10 mb-4">$1</h2>')
    .replace(/^# (.+)$/gm, '<h1 class="text-2xl font-mono text-primary-light mt-10 mb-4">$1</h1>')
    // Bold and italic
    .replace(/\*\*(.+?)\*\*/g, '<strong class="text-foreground">$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    // Links
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-primary-light hover:text-accent underline">$1</a>')
    // Unordered lists
    .replace(/^- (.+)$/gm, '<li class="ml-4 text-foreground/80">$1</li>')
    // Paragraphs (lines that aren't already wrapped)
    .replace(/^(?!<[hluop]|<li|<pre|<code)(.+)$/gm, '<p class="text-foreground/80 leading-relaxed mb-4">$1</p>');

  // Wrap consecutive <li> in <ul>
  html = html.replace(/((?:<li[^>]*>.*<\/li>\n?)+)/g, '<ul class="list-disc space-y-1 my-4">$1</ul>');

  return html;
}

export default function Markdown({ content }: MarkdownProps) {
  const html = parseMarkdown(content);
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
