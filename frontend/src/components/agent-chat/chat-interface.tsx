"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { MessageBubble } from "./message-bubble";
import { AgentWebSocket } from "@/lib/websocket";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ChatMessage, ChatSession } from "@/types";
import { Send, Loader2, RefreshCw } from "lucide-react";

interface AgentWSMessage {
  type: "token" | "sql" | "result" | "done" | "error";
  content?: string;
  sql?: string;
  result?: ChatMessage["result"];
  error?: string;
  message_id?: number;
}

interface ChatInterfaceProps {
  sessionId: number;
  initialMessages: ChatMessage[];
  onNewSession: (session: ChatSession) => void;
}

export function ChatInterface({
  sessionId,
  initialMessages,
  onNewSession,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingMessageId, setStreamingMessageId] = useState<number | null>(null);

  const wsRef = useRef<AgentWebSocket | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    setMessages(initialMessages);
  }, [initialMessages]);

  useEffect(() => {
    const ws = new AgentWebSocket();
    wsRef.current = ws;

    ws.onOpen(() => setIsConnected(true));
    ws.onClose(() => setIsConnected(false));

    ws.onMessage((data) => {
      const msg = data as AgentWSMessage;

      switch (msg.type) {
        case "token":
          setMessages((prev) =>
            prev.map((m) =>
              m.id === streamingMessageId
                ? { ...m, content: m.content + (msg.content ?? "") }
                : m
            )
          );
          break;

        case "sql":
          setMessages((prev) =>
            prev.map((m) =>
              m.id === streamingMessageId ? { ...m, sql: msg.sql } : m
            )
          );
          break;

        case "result":
          setMessages((prev) =>
            prev.map((m) =>
              m.id === streamingMessageId ? { ...m, result: msg.result } : m
            )
          );
          break;

        case "done":
          setIsStreaming(false);
          setStreamingMessageId(null);
          break;

        case "error":
          setIsStreaming(false);
          setStreamingMessageId(null);
          setMessages((prev) =>
            prev.map((m) =>
              m.id === streamingMessageId
                ? { ...m, content: msg.error ?? "An error occurred." }
                : m
            )
          );
          break;
      }
    });

    ws.connect(sessionId);
    return () => ws.disconnect();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || isStreaming) return;

    setInput("");
    setIsStreaming(true);

    const userMessage: ChatMessage = {
      id: Date.now(),
      session_id: sessionId,
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };

    const assistantMessage: ChatMessage = {
      id: Date.now() + 1,
      session_id: sessionId,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);
    setStreamingMessageId(assistantMessage.id);

    if (isConnected) {
      wsRef.current?.send({ query: text, session_id: sessionId });
    } else {
      // Fallback to REST
      try {
        const response = await api.post<ChatMessage>("/agent/query", {
          query: text,
          session_id: sessionId,
        });
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMessage.id ? response : m
          )
        );
      } catch (err) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMessage.id
              ? { ...m, content: err instanceof Error ? err.message : "Error" }
              : m
          )
        );
      } finally {
        setIsStreaming(false);
        setStreamingMessageId(null);
      }
    }
  }, [input, isStreaming, isConnected, sessionId]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleNewSession = async () => {
    try {
      const session = await api.post<ChatSession>("/agent/sessions");
      onNewSession(session);
    } catch (err) {
      console.error("Failed to create session:", err);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Connection status */}
      <div className="flex items-center justify-between px-4 py-2 border-b">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span
            className={`w-2 h-2 rounded-full ${
              isConnected ? "bg-green-400" : "bg-yellow-400"
            }`}
          />
          {isConnected ? "Connected" : "Polling mode"}
        </div>
        <Button variant="ghost" size="sm" onClick={handleNewSession} className="h-7 text-xs gap-1">
          <RefreshCw className="h-3 w-3" />
          New session
        </Button>
      </div>

      {/* Messages */}
      <ScrollArea className="flex-1 px-4 py-4">
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <p className="text-sm text-muted-foreground">
                Ask a question about your healthcare data in plain English.
                <br />
                The agent will generate and run SQL against your PCORnet CDM.
              </p>
            </div>
          )}
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              isStreaming={isStreaming && message.id === streamingMessageId}
            />
          ))}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>

      {/* Input */}
      <div className="px-4 py-3 border-t">
        <div className="flex gap-2 items-end">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your data... (Enter to send, Shift+Enter for newline)"
            rows={2}
            disabled={isStreaming}
            className="flex-1 resize-none rounded-lg border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring placeholder:text-muted-foreground disabled:opacity-50"
          />
          <Button
            onClick={sendMessage}
            disabled={!input.trim() || isStreaming}
            size="icon"
            className="shrink-0"
          >
            {isStreaming ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}
