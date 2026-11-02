export type ProgressSegment = {
  key: string;
  label: string;
  value: number;
  className: string;
};

export function ProgressBar({
  segments,
  caption,
}: {
  segments: ProgressSegment[];
  caption?: string;
}) {
  const total = segments.reduce((sum, segment) => sum + Math.max(segment.value, 0), 0);

  return (
    <div>
      <div
        className="flex h-3 overflow-hidden rounded-full bg-[#efe8dc]"
        role="img"
        aria-label={caption ?? "Distribuição de impacto dos produtos técnicos"}
      >
        {total === 0 ? (
          <div className="h-full w-full bg-[#d9d1c3]" />
        ) : (
          segments.map((segment) =>
            segment.value > 0 ? (
              <div
                key={segment.key}
                className={segment.className}
                style={{ width: `${(segment.value / total) * 100}%` }}
              />
            ) : null,
          )
        )}
      </div>
      <ul className="mt-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-[#5c564c]">
        {segments.map((segment) => (
          <li key={segment.key} className="inline-flex items-center gap-1.5">
            <span className={`size-2 rounded-full ${segment.className}`} aria-hidden />
            {segment.label}: {segment.value}
          </li>
        ))}
      </ul>
    </div>
  );
}
