import { expect, test, type Locator, type Page } from "../fixtures";
import { visit } from "../support/routes";

const RED = "rgb(179, 38, 30)";

type AnimationLog = Window & { __animations?: string[] };

// /ui has several "Email" fields, one of them already errored; this is the one
// in the submittable form.
function errorForm(page: Page): Locator {
  return page
    .locator("form")
    .filter({ has: page.getByRole("button", { name: "Submit", exact: true }) });
}

async function submit(form: Locator) {
  const email = form.getByRole("textbox", { name: "Email" });

  // The first click can land before React hydrates; retry until it takes.
  await expect(async () => {
    await form.getByRole("button", { name: "Submit", exact: true }).click();
    await expect(email).toHaveAttribute("aria-invalid", "true", {
      timeout: 1_000,
    });
  }).toPass();

  return email;
}

async function errorMessage(page: Page, email: Locator) {
  const errorId = await email.getAttribute("aria-describedby");
  expect(errorId).toMatch(/-error$/);

  return page.locator(`[id="${errorId}"]`);
}

test.describe("field errors", { tag: "@a11y" }, () => {
  test("the message names the problem and the field reads as invalid", async ({
    page,
  }) => {
    await visit(page, "/ui");
    const form = errorForm(page);
    await expect(
      form.getByRole("textbox", { name: "Email" }),
    ).not.toHaveAttribute("aria-invalid", "true");

    const email = await submit(form);
    const message = await errorMessage(page, email);

    await expect(message).toHaveText("Enter your email");
    const icon = message.locator("svg");
    await expect(icon).toBeVisible();
    await expect(icon).toHaveAttribute("aria-hidden", "true");
    expect(
      await message.evaluate((el) => !!el.closest('[aria-live="polite"]')),
    ).toBe(true);
  });

  test("the border and the message use the red token", async ({ page }) => {
    await visit(page, "/ui");
    const email = await submit(errorForm(page));
    const message = await errorMessage(page, email);

    await expect(email.locator("..")).toHaveCSS("border-color", RED);
    await expect(message).toHaveCSS("color", RED);
  });

  test("the error state passes axe", async ({ page, a11yAllowlist }) => {
    await visit(page, "/ui");
    const email = await submit(errorForm(page));
    const errorId = await email.getAttribute("aria-describedby");

    // The form has no id, so aim axe at the one holding this message.
    await expect(page).toPassAxe({
      include: `form:has([id="${errorId}"])`,
      allowlist: a11yAllowlist,
    });
  });

  test("submitting shakes the field, and nothing shakes on load", async ({
    page,
  }) => {
    await visit(page, "/ui");
    const form = errorForm(page);
    await expect(form.locator(".mv-shake")).toHaveCount(0);

    // Record the animation as it starts: the class is gone by animationend.
    await form.evaluate((el) => {
      const log = window as AnimationLog;
      log.__animations = [];
      el.addEventListener("animationstart", (event) => {
        log.__animations?.push((event as AnimationEvent).animationName);
      });
    });

    await submit(form);

    await expect
      .poll(() =>
        page.evaluate(() => (window as AnimationLog).__animations ?? []),
      )
      .toContain("mv-shake");
  });
});
