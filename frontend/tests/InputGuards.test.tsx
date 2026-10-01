import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "../src/App";
import * as client from "../src/api/client";

describe("Input guards", () => {
  beforeEach(() => {
    vi.spyOn(client, "getHistory").mockResolvedValue([]);
    vi.spyOn(client, "getSessionStatus").mockResolvedValue({ locked: false });
  });

  it("blocks submission of an empty or whitespace-only message", async () => {
    const sendSpy = vi.spyOn(client, "sendMessage");
    const user = userEvent.setup();
    render(<App />);
    await screen.findByPlaceholderText(/type a message/i);

    const sendButton = screen.getByRole("button", { name: "Send" });
    expect(sendButton).toBeDisabled();

    await user.type(screen.getByPlaceholderText(/type a message/i), "   ");
    expect(screen.getByRole("button", { name: "Send" })).toBeDisabled();
    expect(sendSpy).not.toHaveBeenCalled();
  });

  it("passes a 500+ word message through intact, unmodified", async () => {
    const longMessage = Array.from({ length: 550 }, (_, i) => `word${i}`).join(
      " ",
    );
    vi.spyOn(client, "sendMessage").mockResolvedValue({
      type: "normal",
      message: "ok",
      risk_level: "low",
      end_session: false,
    });

    const user = userEvent.setup();
    render(<App />);
    const input = await screen.findByPlaceholderText(/type a message/i);

    await user.click(input);
    await user.paste(longMessage);
    await user.click(screen.getByRole("button", { name: "Send" }));

    await waitFor(() => {
      expect(client.sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({ message: longMessage }),
      );
    });
  });
});
