export type ChatRequest = {
  session_id: string;
  message: string;
};

export type ChatResponse = {
  type: "normal" | "crisis" | "error" | "non-english" | "boundary";
  message: string;
  risk_level: "low" | "medium" | "high";
  end_session: boolean;
};
export type HistoryEntry = {
  id: number;
  session_id: string;
  user_message: string;
  system_message: string;
  response_type: "normal" | "boundary" | "crisis" | "error" | "non-english";
  risk_level: "low" | "medium" | "high";
  created_at: string;
};

export type ReportFlagProps = {
  sessionId: string;
  messageId: string;
  messageText: string;
};

export type FeedbackRequest = {
  messageId: string;
  messageText: string;
  category: string[];
  additional: string;
};
