type ProgressBarProps = {
  value: number;
  label: string;
  className?: string;
};

export function ProgressBar({ value, label, className }: ProgressBarProps) {
  const clamped = Math.min(1, Math.max(0, value));
  const pct = Math.round(clamped * 100);

  const classes = [
    "h-[10px] w-full overflow-hidden rounded-full bg-blush",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      // oxlint-disable-next-line jsx-a11y/prefer-tag-over-role
      role="progressbar"
      aria-valuemin={0}
      aria-valuemax={100}
      aria-valuenow={pct}
      aria-label={label}
      className={classes}
    >
      {/* Width is dynamic, so it can't be a static Tailwind class. */}
      <div
        className="h-full rounded-full bg-green"
        style={{ width: `${pct}%` }}
      />
    </div>
  );
}
