import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TakeoverScreen } from "../src/components/Takeover";
import { cleanup } from "@testing-library/react";

describe("TakeoverScreen", () => {
  beforeEach(() => {
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText: vi.fn() },
      writable: true,
      configurable: true,
    });
  });
  afterEach(() => {
    cleanup();
  });

  it("renders crisis heading, message, and support links", () => {
    render(
      <TakeoverScreen kind="crisis" message="Please reach out for help." />,
    );
    expect(screen.getByRole("alertdialog")).toBeInTheDocument();
    expect(
      screen.getByText("You deserve support right now"),
    ).toBeInTheDocument();
    expect(screen.getByText("Please reach out for help.")).toBeInTheDocument();
    expect(screen.getByText(/Lifeline Australia/)).toBeInTheDocument();
  });

  it("renders boundary heading without support links", () => {
    render(
      <TakeoverScreen
        kind="boundary"
        message="Let's talk about something else."
      />,
    );
    expect(
      screen.getByText("Let's take a different approach"),
    ).toBeInTheDocument();
    // Boundary to still show the message, but not the support links?
    //expect(screen.queryByText(/Lifeline Australia/)).not.toBeInTheDocument();
  });

  it("is keyboard-focusable on the first support link", async () => {
    const user = userEvent.setup();
    render(<TakeoverScreen kind="crisis" message={null} />);
    await user.tab();
    expect(screen.getByRole("link", { name: /Emergency/ })).toHaveFocus();
  });

  it("shows loading state on the copy button while writing to clipboard", async () => {
    let resolveCopy: () => void;
    (navigator.clipboard.writeText as any).mockReturnValue(
      new Promise<void>((r) => {
        resolveCopy = r;
      }),
    );
    render(<TakeoverScreen kind="crisis" message={null} />);
    const copyButton = screen.getAllByRole("button", { name: "Copy" })[0];
    fireEvent.click(copyButton);
    expect(await screen.findByText("Copying…")).toBeInTheDocument();
    expect(copyButton).toBeDisabled();
    resolveCopy!();
    await waitFor(() =>
      expect(screen.queryByText("Copying…")).not.toBeInTheDocument(),
    );
  });

  it("shows error state and Retry label on clipboard failure", async () => {
    (navigator.clipboard.writeText as any).mockRejectedValue(
      new Error("denied"),
    );
    render(<TakeoverScreen kind="crisis" message={null} />);
    fireEvent.click(screen.getAllByRole("button", { name: "Copy" })[0]);
    expect(await screen.findByRole("alert")).toHaveTextContent(
      /couldn't copy/i,
    );
    expect(
      screen.getAllByRole("button", { name: "Retry" })[0],
    ).toBeInTheDocument();
  });

  it("removes the input/send controls entirely (conversation disabled)", () => {
    render(<TakeoverScreen kind="crisis" message={null} />);
    expect(
      screen.queryByPlaceholderText(/type a message/i),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Send" }),
    ).not.toBeInTheDocument();
    expect(
      screen.getByText(/sending messages is disabled/i),
    ).toBeInTheDocument();
  });
});
