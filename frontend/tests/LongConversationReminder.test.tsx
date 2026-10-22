// TODO
import { render, screen, fireEvent } from "@testing-library/react";
import { describe, it, expect } from "vitest";
import { LongConversationReminder } from "../src/components/LongConversationReminder";

describe("LongConversationReminder", () => {
  it("renders the reminder when visible is true", () => {
    render(<LongConversationReminder visible={true} />);

    expect(
      screen.getByText(
        "Remember, AI support is not a replacement for professional support.",
      ),
    ).toBeInTheDocument();
  });

  it("does not render the reminder when visible is false", () => {
    render(<LongConversationReminder visible={false} />);

    expect(
      screen.queryByText(
        "Remember, AI support is not a replacement for professional support.",
      ),
    ).not.toBeInTheDocument();
  });

  it("dismisses the reminder when the dismiss button is clicked", () => {
    render(<LongConversationReminder visible={true} />);

    const dismissButton = screen.getByRole("button", {
      name: "Dismiss AI support reminder",
    });

    fireEvent.click(dismissButton);

    expect(
      screen.queryByText(
        "Remember, AI support is not a replacement for professional support.",
      ),
    ).not.toBeInTheDocument();
  });

  it("does not show the reminder again when visible remains true after dismissal", () => {
    render(<LongConversationReminder visible={true} />);

    fireEvent.click(
      screen.getByRole("button", {
        name: "Dismiss AI support reminder",
      }),
    );

    expect(
      screen.queryByRole("button", {
        name: "Dismiss AI support reminder",
      }),
    ).not.toBeInTheDocument();

    expect(
      screen.queryByText(
        "Remember, AI support is not a replacement for professional support.",
      ),
    ).not.toBeInTheDocument();
  });

  it("shows the reminder when visible changes from false to true", () => {
    const { rerender } = render(<LongConversationReminder visible={false} />);

    expect(
      screen.queryByRole("button", {
        name: "Dismiss AI support reminder",
      }),
    ).not.toBeInTheDocument();

    rerender(<LongConversationReminder visible={true} />);

    expect(
      screen.getByRole("button", {
        name: "Dismiss AI support reminder",
      }),
    ).toBeInTheDocument();
  });
});
