"use client";

import { useEffect, useState } from "react";
import { AppLayout } from "@/components/sidebar/app-layout";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Loader2, RefreshCw } from "lucide-react";
import { cn } from "@/lib/utils";

interface LogEntry {
  timestamp: string;
  level: "INFO" | "WARNING" | "ERROR" | "DEBUG";
  logger: string;
  message: string;
  event?: string;
}

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "ERROR" | "WARNING">("all");

  const load = () => {
    setIsLoading(true);
    api
      .get<LogEntry[]>("/health/logs")
      .then(setLogs)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const filtered = filter === "all" ? logs : logs.filter((l) => l.level === filter);

  const levelColor = (level: string) => {
    switch (level) {
      case "ERROR": return "destructive";
      case "WARNING": return "warning";
      case "INFO": return "secondary";
      default: return "outline";
    }
  };

  return (
    <AppLayout requiredRole="admin">
      <div className="p-6 flex flex-col gap-4 h-full">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Application Logs</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Structured application and ingestion logs
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center rounded-md border overflow-hidden">
              {(["all", "ERROR", "WARNING"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={cn(
                    "px-3 py-1.5 text-xs font-medium transition-colors",
                    filter === f
                      ? "bg-primary text-white"
                      : "hover:bg-muted"
                  )}
                >
                  {f === "all" ? "All" : f}
                </button>
              ))}
            </div>
            <Button variant="outline" size="sm" onClick={load} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
            </Button>
          </div>
        </div>

        {isLoading && logs.length === 0 ? (
          <div className="flex items-center justify-center flex-1">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <ScrollArea className="flex-1 border rounded-lg">
            <div className="font-mono text-xs">
              {filtered.map((log, i) => (
                <div
                  key={i}
                  className={cn(
                    "flex items-start gap-3 px-4 py-2 border-b last:border-0",
                    log.level === "ERROR" && "bg-red-50",
                    log.level === "WARNING" && "bg-yellow-50"
                  )}
                >
                  <span className="text-muted-foreground shrink-0 w-40">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </span>
                  <Badge variant={levelColor(log.level)} className="shrink-0 text-[10px]">
                    {log.level}
                  </Badge>
                  <span className="text-muted-foreground shrink-0 w-32 truncate" title={log.logger}>
                    {log.logger}
                  </span>
                  <span className="flex-1 break-all">{log.event ?? log.message}</span>
                </div>
              ))}
              {filtered.length === 0 && (
                <div className="px-4 py-8 text-center text-muted-foreground">
                  No log entries
                </div>
              )}
            </div>
          </ScrollArea>
        )}
      </div>
    </AppLayout>
  );
}
