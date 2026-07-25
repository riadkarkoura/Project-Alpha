import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import Home from "./page";

describe("Home", () => {
  it("renders the Project Alpha title and description", () => {
    render(<Home />);

    expect(screen.getByRole("heading", { name: "Project Alpha" })).toBeInTheDocument();
    expect(
      screen.getByText(/AI-powered research platform/i, { selector: "p" })
    ).toBeInTheDocument();
  });

  it("links to /projects via the Open Workspace button", () => {
    render(<Home />);

    const link = screen.getByRole("link", { name: "Open Workspace" });
    expect(link).toHaveAttribute("href", "/projects");
  });
});
