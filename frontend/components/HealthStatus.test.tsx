import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import HealthStatus from "./HealthStatus";

vi.mock("../services/api", () => ({
  getHealth: vi.fn(),
}));

import { getHealth } from "../services/api";

describe("HealthStatus", () => {
  it("shows an error when the backend cannot be reached", async () => {
    vi.mocked(getHealth).mockRejectedValue(
      new Error("Backend unavailable")
    );

    render(<HealthStatus />);

    expect(
      screen.getByText("Checking backend...")
    ).toBeInTheDocument();

    await waitFor(() => {
      expect(
        screen.getByText("Could not connect to backend.")
      ).toBeInTheDocument();
    });
  });
});