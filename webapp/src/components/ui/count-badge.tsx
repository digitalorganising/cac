export default function CountBadge({ count }: { count: number }) {
  return (
    <span className="inline-flex items-center justify-center bg-slate-600 text-white h-4 min-w-4 px-1 rounded-full text-xs tabular-nums">
      {count}
    </span>
  );
}
