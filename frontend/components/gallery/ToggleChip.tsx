"use client";

import { useState } from "react";

import { Chip, type ChipProps } from "@/components/ui/Chip";

type ToggleChipProps = Omit<ChipProps, "pressed" | "onPressedChange"> & {
  defaultPressed?: boolean;
};

export function ToggleChip({
  defaultPressed = false,
  ...rest
}: ToggleChipProps) {
  const [pressed, setPressed] = useState(defaultPressed);

  return <Chip {...rest} pressed={pressed} onPressedChange={setPressed} />;
}
