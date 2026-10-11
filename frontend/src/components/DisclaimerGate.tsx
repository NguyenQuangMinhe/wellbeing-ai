import { useEffect, useRef } from "react";


export const DISCLAIMER_COPY = {
  heading: "Ai Chat Support Acknowledgement",
  paragraphs: [
    "Before proceeding, please acknowledge you are speaking with an unlicensed Ai Support assistant",
    "- This Assistant is backed by the CBT structure of collaborative and reflecting.",
    "- This is not an emergency service and is unable to diagnose or provide medication.",
  ],
  button: "I understand",
} as const;

export function DisclaimerGate({ onAcknowledge }: { onAcknowledge: () => void }) {
  const buttonRef = useRef<HTMLButtonElement>(null);

  // Move focus into the gate on mount so keyboard and screen reader users land on it
  useEffect(() => {
    buttonRef.current?.focus();
  }, []);

  return (
    <div
      className="fixed inset-0 z-40 flex items-center justify-center bg-black/50 p-4"
      onKeyDown={(e) => {
        // The button is the only focusable control, so keep focus on it.
        // Escape is deliberately not handled: this gate must be acknowledged.
        if (e.key === "Tab") {
          e.preventDefault();
          buttonRef.current?.focus();
        }
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="disclaimer-heading"
        aria-describedby="disclaimer-body"
        className="w-full max-w-md rounded border-2 border-gray-500 bg-gray-300 p-6 text-center"
      >
        <h2 id="disclaimer-heading" className="text-lg font-bold text-gray-800 font-style: italic">
          {DISCLAIMER_COPY.heading}
        </h2>

        <div id="disclaimer-body" className="mt-3 space-y-2 text-sm text-gray-600">
          {DISCLAIMER_COPY.paragraphs.map((text) => (
            <p key={text}>{text}</p>
          ))}
        </div>

        <button
          ref={buttonRef}
          type="button"
          onClick={onAcknowledge}
          className="mt-5 w-full rounded bg-blue-600 p-3 font-medium text-white hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-600"
        >
          {DISCLAIMER_COPY.button}
        </button>
      </div>
    </div>
  );
}
