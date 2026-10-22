import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, it, expect, vi, beforeEach } from "vitest";
import * as client from "../src/api/client";
import App from "../src/App";

vi.mock("../src/api/client", async (importOriginal) => {
  const actual = await importOriginal<typeof import("../src/api/client")>();

  return {
    ...actual,
    sendMessage: vi.fn(),
    getHistory: vi.fn().mockResolvedValue([]),
    getSessionStatus: vi.fn().mockResolvedValue({ locked: false }),
  };
});

beforeEach(() => {
  vi.clearAllMocks();
});
it("sends an English message normally", async () => {
  vi.mocked(client.sendMessage).mockResolvedValue({
    type: "normal",
    message: "Thank you for sharing that.",
    risk_level: "low",
    end_session: false,
  });

  const user = userEvent.setup();
  render(<App />);

  // Acknowledge the disclaimer if it appears.
  const acknowledge = screen.queryByRole("button", {
    name: /i understand/i,
  });

  if (acknowledge) {
    await user.click(acknowledge);
  }

  const input = screen.getByPlaceholderText(/type a message/i);
  await user.type(
    input,
    "I have been feeling stressed about university lately.",
  );

  await user.click(screen.getByRole("button", { name: /send/i }));

  await waitFor(() => {
    expect(client.sendMessage).toHaveBeenCalledWith(
      expect.objectContaining({
        message: "I have been feeling stressed about university lately.",
      }),
    );
  });

  expect(
    await screen.findByText("Thank you for sharing that."),
  ).toBeInTheDocument();
});
it("shows a warning", async () => {
  vi.mocked(client.sendMessage).mockResolvedValue({
    type: "non-english",
    message:
      "I'm currently only able to support English. Please share your thoughts and feelings in English, and I'll do my best to help.",
    risk_level: "low",
    end_session: false,
  });

  const user = userEvent.setup();
  render(<App />);

  const acknowledge = screen.queryByRole("button", {
    name: /i understand/i,
  });

  if (acknowledge) {
    await user.click(acknowledge);
  }

  const rejectedMessage = "Tôi cảm thấy rất căng thẳng về việc học đại học.";

  const input = screen.getByPlaceholderText(/type a message/i);
  await user.type(input, rejectedMessage);
  await user.click(screen.getByRole("button", { name: /send/i }));

  expect(
    await screen.findByText(/only able to support english/i),
  ).toBeInTheDocument();
  expect(
    screen.queryByText(
      "I'm currently only able to support English. Please share your thoughts and feelings in English, and I'll do my best to help.",
    ),
  ).toBeInTheDocument();
});
