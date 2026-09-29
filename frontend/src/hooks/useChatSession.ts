import { useState, useEffect } from "react";
import { sendMessage, clearHistory, getHistory } from "../api/client";
import type { ChatResponse } from "../types/chat";

type Message = {
  role: "user" | "system";
  text: string;
  risk?: "low" | "medium" | "high";
};

export function useChatSession(sessionId: string) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [crisisTriggered, setCrisisTriggered] = useState(false);
  const [crisisMessage, setCrisisMessage] = useState<string | null>(null);
  const [boundaryTriggered, setBoundaryTriggered] = useState(false);
  const [boundaryMessage, setBoundaryMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadHistory() {
      try {
        const history = await getHistory(sessionId);
        const restored: Message[] = history.flatMap((entry) => [
          { role: "user" as const, text: entry.user_message },
          { role: "system" as const, text: entry.system_message, risk: entry.risk_level },
        ]);
        setMessages(restored);
      } catch {
        // no history yet, or backend unreachable — start with an empty chat, not an error
      }
    }
    loadHistory();
  }, [sessionId]);

  async function send(text: string) {
    setMessages((prev) => [...prev, { role: "user", text }]);
    setIsLoading(true);
    setError(null);

    try {
      const data: ChatResponse = await sendMessage({
        session_id: sessionId,
        message: text,
      });
      console.log("data message:", data.message);
      if (data.risk_level === "high") {
        if (data.type === "crisis") {
          setCrisisTriggered(true);
          setCrisisMessage(data.message);
        } else if (data.type === "boundary") {
          setBoundaryTriggered(true);
          setBoundaryMessage(data.message);
        }
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "system", text: data.message, risk: data.risk_level },
        ]);
      }

      if (data.end_session) {
        setCrisisTriggered(true);
      }
    } catch (err) {
      setError(
        "We couldn't generate a response right now. Please try again later. Sorry for the inconvenience.",
      );
    } finally {
      setIsLoading(false);
    }
  }
  async function clear() {
    await clearHistory(sessionId);
    setMessages([]);
    setCrisisTriggered(false);
    setCrisisMessage(null);
    setBoundaryTriggered(false);
    setBoundaryMessage(null);
    setError(null);
  }

  return {
    messages,
    send,
    clear,
    isLoading,
    crisisTriggered,
    crisisMessage,
    boundaryTriggered,
    boundaryMessage,
    error,
  };
}
