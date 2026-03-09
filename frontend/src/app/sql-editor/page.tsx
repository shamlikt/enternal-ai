"use client";

import { useState, useCallback, useEffect } from "react";
import { AppLayout } from "@/components/sidebar/app-layout";
import { SqlEditor } from "@/components/sql-editor/editor";
import { ResultsTable } from "@/components/sql-editor/results-table";
import { DataExplorerTreeView } from "@/components/data-explorer/tree-view";
import { api } from "@/lib/api";
import { fetchSchemaCache, type SchemaCache } from "@/lib/sql-schema-cache";
import { format as formatSql } from "sql-formatter";
import { Button } from "@/components/ui/button";
import type { QueryResult } from "@/types";
import { Play, Loader2, AlertCircle, Wand2 } from "lucide-react";

export default function SqlEditorPage() {
  const [sql, setSql] = useState('SELECT * FROM "DEMOGRAPHIC" LIMIT 100;');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [schemaCache, setSchemaCache] = useState<SchemaCache | undefined>();

  useEffect(() => {
    fetchSchemaCache()
      .then(setSchemaCache)
      .catch(() => {});
  }, []);

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

  const handleFormat = useCallback(() => {
    try {
      const formatted = formatSql(sql, {
        language: "postgresql",
        tabWidth: 2,
        keywordCase: "upper",
        linesBetweenQueries: 2,
      });
      setSql(formatted);
    } catch {
      // If formatting fails, silently ignore
    }
  }, [sql]);

  return (
    <AppLayout>
      <div className="flex flex-col h-screen">
        <div className="flex items-center gap-3 px-4 py-2 border-b bg-white shrink-0">
          <h1 className="text-sm font-semibold">SQL Editor</h1>
          <div className="flex-1" />
          <kbd className="hidden sm:inline-flex text-xs text-muted-foreground px-2 py-0.5 border rounded">
            Ctrl+Enter to run
          </kbd>
          <Button
            variant="outline"
            size="sm"
            onClick={handleFormat}
            disabled={!sql.trim()}
            title="Format SQL"
          >
            <Wand2 className="h-4 w-4 mr-2" />
            Format
          </Button>
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

        <div className="flex-1 overflow-hidden flex">
          <div className="w-60 border-r overflow-hidden flex flex-col shrink-0">
            <DataExplorerTreeView
              onInsert={(text) => setSql((s) => s + text)}
              tables={schemaCache?.tables}
            />
          </div>

          <div className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 overflow-hidden" style={{ minHeight: "200px" }}>
              <SqlEditor
                value={sql}
                onChange={setSql}
                onRun={runQuery}
                schemaCache={schemaCache}
              />
            </div>
            <div className="h-px bg-border shrink-0" />
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
