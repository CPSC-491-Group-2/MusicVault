import AxeBuilder from "@axe-core/playwright";
import { test, type Page } from "@playwright/test";

import type { AllowlistEntry } from "./a11y-allowlist";

type AxeResults = Awaited<ReturnType<AxeBuilder["analyze"]>>;
type Violation = AxeResults["violations"][number];
type ViolationNode = Violation["nodes"][number];

export type AxeOptions = {
  /** Only scan inside this CSS selector, e.g. "#saved-songs". */
  include?: string;
  /** CSS selectors to leave out of the scan. */
  exclude?: string[];
  /** Axe rule ids to turn off. Always leave a comment saying why. */
  disableRules?: string[];
  /** Known, accepted violations. Pass the a11yAllowlist fixture. */
  allowlist?: AllowlistEntry[];
};

// WCAG 2.0, 2.1 and 2.2 at levels A and AA.
const WCAG_TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"];

export function makeAxe(page: Page) {
  return new AxeBuilder({ page }).withTags(WCAG_TAGS);
}

// Targets inside shadow roots or iframes come as nested lists of selectors.
function targetOf(node: ViolationNode) {
  return node.target.flat().join(" >>> ");
}

function isAllowlisted(
  rule: string,
  node: ViolationNode,
  allowlist: AllowlistEntry[],
) {
  const target = targetOf(node);

  return allowlist.some(
    (entry) => entry.rule === rule && target.includes(entry.selector),
  );
}

function describeViolations(violations: Violation[]) {
  const lines = [`Expected no axe violations, found ${violations.length}:`, ""];

  for (const violation of violations) {
    const targets = violation.nodes.map(targetOf);

    lines.push(
      `  ${violation.id} (${violation.impact ?? "unknown impact"}): ${violation.help}`,
      `    ${violation.helpUrl}`,
      ...targets.slice(0, 5).map((target) => `    - ${target}`),
    );

    if (targets.length > 5) {
      lines.push(`    ...and ${targets.length - 5} more`);
    }

    lines.push("");
  }

  lines.push("The full results are attached to the test report as axe-results.");

  return lines.join("\n");
}

export const axeMatchers = {
  async toPassAxe(page: Page, options: AxeOptions = {}) {
    const { include, exclude = [], disableRules = [], allowlist = [] } = options;

    const axe = makeAxe(page);

    if (include) {
      axe.include(include);
    }

    for (const selector of exclude) {
      axe.exclude(selector);
    }

    if (disableRules.length > 0) {
      axe.disableRules(disableRules);
    }

    const results = await axe.analyze();

    await test.info().attach("axe-results", {
      body: JSON.stringify(results, null, 2),
      contentType: "application/json",
    });

    const remaining = results.violations
      .map((violation) => ({
        ...violation,
        nodes: violation.nodes.filter(
          (node) => !isAllowlisted(violation.id, node, allowlist),
        ),
      }))
      .filter((violation) => violation.nodes.length > 0);

    const pass = remaining.length === 0;

    return {
      pass,
      name: "toPassAxe",
      message: () =>
        pass
          ? "Expected axe violations, but the page passed."
          : describeViolations(remaining),
    };
  },
};
