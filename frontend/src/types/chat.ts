export type ChatRequest = {
  session_id: string;
  message: string;
};

export type ChatResponse = {
  type: "normal" | "crisis" | "error" | "boundary";
  message: string;
  risk_level: "low" | "medium" | "high";
  end_session: boolean;
};
export type HistoryEntry = {
  id: number;
  session_id: string;
  user_message: string;
  system_message: string;
  response_type: "normal" | "boundary" | "crisis" | "error";
  risk_level: "low" | "medium" | "high";
  created_at: string;
};