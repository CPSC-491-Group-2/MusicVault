import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Navbar from "./Navbar";

describe("Navbar", () => {
  it("renders the MusicVault navigation links", () => {
    render(<Navbar />);

    expect(
      screen.getByRole("link", { name: "Home" })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", { name: "Library" })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", { name: "Search" })
    ).toBeInTheDocument();

    expect(
      screen.getByRole("link", { name: "Profile" })
    ).toBeInTheDocument();
  });
});
