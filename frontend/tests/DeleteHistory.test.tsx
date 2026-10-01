import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import App from "../src/App";
import * as client from "../src/api/client";

describe("Delete history flow", () => {
  beforeEach(() => {
    vi.spyOn(client, "getHistory").mockResolvedValue([]);
    vi.spyOn(client, "getSessionStatus").mockResolvedValue({ locked: false });
  });

  async function openDeleteConfirmation(
    user: ReturnType<typeof userEvent.setup>,
  ) {
    render(<App />);
    await screen.findByPlaceholderText(/type a message/i);
    await user.click(screen.getByRole("button", { name: /open menu/i }));
    await user.click(screen.getByRole("menuitem", { name: /delete history/i }));
  }

  it("requires confirmation before deleting", async () => {
    const clearSpy = vi.spyOn(client, "clearHistory");
    const user = userEvent.setup();
    await openDeleteConfirmation(user);

    expect(
      screen.getByText(/delete conversation history permanently/i),
    ).toBeInTheDocument();
    expect(clearSpy).not.toHaveBeenCalled();
  });

  it("cancel closes the dialog without deleting", async () => {
    const clearSpy = vi.spyOn(client, "clearHistory");
    const user = userEvent.setup();
    await openDeleteConfirmation(user);

    await user.click(screen.getByRole("button", { name: "Cancel" }));
    expect(
      screen.queryByText(/delete conversation history permanently/i),
    ).not.toBeInTheDocument();
    expect(clearSpy).not.toHaveBeenCalled();
  });

  it("confirms deletion, shows success, and leaves the session usable afterward", async () => {
    vi.spyOn(client, "clearHistory").mockResolvedValue({ deleted: 3 });
    const sendSpy = vi.spyOn(client, "sendMessage").mockResolvedValue({
      type: "normal",
      message: "hi again",
      risk_level: "low",
      end_session: false,
    });

    const user = userEvent.setup();
    await openDeleteConfirmation(user);
    await user.click(screen.getByRole("button", { name: "Delete" }));

    await waitFor(() => {
      expect(
        screen.getByText(/conversation history deleted/i),
      ).toBeInTheDocument();
    });

    await user.click(screen.getByRole("button", { name: "Done" }));
    expect(
      screen.queryByText(/conversation history deleted/i),
    ).not.toBeInTheDocument();

    // session remains usable: can still type and send after deletion
    const input = screen.getByPlaceholderText(/type a message/i);
    await user.type(input, "hello again");
    await user.click(screen.getByRole("button", { name: "Send" }));
    await waitFor(() => expect(sendSpy).toHaveBeenCalled());
  });

  it("shows an error state and allows retry on failed deletion", async () => {
    vi.spyOn(client, "clearHistory")
      .mockRejectedValueOnce(new Error("fail"))
      .mockResolvedValueOnce({ deleted: 1 });

    const user = userEvent.setup();
    await openDeleteConfirmation(user);
    await user.click(screen.getByRole("button", { name: "Delete" }));

    await waitFor(() =>
      expect(
        screen.getByText(/sorry, an error has occurred/i),
      ).toBeInTheDocument(),
    );

    await user.click(screen.getByRole("button", { name: "Try again" }));
    await waitFor(() =>
      expect(
        screen.getByText(/conversation history deleted/i),
      ).toBeInTheDocument(),
    );
  });
});
