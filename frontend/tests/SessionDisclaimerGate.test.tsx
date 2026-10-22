import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "../src/App";
import * as client from "../src/api/client";
import { DISCLAIMER_STORAGE_KEY } from "../src/hooks/useDisclaimerAckn";

const SESSION_KEY = "wellbeing_session_id";

describe("Disclaimer gate and fresh conversations", () => {
  beforeEach(() => {
    // runs after the global setup, so each test controls its own session state
    localStorage.clear();
    vi.spyOn(client, "getHistory").mockResolvedValue([]);
    vi.spyOn(client, "getSessionStatus").mockResolvedValue({ locked: false });
  });

  it("does not reappear when the same conversation is reopened", async () => {
    localStorage.setItem(SESSION_KEY, "s-1");
    localStorage.setItem(DISCLAIMER_STORAGE_KEY, "s-1");
    render(<App />);

    await screen.findByPlaceholderText(/type a message/i);
    expect(screen.queryByText(/before proceeding/i)).not.toBeInTheDocument();
  });

  it("appears when the conversation id differs from the acknowledged one", async () => {
    localStorage.setItem(SESSION_KEY, "s-1");
    localStorage.setItem(DISCLAIMER_STORAGE_KEY, "s-2");
    render(<App />);

    expect(await screen.findByText(/before proceeding/i)).toBeInTheDocument();
  });

  it("appears again after Delete history starts a fresh conversation", async () => {
    localStorage.setItem(SESSION_KEY, "s-1");
    localStorage.setItem(DISCLAIMER_STORAGE_KEY, "s-1");
    vi.spyOn(client, "clearHistory").mockResolvedValue({ deleted: 1 });

    const user = userEvent.setup();
    render(<App />);
    await screen.findByPlaceholderText(/type a message/i);

    await user.click(screen.getByRole("button", { name: /open menu/i }));
    await user.click(screen.getByRole("menuitem", { name: /delete history/i }));
    await user.click(screen.getByRole("button", { name: "Delete" }));
    await user.click(await screen.findByRole("button", { name: "Done" }));

    expect(await screen.findByText(/before proceeding/i)).toBeInTheDocument();
    expect(localStorage.getItem(SESSION_KEY)).not.toBe("s-1");
  });

  it("keeps the fresh conversation blocked until acknowledged, then opens it", async () => {
    localStorage.setItem(SESSION_KEY, "s-1");
    localStorage.setItem(DISCLAIMER_STORAGE_KEY, "s-1");
    vi.spyOn(client, "clearHistory").mockResolvedValue({ deleted: 1 });

    const user = userEvent.setup();
    render(<App />);
    await screen.findByPlaceholderText(/type a message/i);

    await user.click(screen.getByRole("button", { name: /open menu/i }));
    await user.click(screen.getByRole("menuitem", { name: /delete history/i }));
    await user.click(screen.getByRole("button", { name: "Delete" }));
    await user.click(await screen.findByRole("button", { name: "Done" }));
    await screen.findByText(/before proceeding/i);

    expect(
      screen.getByPlaceholderText(/type a message/i).closest("[inert]"),
    ).not.toBeNull();

    await user.click(screen.getByRole("button", { name: /i understand/i }));
    expect(screen.queryByText(/before proceeding/i)).not.toBeInTheDocument();
    expect(
      screen.getByPlaceholderText(/type a message/i).closest("[inert]"),
    ).toBeNull();
  });
});
