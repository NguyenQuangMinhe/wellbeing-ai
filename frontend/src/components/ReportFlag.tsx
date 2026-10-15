"use client";

import { useEffect, useRef, useState  } from "react";
import type { ReportFlagProps } from "../types/chat";
import { sendFeedback } from "../api/client";
const REPORT_REASONS = [
  "Inaccurate or Misleading",
  "Unhelpful",
  "Inappropriate",
  "Not CBT Structure",
];
type ReportStatus = "idle" | "success" | "error";


export function ReportFlag({sessionId, messageId, messageText}: ReportFlagProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedReasons, setSelectedReasons] = useState<string[]>([]);
  const [comments, setComments] = useState("");
  const [status, setStatus] = useState<ReportStatus>("idle");

  function toggleReason(reason: string) {
    setSelectedReasons((previous) =>
      previous.includes(reason)
        ? previous.filter((item) => item !== reason)
        : [...previous, reason]
    );
  }
const triggerRef = useRef<HTMLButtonElement>(null);
const dialogRef = useRef<HTMLDivElement>(null);
async function handleSubmit() {
    if (selectedReasons.length === 0) return;

    const report = {messageId, messageText, reasons: selectedReasons, additional: comments.trim(),};

    setStatus("idle");

    try {
      await sendFeedback(sessionId, report);
      setStatus("success");
    } catch {
      setStatus("error");
    }
  }
  useEffect(() => {
  if (!isOpen) return;

  const dialog = dialogRef.current;
  if (!dialog) return;

  const getFocusableElements = () =>
    Array.from(
      dialog.querySelectorAll<HTMLElement>(
        'button:not([disabled]), input:not([disabled]), textarea:not([disabled]), select:not([disabled]), a[href], [tabindex]:not([tabindex="-1"])'
      )
    ).filter((element) => element.getAttribute("aria-hidden") !== "true");

  // Move focus into the popup when it opens.
  const focusable = getFocusableElements();
  (focusable[0] ?? dialog).focus();

  function handleKeyDown(event: KeyboardEvent) {
    if (event.key === "Escape") {
      event.preventDefault();
      handleClose();
      return;
    }

    if (event.key !== "Tab") return;

    const elements = getFocusableElements();

    if (elements.length === 0) {
      event.preventDefault();
      dialog?.focus();
      return;
    }

    const first = elements[0];
    const last = elements[elements.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  }

  dialog.addEventListener("keydown", handleKeyDown);

  return () => {
    dialog.removeEventListener("keydown", handleKeyDown);
  };
}, [isOpen]);

  function handleClose() {
    setIsOpen(false);
    setSelectedReasons([]);
    setComments("");
    setStatus("idle");

    triggerRef.current?.focus();
  }

  return (
    <>
      {/* Report flag button */}
      <button
        ref={triggerRef}
        type="button"
        aria-label="Report message"
        title="Report message"
        onClick={() => setIsOpen(true)}
        className="
          ml-2 inline-flex shrink-0 items-center justify-center
          rounded-md border border-transparent p-1
          text-yellow-600
          transition-all duration-150
          hover:scale-105 hover:border-yellow-500
          hover:bg-yellow-50 hover:text-yellow-700
          focus-visible:outline-none
          focus-visible:ring-2 focus-visible:ring-yellow-500
          focus-visible:ring-offset-2
        "
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M4 22V4" />
          <path d="M4 4c6-4 10 4 16 0v12c-6 4-10-4-16 0" />
        </svg>
      </button>

      {/* Report popup */}
      {isOpen && (
        <div
          className="
            fixed inset-0 z-50 flex items-center
            justify-center bg-black/40 p-4
          "
          onClick={handleClose}
        >
          <div
            ref={dialogRef}
            role="dialog"
            aria-modal="true"
            aria-labelledby="report-title"
            className="
              w-full max-w-md rounded-xl bg-white p-6
              shadow-xl
            "
            onClick={(event) => event.stopPropagation()}
          >
            {status === "success" ? (
                // Success confirmation
                <div className="py-6 text-center text-gray-800">
                  <p className="font-bold text-lg">
                    Message reported
                  </p>
                  <p className="mt-2 text-gray-600">
                    Thank you for helping improve our support system.
                  </p>

                  <button
                    type="button"
                    onClick={handleClose}
                    className="mt-5 rounded-md bg-blue-600 px-4 py-2
                              text-sm font-medium text-white
                              hover:bg-blue-700
                              focus-visible:outline-none
                              focus-visible:ring-2
                              focus-visible:ring-blue-500"
                  >
                    Done
                  </button>
                </div>
              ) : status === "error" ? (
                // Error confirmation
                <div className="py-6 text-center text-gray-800">
                  <p className="font-bold text-lg">
                    Message reporting Error
                  </p>
                  <p className="mt-2 text-gray-600">
                    Sorry for the inconvenience try again later.
                  </p>

                  <button
                    type="button"
                    onClick={handleClose}
                    className="mt-5 rounded-md bg-blue-600 px-4 py-2
                              text-sm font-medium text-white
                              hover:bg-blue-700
                              focus-visible:outline-none
                              focus-visible:ring-2
                              focus-visible:ring-blue-500"
                  >
                    Done
                  </button>
                </div>
              ) : (
                //Normal
              <>
                <div className="flex items-start justify-between">
                  <div>
                    <h2
                      id="report-title"
                      className="text-lg font-bold text-gray-800"
                    >
                      Report message
                    </h2>
                    <p className="font-bold text-sm text-gray-500">
                      Why are you flagging this message?
                    </p>
                  </div>

                  <button
                    type="button"
                    aria-label="Close report dialog"
                    onClick={handleClose}
                    className="
                      rounded-md p-1 text-gray-500
                      hover:bg-gray-100 hover:text-gray-900
                      focus-visible:outline-none
                      focus-visible:ring-2 focus-visible:ring-blue-500
                    "
                  >
                    ✕
                  </button>
                </div>

                <div className="mt-5 space-y-3 text-sm text-gray-800">
                  {REPORT_REASONS.map((reason) => (
                    <label
                      key={reason}
                      className="
                        flex cursor-pointer items-center gap-3
                        rounded-md border border-gray-200 p-3
                        text-sm text-gray-700
                        hover:border-yellow-400 hover:bg-yellow-50
                      "
                    >
                      <input
                        type="checkbox"
                        checked={selectedReasons.includes(reason)}
                        onChange={() => toggleReason(reason)}
                        className="
                          h-4 w-4 rounded border-gray-300
                          accent-yellow-500
                          focus-visible:ring-2
                          focus-visible:ring-yellow-500
                        "
                      />
                      {reason}
                    </label>
                  ))}
                </div>

                <div className="mt-5">
                  <label
                    htmlFor={`report-details-${messageId}`}
                    className="block text-sm font-medium text-gray-700"
                  >
                    Additional details{" "}
                    <span className="font-normal text-gray-400">
                      (optional)
                    </span>
                  </label>

                  <textarea
                    id={`report-details-${messageId}`}
                    value={comments}
                    onChange={(event) => setComments(event.target.value)}
                    placeholder="Tell us more if needed..."
                    rows={3}
                    maxLength={1000}
                    className="
                      mt-2 w-full resize-y rounded-md
                      border border-gray-300 p-3 text-sm
                      text-gray-900 placeholder:text-gray-400
                      focus:border-yellow-500 focus:outline-none
                      focus:ring-2 focus:ring-yellow-200
                    "
                  />
                </div>

                <div className="mt-6 flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={handleClose}
                    className="
                      bg-red-600 rounded-md border border-gray-300 p-2 
                      text-sm font-medium text-white-medium
                      hover:scale-105
                      focus-visible:outline-none
                      focus-visible:ring-2 focus-visible:ring-red-400
                    "
                  >
                    Cancel
                  </button>

                  <button
                    type="button"
                    onClick={handleSubmit}
                    disabled={selectedReasons.length === 0}
                    className="
                      rounded-md bg-blue-600 p-2
                      text-sm font-semibold text-white-medium
                      hover:scale-105
                      disabled:cursor-not-allowed
                      disabled:opacity-50
                      focus-visible:outline-none
                      focus-visible:ring-2
                    "
                  >
                    Submit report
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}