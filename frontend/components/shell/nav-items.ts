import type { ComponentType } from "react";

import {
  ChartIcon,
  HeartIcon,
  HomeIcon,
  SearchIcon,
  SwipeIcon,
  UserIcon,
} from "@/components/ui/icons";

/** Keys the icon hover motion in globals.css is written against. */
export type NavIconKey =
  | "home"
  | "swipe"
  | "vault"
  | "search"
  | "taste"
  | "profile";

export type NavItem = {
  label: string;
  href: string;
  icon: ComponentType<{ className?: string }>;
  iconKey: NavIconKey;
};

export const NAV_ITEMS: readonly NavItem[] = [
  { label: "Home", href: "/dashboard", icon: HomeIcon, iconKey: "home" },
  { label: "Swipe", href: "/swipe", icon: SwipeIcon, iconKey: "swipe" },
  { label: "Vault", href: "/library", icon: HeartIcon, iconKey: "vault" },
  { label: "Search", href: "/search", icon: SearchIcon, iconKey: "search" },
  { label: "Taste", href: "/taste", icon: ChartIcon, iconKey: "taste" },
  { label: "Profile", href: "/profile", icon: UserIcon, iconKey: "profile" },
];
