import { useState, useRef, useEffect } from "react";
import { useChatSession } from "./hooks/useChatSession";
import { TakeoverScreen } from "./components/Takeover";

type DeleteStatus = "idle" | "confirming" | "loading" | "error" | "success";

function App() {
  const [sessionId] = useState(() => {
    const existing = localStorage.getItem("wellbeing_session_id");
    if (existing) return existing;
    const newId = crypto.randomUUID();
    localStorage.setItem("wellbeing_session_id", newId);
    return newId;
  });
  const [inputText, setInputText] = useState("");
  const [deleteStatus, setDeleteStatus] = useState<DeleteStatus>("idle");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const [menuOpen, setMenuOpen] = useState(false);
  const [isTimedOut, setIsTimedOut] = useState(false);

  const {
    messages,
    send,
    clear,
    isLoading,
    crisisTriggered,
    crisisMessage,
    boundaryTriggered,
    boundaryMessage,
    error,
  } = useChatSession(sessionId);

  const takeoverActive = crisisTriggered || boundaryTriggered;

  useEffect(() => {
    if (!takeoverActive) textareaRef.current?.focus();
  }, [isLoading, takeoverActive]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  useEffect(() => {
    //May need to send to backend instead
    if (!isLoading) {
      setIsTimedOut(false);
      return;
    }
    const timer = setTimeout(() => setIsTimedOut(true), 15000);
    return () => clearTimeout(timer);
  }, [isLoading]);

  function handleSend() {
    if (!inputText.trim() || isLoading || takeoverActive) return;
    send(inputText);
    setInputText("");
  }

  async function handleConfirmDelete() {
    setDeleteStatus("loading");
    try {
      await clear();
      setDeleteStatus("success");
    } catch {
      setDeleteStatus("error");
    }
  }
  if (takeoverActive) {
    return (
      <TakeoverScreen
        kind={crisisTriggered ? "crisis" : "boundary"}
        message={
          crisisTriggered
            ? crisisMessage
            : boundaryTriggered
              ? boundaryMessage
              : null
        }
      />
    );
  }

  return (
    <div className="flex h-screen w-full flex-col bg-white">
      {/* Disclaimer */}
      <div className="sticky top-0 z-10 bg-gray-100 p-2 text-sm text-gray-600 text-center">
        <span className="font-semibold">Disclaimer: </span>
        You are chatting with an AI, not a proffessional clinician
      </div>

      {/* Header / Delete History */}
      <div className="relative flex items-center justify-end border-b border-gray-200 px-2 py-1.5">
        <button
          type="button"
          onClick={() => setMenuOpen((open) => !open)}
          aria-haspopup="menu"
          aria-expanded={menuOpen}
          className="rounded p-2 text-gray-600 hover:bg-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth={2}
            strokeLinecap="round"
            className="h-5 w-5"
          >
            <line x1="4" y1="6" x2="20" y2="6" />
            <line x1="4" y1="12" x2="20" y2="12" />
            <line x1="4" y1="18" x2="20" y2="18" />
          </svg>
        </button>

        {menuOpen && (
          <div
            role="menu"
            className="absolute right-2 top-full z-10 mt-1 w-40 rounded-md border border-gray-200 bg-white py-1 shadow-lg"
          >
            <button
              type="button"
              role="menuitem"
              onClick={() => {
                setMenuOpen(false);
                setDeleteStatus("confirming");
              }}
              className="w-full rounded px-3 py-1.5 text-left text-xs text-red-600 hover:bg-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500"
            >
              Delete history
            </button>
          </div>
        )}
      </div>

      {deleteStatus !== "idle" && (
        <div className="fixed inset-0 z-20 flex items-center justify-center bg-black/30 p-2">
          <div className="w-full max-w-xs rounded-md bg-white p-4 shadow-lg">
            {/* Confirmation dialog */}
            <p className="flex items-center justify-center p-2 text-center text-sm text-gray-800">
              {deleteStatus === "error"
                ? "Sorry, an error has occurred."
                : deleteStatus === "success"
                  ? "Conversation history deleted."
                  : "Delete conversation history permanently?"}
            </p>
            <div className="mt-3 flex items-center justify-center gap-2">
              {deleteStatus === "success" ? (
                <button
                  type="button"
                  onClick={() => setDeleteStatus("idle")}
                  className="rounded p-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500"
                >
                  Done
                </button>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => setDeleteStatus("idle")}
                    disabled={deleteStatus === "loading"}
                    className="rounded p-2 text-sm text-gray-700 hover:bg-gray-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-gray-400 disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleConfirmDelete}
                    disabled={deleteStatus === "loading"}
                    className="rounded bg-red-500 p-2 text-sm text-white hover:bg-red-600 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-red-500 disabled:opacity-50"
                  >
                    {deleteStatus === "loading"
                      ? "Deleting…"
                      : deleteStatus === "error"
                        ? "Try again"
                        : "Delete"}
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Chat area */}
      <div className="flex flex-1 flex-col overflow-y-auto p-4">
        {messages.length === 0 && !isLoading && (
          <div className="m-auto text-center text-sm text-gray-400">
            Start the conversation whenever you're ready.
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={i}
            className={`mb-2 flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[75%] rounded-md p-2 text-sm ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-100 text-gray-800"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}

        {isLoading && !isTimedOut && (
          <div className="mb-2 flex justify-start">
            <div className="flex items-center gap-1.5 rounded-md bg-gray-100 p-2 text-sm text-gray-400">
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.3s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400 [animation-delay:-0.15s]" />
              <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-gray-400" />
              <span className="ml-2 whitespace-pre-line">
                {"\nThroughout our conversation I am unable to provide any medication advice,\n" +
                  "diagnosis or crisis response. I am able to provide assistance to feelings,\n" +
                  "thoughts and actions."}
              </span>
            </div>
          </div>
        )}

        {isLoading && isTimedOut && (
          <div className="mb-2 flex justify-start">
            <div className="rounded-md border border-amber-200 bg-amber-50 p-2 text-sm text-amber-700">
              This is taking longer than expected. Still waiting on a response…
            </div>
          </div>
        )}

        {error && (
          <div className="mt-2 rounded-md border border-red-200 bg-red-50 p-2 text-sm text-red-600">
            {error}
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input area */}
      <div className="flex items-end gap-2 border-t border-gray-200 p-2">
        <textarea
          ref={textareaRef}
          value={inputText}
          disabled={isLoading}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          placeholder="Type a message…"
          rows={1}
          className="flex-1 resize-none rounded-md border border-gray-300 p-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:bg-gray-50 disabled:text-gray-400"
        />
        {/* Send Button */}
        <button
          type="button"
          onClick={handleSend}
          disabled={!inputText.trim() || isLoading}
          className="rounded p-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 disabled:bg-gray-300 disabled:text-gray-500"
        >
          Send
        </button>
      </div>
    </div>
  );
}

export default App;
