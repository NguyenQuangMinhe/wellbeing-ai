// TODO: session storage or local storage?
import { useState } from "react";
 
export const DISCLAIMER_STORAGE_KEY = "wellbeing_disclaimer_ack";
 
function readAckedSessionId(): string | null {
  try {
    return localStorage.getItem(DISCLAIMER_STORAGE_KEY);
  } catch {
    // storage unavailable: treat as never acknowledged
    return null;
  }
}
 
// Acknowledgement is tied to one conversation (its session_id), so a fresh
// conversation always gets a fresh gate.
export function useDisclaimerAck(sessionId: string) {
  const [ackedSessionId, setAckedSessionId] = useState<string | null>(readAckedSessionId);
  const acknowledged = ackedSessionId === sessionId;
 
  function acknowledge() {
    setAckedSessionId(sessionId);
    try {
      localStorage.setItem(DISCLAIMER_STORAGE_KEY, sessionId);
    } catch {
      // storage unavailable: the gate still closes for this page load,
      // it will simply show again next visit
    }
  }
 
  return { acknowledged, acknowledge };
}
