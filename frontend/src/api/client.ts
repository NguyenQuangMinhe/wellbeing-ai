import type { ChatRequest, ChatResponse } from "../types/chat";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

export async function sendMessage(payload: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/message`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
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
