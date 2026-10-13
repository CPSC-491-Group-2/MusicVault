import type { ComponentType } from "react";

import {
  ChartIcon,
  HeartIcon,
  HomeIcon,
  SearchIcon,
  SwipeIcon,
  UserIcon,
} from "@/components/ui/icons";

export type NavItem = {
  label: string;
  href: string;
  icon: ComponentType<{ className?: string }>;
};

export const NAV_ITEMS: readonly NavItem[] = [
  { label: "Home", href: "/dashboard", icon: HomeIcon },
  { label: "Swipe", href: "/swipe", icon: SwipeIcon },
  { label: "Vault", href: "/library", icon: HeartIcon },
  { label: "Search", href: "/search", icon: SearchIcon },
  { label: "Taste", href: "/taste", icon: ChartIcon },
  { label: "Profile", href: "/profile", icon: UserIcon },
];
