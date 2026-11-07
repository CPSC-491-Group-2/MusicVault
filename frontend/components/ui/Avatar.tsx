import Image from "next/image";

type AvatarSize = 32 | 40 | 56;

type AvatarProps = {
  size: AvatarSize;
  src?: string;
  alt?: string;
  initial?: string;
  className?: string;
};

const SIZE_CLASSES: Record<AvatarSize, string> = {
  32: "size-8",
  40: "size-10",
  56: "size-14",
};

const INITIAL_TEXT_CLASSES: Record<AvatarSize, string> = {
  32: "text-[14px]",
  40: "text-[17px]",
  56: "text-[22px]",
};

export function Avatar({ size, src, alt, initial, className }: AvatarProps) {
  const classes = [
    "inline-flex shrink-0 items-center justify-center overflow-hidden rounded-full bg-orchid text-olive font-medium",
    SIZE_CLASSES[size],
    INITIAL_TEXT_CLASSES[size],
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <span className={classes}>
      {src ? (
        <Image
          src={src}
          alt={alt ?? ""}
          width={size}
          height={size}
          className="h-full w-full object-cover"
        />
      ) : (
        initial
      )}
    </span>
  );
}
