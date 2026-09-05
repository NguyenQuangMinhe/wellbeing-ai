import { useState } from "react";
import { sendMessage } from "../api/client";
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
  const [error, setError] = useState<string | null>(null);

  async function send(text: string) {
    setMessages((prev) => [...prev, { role: "user", text }]);
    setIsLoading(true);
    setError(null);

    try {
      const data: ChatResponse = await sendMessage({
        session_id: sessionId,
        message: text,
      });

      if (data.type === "crisis") {
        setCrisisTriggered(true);
        setCrisisMessage(data.message);
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
      setError("The assistant is unavailable right now. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }

  return { messages, send, isLoading, crisisTriggered, crisisMessage, error };
}
