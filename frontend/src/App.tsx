import { useState } from "react";
import "./App.css";
import { useChatSession } from "./hooks/useChatSession";

function App() {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [inputText, setInputText] = useState("");
  const { messages, send, isLoading, crisisTriggered, error } =
    useChatSession(sessionId);

  function handleSend() {
    if (!inputText.trim()) return;
    send(inputText);
    setInputText("");
  }
  if (crisisTriggered) {
    return (
      <div className="crisis-overlay">
        <h2>You deserve support right now</h2>
      </div>
    );
  }
  return (
    <div>
      {/*Disclaimer*/}
      <div className="disclaimer">
        This is a research prototype. It does not provide clinical advice, diagnosis, or treatment.
      </div>
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
