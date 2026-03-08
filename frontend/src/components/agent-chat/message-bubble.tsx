"use client";

import { StreamingText } from "./streaming-text";
import type { ChatMessage } from "@/types";
import { cn } from "@/lib/utils";
import { User, Bot } from "lucide-react";

interface MessageBubbleProps {
  message: ChatMessage;
  isStreaming?: boolean;
}

export function MessageBubble({ message, isStreaming = false }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={cn("flex gap-3", isUser && "flex-row-reverse")}>
      {/* Avatar */}
      <div
        className={cn(
          "flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full",
          isUser ? "bg-primary text-white" : "bg-gray-100 text-gray-600"
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      {/* Content */}
      <div
        className={cn(
          "flex flex-col gap-2 max-w-[80%]",
          isUser && "items-end"
        )}
      >
        {/* Text */}
        <div
          className={cn(
            "rounded-2xl px-4 py-2 text-sm",
            isUser
              ? "bg-primary text-white rounded-tr-sm"
              : "bg-gray-100 text-gray-900 rounded-tl-sm"
          )}
        >
          {isUser ? (
            message.content
          ) : (
            <StreamingText text={message.content} isStreaming={isStreaming} />
          )}
        </div>

        {/* SQL block */}
        {message.sql && (
          <div className="w-full rounded-lg overflow-hidden border border-gray-200">
            <div className="px-3 py-1.5 bg-gray-800 text-xs text-gray-400 font-mono flex items-center justify-between">
              <span>Generated SQL</span>
            </div>
            <pre className="px-3 py-2 text-xs font-mono bg-gray-900 text-green-400 overflow-x-auto whitespace-pre-wrap">
              {message.sql}
            </pre>
          </div>
        )}

        {/* Results preview */}
        {message.result && message.result.rows.length > 0 && (
          <div className="w-full rounded-lg overflow-hidden border border-gray-200">
            <div className="px-3 py-1.5 bg-gray-50 border-b text-xs text-muted-foreground">
              {message.result.row_count} rows • {message.result.execution_time_ms}ms
            </div>
            <div className="overflow-auto max-h-40">
              <table className="w-full text-xs">
                <thead>
                  <tr className="bg-gray-50 border-b">
                    {message.result.columns.map((col) => (
                      <th
                        key={col}
                        className="px-2 py-1 text-left font-medium text-muted-foreground"
                      >
                        {col}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {message.result.rows.slice(0, 10).map((row, i) => (
                    <tr key={i} className="border-b last:border-0 hover:bg-muted/30">
                      {message.result!.columns.map((col) => (
                        <td key={col} className="px-2 py-1">
                          {String(row[col] ?? "")}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <span className="text-[10px] text-muted-foreground px-1">
          {new Date(message.created_at).toLocaleTimeString()}
        </span>
      </div>
    </div>
  );
}
