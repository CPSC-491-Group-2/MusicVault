import type { CSSProperties } from "react";
import { LOGO_MARK_PATH, LOGO_MARK_VIEWBOX } from "../brand/LogoMark";
import styles from "./LoadingStack.module.css";

type LoadingStackProps = {
  size?: number;
  layers?: number;
  label?: string;
  still?: boolean;
  flat?: boolean;
  mono?: boolean;
  inline?: boolean;
  className?: string;
};

const DEPTH_FILLS = [
  styles.green,
  styles.orchid,
  styles.greenTint,
  styles.orchidTint,
];

export function LoadingStack({
  size = 92,
  layers = 4,
  label = "Loading",
  still = false,
  flat = false,
  mono = false,
  inline = false,
  className,
}: LoadingStackProps) {
  const count = Math.min(6, Math.max(3, Math.round(layers)));
  const labelled = label !== "";

  const classes = [
    styles.root,
    still && styles.still,
    still && flat && styles.flat,
    inline && styles.inline,
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      role={labelled ? "status" : undefined}
      aria-label={labelled ? label : undefined}
      aria-hidden={labelled ? undefined : true}
      className={classes}
      style={{ "--ls-size": `${size}px` } as CSSProperties}
    >
      <div className={styles.stack}>
        {Array.from({ length: count }, (_, i) => (
          <svg
            key={i}
            viewBox={LOGO_MARK_VIEWBOX}
            aria-hidden="true"
            className={`${styles.layer} ${mono ? styles.mono : DEPTH_FILLS[(count - 1 - i) % 4]}`}
            style={{ "--i": i, "--ls-depth": count - 1 - i } as CSSProperties}
          >
            <path d={LOGO_MARK_PATH} />
          </svg>
        ))}
      </div>
    </div>
  );
}
