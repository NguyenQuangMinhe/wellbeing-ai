import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "../src/App";
import * as client from "../src/api/client";

function setViewport(width: number, height: number) {
  Object.defineProperty(window, "innerWidth", {
    writable: true,
    configurable: true,
    value: width,
  });
  Object.defineProperty(window, "innerHeight", {
    writable: true,
    configurable: true,
    value: height,
  });
  window.dispatchEvent(new Event("resize"));
}

describe("Disclaimer", () => {
  beforeEach(() => {
    vi.spyOn(client, "getHistory").mockResolvedValue([]);
    vi.spyOn(client, "getSessionStatus").mockResolvedValue({ locked: false });
  });

  it("is present on load", async () => {
    render(<App />);
    expect(await screen.findByText(/Disclaimer:/)).toBeInTheDocument();
    expect(
      screen.getByText(/not a proffessional clinician/i),
    ).toBeInTheDocument();
  });

  it("has no dismiss/close control", async () => {
    render(<App />);
    await screen.findByText(/Disclaimer:/);
    expect(
      screen.queryByRole("button", { name: /close|dismiss/i }),
    ).not.toBeInTheDocument();
  });

  it("remains visible at the smallest supported viewport (320px)", async () => {
    setViewport(320, 568);
    render(<App />);
    const disclaimer = await screen.findByText(/Disclaimer:/);
    expect(disclaimer).toBeVisible();
  });
});
