import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "../src/App";
import * as client from "../src/api/client";
import { DISCLAIMER_STORAGE_KEY } from "../src/hooks/useDisclaimerAckn";

describe("First-run disclaimer gate", () => {
  beforeEach(() => {
    // runs after the global setup that pre-acknowledges, so this file starts at "first run"
    localStorage.clear();
    vi.spyOn(client, "getHistory").mockResolvedValue([]);
    vi.spyOn(client, "getSessionStatus").mockResolvedValue({ locked: false});
  });

  it("shows the gate on first run", async () => {
    render(<App />);
    expect(await screen.findByText(/before proceeding/i )).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /i understand/i })).toBeInTheDocument();
  });

  it("blocks the conversation until acknowledged", async () => {
    const sendSpy = vi.spyOn(client, "sendMessage");
    render(<App />);
    await screen.findByRole("dialog");

    const input = screen.getByPlaceholderText(/type a message/i);
    expect(input.closest("[inert]")).not.toBeNull();
    expect(sendSpy).not.toHaveBeenCalled();
  });

  it("does not close on Escape", async () => {
    const user = userEvent.setup();
    render(<App />);
    await screen.findByRole("dialog");

    await user.keyboard("{Escape}");
    expect(screen.getByRole("dialog")).toBeInTheDocument();
  });

  it("closes on button press, persists, and allows the conversation to start", async () => {
    const sendSpy = vi.spyOn(client, "sendMessage").mockResolvedValue({
      type: "normal",
      message: "hello back",
      risk_level: "low",
      end_session: false,
    });
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: /i understand/i }));

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(localStorage.getItem(DISCLAIMER_STORAGE_KEY)).toBe(
      localStorage.getItem("wellbeing_session_id"),
    );

    const input = screen.getByPlaceholderText(/type a message/i);
    expect(input.closest("[inert]")).toBeNull();
    await user.type(input, "hello");
    await user.click(screen.getByRole("button", { name: "Send" }));
    await waitFor(() => expect(sendSpy).toHaveBeenCalled());
  });

  it("does not show on a later visit once acknowledged", async () => {
    localStorage.setItem("wellbeing_session_id", "s-1");
    localStorage.setItem(DISCLAIMER_STORAGE_KEY, "s-1");
    render(<App />);
    await screen.findByPlaceholderText(/type a message/i);
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });
});