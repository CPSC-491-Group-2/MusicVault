type LogoMarkProps = {
  className?: string;
  color: "green" | "orchid";
};

// The headphones mark on its own, without the wordmark. Decorative by default:
// it always sits next to the Wordmark, which already carries the accessible name.
export default function LogoMark({ className, color }: LogoMarkProps) {
  const fill = color === "green" ? "fill-green" : "fill-orchid";

  return (
    <svg viewBox="-6 0 152 131" aria-hidden="true" className={className}>
      <path className={fill} d="M0.0,100.9 L0.0,70.0 A70.0,70.0 0 0 1 140.0,70.0 L140.0,100.9 L110.0,100.9 L110.0,70.0 A40.0,40.0 0 0 0 30.0,70.0 L30.0,100.9 Z M6.9,70.7 H23.1 A12.2,12.2 0 0 1 35.2,82.9 V118.8 A12.2,12.2 0 0 1 23.1,131.0 H6.9 A12.2,12.2 0 0 1 -5.2,118.8 V82.9 A12.2,12.2 0 0 1 6.9,70.7 Z M116.9,70.7 H133.1 A12.2,12.2 0 0 1 145.2,82.9 V118.8 A12.2,12.2 0 0 1 133.1,131.0 H116.9 A12.2,12.2 0 0 1 104.8,118.8 V82.9 A12.2,12.2 0 0 1 116.9,70.7 Z" />
    </svg>
  );
}
