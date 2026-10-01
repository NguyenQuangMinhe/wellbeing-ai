import { describe, it, expect, vi, beforeEach } from "vitest";
import { renderHook, waitFor, act, screen, render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useChatSession } from "../src/hooks/useChatSession";
import * as client from "../src/api/client";
import App from "../src/App";

describe("useChatSession", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    vi.spyOn(client, "getHistory").mockResolvedValue([]);
    vi.spyOn(client, "getSessionStatus").mockResolvedValue({ locked: false});
  });

  it("starts with isLoading false and empty messages", async () => {
    const { result } = renderHook(() => useChatSession("s1"));
    await waitFor(() => expect(result.current.messages).toEqual([]));
    expect(result.current.isLoading).toBe(false);
  });

  it("sets isLoading true while send() is in flight, then false on success", async () => {
    let resolveSend: (v: any) => void;
    vi.spyOn(client, "sendMessage").mockReturnValue(
      new Promise((resolve) => { resolveSend = resolve; })
    );

    const { result } = renderHook(() => useChatSession("s1"));
    await waitFor(() => expect(result.current.messages).toEqual([]));

    act(() => { result.current.send("hi"); });
    await waitFor(() => expect(result.current.isLoading).toBe(true));

    act(() => resolveSend!({ type: "normal", message: "hello back", risk_level: "low", end_session: false }));
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.messages).toHaveLength(2);
    expect(result.current.messages[1].text).toBe("hello back");
  });

  it("sets error state and clears isLoading on network failure", async () => {
    vi.spyOn(client, "sendMessage").mockRejectedValue(new Error("network down"));

    const { result } = renderHook(() => useChatSession("s1"));
    await waitFor(() => expect(result.current.messages).toEqual([]));

    await act(async () => { await result.current.send("hi"); });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toMatch(/couldn't generate a response/i);
  });

  it("sets crisisTriggered and crisisMessage on a crisis response", async () => {
    vi.spyOn(client, "sendMessage").mockResolvedValue({
      type: "crisis", message: "crisis resources", risk_level: "high", end_session: true,
    });

    const { result } = renderHook(() => useChatSession("s1"));
    await waitFor(() => expect(result.current.messages).toEqual([]));
    await act(async () => { await result.current.send("I want to end my life"); });

    expect(result.current.crisisTriggered).toBe(true);
    expect(result.current.crisisMessage).toBe("crisis resources");
  });

  it("restores locked status from getSessionStatus on mount", async () => {
    vi.spyOn(client, "getSessionStatus").mockResolvedValue({ locked: true});

    const { result } = renderHook(() => useChatSession("s1"));
    await waitFor(() => expect(result.current.isLoading).toBe(true));
    //expect(result.current.crisisMessage).toBe("locked message");
  });
  it("cold-start test first message is sent and received correctly", async () => {
    let resolveSend: (v:any) => void;
    vi.spyOn(client, "sendMessage").mockReturnValue(
      new Promise((resolve) => { resolveSend = resolve; })
    );
    const user = userEvent.setup();
    render(<App/>);
    const input = await screen.findByPlaceholderText(/type a message/i);

    await user.type(input, "cold start message");
    await user.click(screen.getByRole("button", { name: "Send" }));
    expect(await screen.findByText(/Your first response/)).toBeInTheDocument();
    resolveSend!({ type: "normal", message: "response to cold start", risk_level: "low", end_session:false })
    await waitFor(() => expect(screen.queryByText(/Your first response/i)).toBeInTheDocument());
  });
});