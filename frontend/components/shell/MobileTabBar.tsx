import { NavLinks } from "./NavLinks";

export function MobileTabBar() {
  return (
    <nav
      aria-label="Main"
      className="fixed inset-x-0 bottom-0 z-10 border-t border-olive/14 bg-paper pt-2 pb-[calc(8px+env(safe-area-inset-bottom))] min-[860px]:hidden"
    >
      <NavLinks variant="tabbar" />
    </nav>
  );
}
