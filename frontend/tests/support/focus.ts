import { expect, type Locator, type Page } from "../fixtures";

export type FocusStop = {
  role: string; // "link"
  name: string; // accessible name, e.g. "Home"
  tag: string; // "a"
  width: number;
  height: number;
  hidden: boolean; // display, visibility or opacity, aria-hidden, or inert
  key: number; // the same element always gets the same key
};

async function roleAndName(locator: Locator) {
  // An aria snapshot starts with `- role "name"`, e.g. `- link "Home":`.
  const firstLine = (await locator.ariaSnapshot()).split("\n")[0];
  const match = /^- ([\w-]+)(?: ("(?:[^"\\]|\\.)*"))?/.exec(firstLine);

  return {
    role: match?.[1] ?? "",
    name: match?.[2] ? (JSON.parse(match[2]) as string) : "",
  };
}

async function describe(locator: Locator) {
  const { role, name } = await roleAndName(locator);

  return name ? `${role} "${name}"` : role || "element";
}

/** The accessible name Playwright computes for the element, "" if none. */
export async function accessibleName(locator: Locator) {
  return (await roleAndName(locator)).name;
}

async function readFocus(page: Page) {
  return page.evaluate(() => {
    const el = document.activeElement;

    if (!el || el === document.body || el === document.documentElement) {
      return null;
    }

    const state = window as typeof window & {
      __focusKeys?: WeakMap<Element, number>;
      __focusKeyCount?: number;
    };
    state.__focusKeys ??= new WeakMap();

    let key = state.__focusKeys.get(el);
    if (key === undefined) {
      key = state.__focusKeyCount = (state.__focusKeyCount ?? 0) + 1;
      state.__focusKeys.set(el, key);
    }

    const rect = el.getBoundingClientRect();

    return {
      tag: el.localName,
      key,
      width: rect.width,
      height: rect.height,
      hidden:
        !el.checkVisibility({ visibilityProperty: true, opacityProperty: true }) ||
        el.closest('[aria-hidden="true"], [inert]') !== null,
    };
  });
}

type TabThroughOptions = {
  /** Give up after this many presses, even if focus hasn't cycled. */
  max?: number;
  /** Runs at every stop, while that element has focus. */
  onStop?: (stop: FocusStop) => Promise<void>;
};

/**
 * Presses Tab from wherever focus is (the top of the page, right after
 * page.goto) until focus cycles back to the start or `max` presses, and
 * returns every element it landed on, in order. If focus gets stuck on an
 * element, that element appears twice in a row at the end.
 */
export async function tabThrough(
  page: Page,
  { max = 60, onStop }: TabThroughOptions = {},
) {
  const stops: FocusStop[] = [];

  for (let press = 0; press < max; press++) {
    await page.keyboard.press("Tab");
    const focus = await readFocus(page);

    if (!focus) {
      // Focus left the page after its last element: one full cycle.
      if (stops.length > 0) {
        break;
      }
      continue;
    }

    const stop = { ...focus, ...(await roleAndName(page.locator(":focus"))) };

    if (stops.at(-1)?.key === stop.key) {
      stops.push(stop);
      break;
    }

    if (stops[0]?.key === stop.key) {
      break;
    }

    stops.push(stop);
    await onStop?.(stop);
  }

  return stops;
}

/** Presses Tab until `target` has focus. Fails after `max` presses. */
export async function tabTo(page: Page, target: Locator, { max = 60 } = {}) {
  for (let press = 0; press < max; press++) {
    await page.keyboard.press("Tab");

    if (await target.evaluate((el) => el === document.activeElement)) {
      return;
    }
  }

  throw new Error(`Tab never reached ${await describe(target)} in ${max} presses`);
}

function isTransparent(color: string) {
  if (color === "" || color === "transparent") {
    return true;
  }

  // rgba(r, g, b, a) or the newer `... / a)` syntax.
  const alpha =
    /rgba\([^)]*,\s*([\d.]+)\)/.exec(color)?.[1] ??
    /\/\s*([\d.]+)\)/.exec(color)?.[1];

  return alpha !== undefined && parseFloat(alpha) === 0;
}

// Tailwind gives every element a stack of transparent, zero-size shadows, so
// "not none" isn't enough: a layer only counts with a real color and size.
function hasVisibleShadow(boxShadow: string) {
  if (boxShadow === "none") {
    return false;
  }

  return boxShadow.split(/,(?![^(]*\))/).some((layer) => {
    const color = /[a-z]+\([^)]*\)/.exec(layer)?.[0] ?? "";
    const lengths = layer.replace(color, "").match(/-?[\d.]+px/g) ?? [];

    return !isTransparent(color) && lengths.some((length) => parseFloat(length) !== 0);
  });
}

/**
 * Asserts the element has focus and shows it: an outline at least 2px wide in
 * a visible color, or a visible box-shadow ring. Spec section 11 asks for a
 * 2px olive ring with a 2 to 3px offset.
 */
export async function expectVisibleFocus(locator: Locator) {
  await expect(locator).toBeFocused();

  const style = await locator.evaluate((el) => {
    const computed = getComputedStyle(el);

    return {
      outlineStyle: computed.outlineStyle,
      outlineWidth: computed.outlineWidth,
      outlineColor: computed.outlineColor,
      boxShadow: computed.boxShadow,
    };
  });

  const outline =
    style.outlineStyle !== "none" &&
    parseFloat(style.outlineWidth) >= 2 &&
    !isTransparent(style.outlineColor);

  expect(
    outline || hasVisibleShadow(style.boxShadow),
    `${await describe(locator)} shows no focus indicator (outline: ${style.outlineStyle} ${style.outlineWidth} ${style.outlineColor}; box-shadow: ${style.boxShadow})`,
  ).toBe(true);
}

/** Asserts the element is at least `min` px wide and tall. Spec section 11: 44px. */
export async function expectMinTargetSize(locator: Locator, min = 44) {
  const box = await locator.boundingBox();
  const label = await describe(locator);

  expect(box, `${label} isn't rendered`).not.toBeNull();

  const { width, height } = box ?? { width: 0, height: 0 };

  expect(
    width >= min && height >= min,
    `${label} is ${width.toFixed(1)} x ${height.toFixed(1)}px, under ${min}px`,
  ).toBe(true);
}
