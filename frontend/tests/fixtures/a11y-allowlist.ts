// Known, accepted axe violations. This list should stay empty.
//
// An entry hides one axe rule on matching elements wherever a spec passes the
// a11yAllowlist fixture to toPassAxe. Fix the markup instead whenever you can.
// Every entry needs a reason and a Jira ticket for the real fix, and adding one
// needs a review from the design spec owner (see tests/README.md).
export type AllowlistEntry = {
  rule: string; // axe rule id, e.g. "color-contrast"
  selector: string; // substring of the failing target selector
  reason: string; // why this is acceptable right now
  ticket: string; // jira key, e.g. "MV-130"
  addedBy: string;
};

export const A11Y_ALLOWLIST: AllowlistEntry[] = [];
