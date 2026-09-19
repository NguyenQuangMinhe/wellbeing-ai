import { useState, useRef, useEffect } from "react";
import "./App.css";
import { useChatSession } from "./hooks/useChatSession";

function App() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [inputText, setInputText] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);
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

  useEffect(() => {
    textareaRef.current?.focus();
  });

  function handleSend() {
    if (!inputText.trim()) return;
    send(inputText);
    setInputText("");
  }
  function handleClear() {
    if (window.confirm("Clear this conversation? This cannot be undone.")) {
      clear();
    }
  }
  if (crisisTriggered) {
    return (
      <div className="crisis-overlay">
        <h2>You deserve support right now</h2>
        {crisisMessage && (
          <p style={{ whiteSpace: "pre-line" }}>{crisisMessage}</p>
        )}
      </div>
    );
  }
  if (boundaryTriggered) {
    return (
      <div className="boundary-overlay">
        <h2>Important Notice</h2>
        {boundaryMessage && (
          <p style={{ whiteSpace: "pre-line" }}>{boundaryMessage}</p>
        )}
      </div>
    );
  }
  return (
    <div>
      {/*Disclaimer*/}
      <div className="disclaimer">
        This is a research prototype. It does not provide clinical advice,
        diagnosis, or treatment.
      </div>
      <button onClick={handleClear} className="clear-btn">
        Clear history
      </button>
      {/*Chat area*/}
      <div className="chat-area">
        {messages.map((msg, i) => (
          <div key={i} className={`msg-row ${msg.role}`}>
            <div className="bubble">{msg.text}</div>
          </div>
        ))}
        {isLoading && <div className="typing">...</div>}
        {error && <div className="error-banner">{error}</div>}
      </div>

      {/*Input area*/}
      <div className="input-bar">
        <textarea
          ref={textareaRef}
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
        />
        <button onClick={handleSend} disabled={isLoading}>
          Send
        </button>
      </div>
    </div>
  );
}

export default App;
