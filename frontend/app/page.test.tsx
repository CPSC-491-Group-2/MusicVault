import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import Home from "./page";

vi.mock("../components/HealthStatus", () => ({
  default: () => <div>Mock Health Status</div>,
}));

describe("Home page", () => {
  it("renders the main application content", () => {
    render(<Home />);

    expect(
      screen.getByRole("heading", { name: "MusicVault" })
    ).toBeInTheDocument();

    expect(
      screen.getByText("Welcome to MusicVault.")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Mock Health Status")
    ).toBeInTheDocument();
  });
});