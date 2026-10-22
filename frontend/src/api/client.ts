import type { ChatRequest, ChatResponse } from "../types/chat";
import type { HistoryEntry } from "../types/chat";
import type { FeedbackRequest } from "../types/chat";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function sendMessage(payload: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  console.log("sendMessage response:", response.body);

  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status}`);
  }

  return response.json();
}
export async function sendFeedback(
  sessionId: string,
  feedback: FeedbackRequest,
): Promise<{"status": "success"}> {
  const response = await fetch(`${API_BASE_URL}/api/feedback/${sessionId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message_id: feedback.messageId,
      message_text: feedback.messageText,
      category: feedback.category,
      additional: feedback.additional,
    }),
  });

  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status}`);
  }
  return response.json();
}

export async function clearHistory(
  sessionId: string,
): Promise<{ deleted: number }> {
  //await new Promise((r) => setTimeout(r, 15000));
  //throw new Error('Simulated failure');
  const response = await fetch(`${API_BASE_URL}/api/history/${sessionId}`, {
    method: "DELETE",
  });
  if (!response.ok)
    throw new Error(`Failed to clear history: ${response.status}`);
  return response.json();
}

export async function getHistory(sessionId: string): Promise<HistoryEntry[]> {
  const response = await fetch(`${API_BASE_URL}/api/history/${sessionId}`);
  if (!response.ok)
    throw new Error(`Failed to load history: ${response.status}`);
  return response.json();
}

export async function getSessionStatus(
  sessionId: string,
): Promise<{ locked: boolean }> {
  const response = await fetch(
    `${API_BASE_URL}/api/session/${sessionId}/status`,
  );
  if (!response.ok)
    throw new Error(`Failed to get session status: ${response.status}`);
  return response.json();
}
