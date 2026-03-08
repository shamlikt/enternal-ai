"use client";

import { useState, useCallback } from "react";
import { AppLayout } from "@/components/sidebar/app-layout";
import { SqlEditor } from "@/components/sql-editor/editor";
import { ResultsTable } from "@/components/sql-editor/results-table";
import { DataExplorerTreeView } from "@/components/data-explorer/tree-view";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import type { QueryResult } from "@/types";
import { Play, Loader2, AlertCircle } from "lucide-react";

export default function SqlEditorPage() {
  const [sql, setSql] = useState("SELECT * FROM DEMOGRAPHIC LIMIT 100;");
  const [result, setResult] = useState<QueryResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runQuery = useCallback(async () => {
    if (!sql.trim()) return;
    setIsRunning(true);
    setError(null);
    try {
      const res = await api.post<QueryResult>("/query/execute", { sql });
      setResult(res);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Query failed");
      setResult(null);
    } finally {
      setIsRunning(false);
    }
  }, [sql]);

  return (
    <AppLayout>
      <div className="flex flex-col h-screen">
        {/* Toolbar */}
        <div className="flex items-center gap-3 px-4 py-2 border-b bg-white shrink-0">
          <h1 className="text-sm font-semibold">SQL Editor</h1>
          <div className="flex-1" />
          <kbd className="hidden sm:inline-flex text-xs text-muted-foreground px-2 py-0.5 border rounded">
            Ctrl+Enter to run
          </kbd>
          <Button
            size="sm"
            onClick={runQuery}
            disabled={isRunning || !sql.trim()}
          >
            {isRunning ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            Run
          </Button>
        </div>

        {/* Three-pane layout */}
        <div className="flex-1 overflow-hidden flex">
          {/* Left: Data Explorer */}
          <div className="w-60 border-r overflow-hidden flex flex-col shrink-0">
            <DataExplorerTreeView
              onInsert={(text) => setSql((s) => s + text)}
            />
          </div>

          {/* Right: Editor + Results stacked */}
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Monaco Editor */}
            <div className="flex-1 overflow-hidden" style={{ minHeight: "200px" }}>
              <SqlEditor
                value={sql}
                onChange={setSql}
                onRun={runQuery}
              />
            </div>
            <div className="h-px bg-border shrink-0" />
            {/* Results */}
            <div className="overflow-hidden flex flex-col shrink-0" style={{ height: "280px" }}>
              {error && (
                <div className="flex items-center gap-2 px-4 py-2 bg-red-50 text-sm text-red-700 border-b shrink-0">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {error}
                </div>
              )}
              <div className="flex-1 overflow-hidden">
                <ResultsTable result={result} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
