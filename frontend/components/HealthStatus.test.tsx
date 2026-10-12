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
it("shows backend status when the API succeeds", async () => {
  vi.mocked(getHealth).mockResolvedValue({
    status: "ok",
    service: "MusicVault API",
  });

  render(<HealthStatus />);

  await waitFor(() => {
    expect(
      screen.getByText("Backend Status")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Service: MusicVault API")
    ).toBeInTheDocument();

    expect(
      screen.getByText("Status: ok")
    ).toBeInTheDocument();
  });
});