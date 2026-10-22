// Implement
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi } from "vitest";
import { ReportFlag } from "../src/components/ReportFlag";
import * as client from "../src/api/client";

function renderReportFlag() {
  const result = render(
    <ReportFlag
      sessionId="test-session"
      messageId="test-message"
      messageText="Test message"
    />,
  );
  fireEvent.click(screen.getByRole("button", { name: "Report message" }));
  return result;
}

describe("toggleReason", () => {
  it("adds a reason when it is not selected", () => {
    renderReportFlag();

    const checkbox = screen.getByRole("checkbox", {
      name: "Unhelpful",
    });

    fireEvent.click(checkbox);

    expect(checkbox).toBeChecked();
  });

  it("removes a reason when it is already selected", () => {
    renderReportFlag();

    const checkbox = screen.getByRole("checkbox", {
      name: "Unhelpful",
    });

    fireEvent.click(checkbox);
    expect(checkbox).toBeChecked();

    fireEvent.click(checkbox);
    expect(checkbox).not.toBeChecked();
  });

  it("allows multiple reasons to be selected", () => {
    renderReportFlag();

    const unhelpful = screen.getByRole("checkbox", {
      name: "Unhelpful",
    });
    const inaccurate = screen.getByRole("checkbox", {
      name: "Inaccurate or Misleading",
    });

    fireEvent.click(unhelpful);
    fireEvent.click(inaccurate);

    expect(unhelpful).toBeChecked();
    expect(inaccurate).toBeChecked();
  });

  it("removes only the clicked reason", () => {
    renderReportFlag();

    const unhelpful = screen.getByRole("checkbox", {
      name: "Unhelpful",
    });
    const inaccurate = screen.getByRole("checkbox", {
      name: "Inaccurate or Misleading",
    });

    fireEvent.click(unhelpful);
    fireEvent.click(inaccurate);
    fireEvent.click(unhelpful);

    expect(unhelpful).not.toBeChecked();
    expect(inaccurate).toBeChecked();
  });

  it("allows a reason to be selected again after removal", () => {
    renderReportFlag();

    const checkbox = screen.getByRole("checkbox", {
      name: "Unhelpful",
    });

    fireEvent.click(checkbox);
    fireEvent.click(checkbox);
    fireEvent.click(checkbox);

    expect(checkbox).toBeChecked();
  });

  it("does not select unrelated reasons", () => {
    renderReportFlag();

    const unhelpful = screen.getByRole("checkbox", {
      name: "Unhelpful",
    });
    const inaccurate = screen.getByRole("checkbox", {
      name: "Inaccurate or Misleading",
    });

    fireEvent.click(unhelpful);

    expect(unhelpful).toBeChecked();
    expect(inaccurate).not.toBeChecked();
  });
});
describe("ReportFlag submission", () => {
  it("submits a report with an empty description", async () => {
    const sendFeedbackSpy = vi
      .spyOn(client, "sendFeedback")
      .mockResolvedValue({ status: "success" });

    renderReportFlag();

    // Select a reason
    fireEvent.click(screen.getByRole("checkbox", { name: "Unhelpful" }));

    // Leave the description empty and submit
    fireEvent.click(screen.getByRole("button", { name: /submit report/i }));

    await waitFor(() => {
      expect(sendFeedbackSpy).toHaveBeenCalledWith(
        "test-session",
        expect.objectContaining({
          messageId: "test-message",
          messageText: "Test message",
          category: ["Unhelpful"],
          additional: "",
        }),
      );
    });
  });

  it("does not submit a report when no reason is selected", () => {
    const sendFeedbackSpy = vi
      .spyOn(client, "sendFeedback")
      .mockResolvedValue({ status: "success" });

    renderReportFlag();
    sendFeedbackSpy.mockClear();

    const submitButton = screen.getByRole("button", {
      name: /submit report/i,
    });

    expect(submitButton).toBeDisabled();
    expect(sendFeedbackSpy).not.toHaveBeenCalled();

    sendFeedbackSpy.mockRestore();
  });
});
