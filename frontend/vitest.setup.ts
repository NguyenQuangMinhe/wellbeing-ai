import "@testing-library/jest-dom";
import { vi } from "vitest";

Element.prototype.scrollIntoView = vi.fn();
import { beforeEach } from "vitest";

beforeEach(() => {
  localStorage.setItem("wellbeing_session_id", "test-session");
  localStorage.setItem("wellbeing_disclaimer_ack", "test-session");
});
