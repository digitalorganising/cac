import { cn } from "@/lib/utils";

const proseClasses =
  "prose prose-slate prose-sm sm:prose-base prose-a:hover:no-underline ";

export default function DocsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <article className={cn(proseClasses, "max-w-4xl mx-auto pt-6 sm:pt-12")}>
      {children}
    </article>
  );
}
