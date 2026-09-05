export type ChatRequest = {
  session_id: string;
  message: string;
};

export type ChatResponse = {
  type: "normal" | "crisis" | "error";
  message: string;
  risk_level: "low" | "medium" | "high";
  end_session: boolean;
};
