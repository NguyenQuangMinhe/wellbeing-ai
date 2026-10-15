"use client";

import { useState } from "react";

type LongConversationReminderProps = {
  // Set this from your conversation-length logic.
  visible: boolean;
};

export function LongConversationReminder({
  visible,
}: LongConversationReminderProps) {
  const [dismissed, setDismissed] = useState(false);

  if (!visible || dismissed) {
    return null;
  }

  return (
    <div className="mt-2 flex w-full items-start gap-2 text-sm text-gray-500">
      <p className="min-w-0 flex-1 break-words">
        Remember, AI support is not a replacement for professional support.
      </p>

      <button
        type="button"
        aria-label="Dismiss AI support reminder"
        title="Dismiss reminder"
        onClick={() => setDismissed(true)}
        className="inline-flex h-6 w-6 shrink-0 items-center justify-center
                   rounded bg-red-500 text-white
                   hover:bg-red-600
                   focus-visible:outline-none
                   focus-visible:ring-2 focus-visible:ring-red-400
                   focus-visible:ring-offset-2"
      >
        <span aria-hidden="true">×</span>
      </button>
    </div>
  );
}
