"use client";

import { useEffect, useState } from "react";
import { AppLayout } from "@/components/sidebar/app-layout";
import { ChatInterface } from "@/components/agent-chat/chat-interface";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { ChatSession, ChatMessage } from "@/types";
import { Plus, MessageSquare, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

export default function AgentPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    api
      .get<ChatSession[]>("/agent/sessions")
      .then((data) => {
        setSessions(data);
        if (data.length > 0) {
          setActiveSession(data[0]);
        }
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  useEffect(() => {
    if (!activeSession) return;
    api
      .get<ChatMessage[]>(`/agent/sessions/${activeSession.id}/messages`)
      .then(setMessages)
      .catch(console.error);
  }, [activeSession]);

  const handleNewSession = async () => {
    try {
      const session = await api.post<ChatSession>("/agent/sessions");
      setSessions((prev) => [session, ...prev]);
      setActiveSession(session);
      setMessages([]);
    } catch (err) {
      console.error("Failed to create session:", err);
    }
  };

  const handleSessionCreated = (session: ChatSession) => {
    setSessions((prev) => {
      const exists = prev.find((s) => s.id === session.id);
      if (exists) return prev;
      return [session, ...prev];
    });
    setActiveSession(session);
    setMessages([]);
  };

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="flex h-screen overflow-hidden">
        {/* Session sidebar */}
        <div className="w-56 border-r flex flex-col shrink-0">
          <div className="px-3 py-3 border-b flex items-center justify-between">
            <p className="text-sm font-semibold">Sessions</p>
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7"
              onClick={handleNewSession}
              title="New session"
            >
              <Plus className="h-4 w-4" />
            </Button>
          </div>
          <ScrollArea className="flex-1">
            <div className="py-2 px-2 space-y-1">
              {sessions.length === 0 && (
                <p className="text-xs text-muted-foreground px-2 py-4 text-center">
                  No sessions yet
                </p>
              )}
              {sessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => setActiveSession(session)}
                  className={cn(
                    "flex items-center gap-2 w-full px-2 py-2 rounded-md text-left text-sm hover:bg-muted/50 transition-colors",
                    activeSession?.id === session.id && "bg-muted"
                  )}
                >
                  <MessageSquare className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                  <span className="truncate">
                    {session.title || `Session ${session.id}`}
                  </span>
                </button>
              ))}
            </div>
          </ScrollArea>
        </div>

        {/* Chat area */}
        <div className="flex-1 overflow-hidden">
          {activeSession ? (
            <ChatInterface
              sessionId={activeSession.id}
              initialMessages={messages}
              onNewSession={handleSessionCreated}
            />
          ) : (
            <div className="flex flex-col items-center justify-center h-full gap-4">
              <MessageSquare className="h-12 w-12 text-muted-foreground" />
              <div className="text-center">
                <h3 className="text-lg font-medium">Start a conversation</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Ask questions about your healthcare data in plain English
                </p>
              </div>
              <Button onClick={handleNewSession}>
                <Plus className="h-4 w-4 mr-2" />
                New Session
              </Button>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
