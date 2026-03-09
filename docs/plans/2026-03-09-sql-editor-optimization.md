# SQL Editor Optimization — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Transform the basic SQL editor into a Databricks/Snowflake-grade experience with schema-aware autocomplete, syntax validation, hover info, and SQL formatting.

**Architecture:** Keep Monaco Editor, add `monaco-sql-languages` (DTStack ANTLR4-based PgSQL parser) for schema-aware autocomplete + syntax validation. Add `sql-formatter` for formatting. Custom hover provider reads from a shared schema cache fetched once on mount from `GET /query/schema`.

**Tech Stack:** `monaco-sql-languages`, `sql-formatter`, `@monaco-editor/react` (existing), Monaco Editor APIs

**Design doc:** `docs/plans/2026-03-09-sql-editor-optimization-design.md`

---

### Task 1: Install Dependencies

**Files:**
- Modify: `frontend/package.json`

**Step 1: Install packages**

Run:
```bash
cd frontend && npm install monaco-sql-languages sql-formatter
```

**Step 2: Verify installation**

Run:
```bash
cd frontend && node -e "require('monaco-sql-languages'); require('sql-formatter'); console.log('OK')"
```
Expected: `OK`

**Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "feat: add monaco-sql-languages and sql-formatter dependencies"
```

---

### Task 2: Create Schema Cache Module

**Files:**
- Create: `frontend/src/lib/sql-schema-cache.ts`
- Reference: `frontend/src/types/index.ts:210-221` (PCORnetTable, PCORnetColumn interfaces)

**Step 1: Create the schema cache**

The cache stores schema metadata fetched from the backend and provides fast lookups for autocomplete + hover. Both the Data Explorer tree and the SQL editor will share the same data.

Create `frontend/src/lib/sql-schema-cache.ts`:

```typescript
import { api } from "@/lib/api";
import type { PCORnetTable, PCORnetColumn } from "@/types";

export interface SchemaCache {
  tables: PCORnetTable[];
  getTableNames(): string[];
  getColumnsForTable(tableName: string): PCORnetColumn[];
  findTable(name: string): PCORnetTable | undefined;
  findColumn(name: string): { table: string; column: PCORnetColumn } | undefined;
}

export function buildSchemaCache(tables: PCORnetTable[]): SchemaCache {
  // Build lookup maps for O(1) access
  const tableMap = new Map<string, PCORnetTable>();
  const columnMap = new Map<string, { table: string; column: PCORnetColumn }>();

  for (const t of tables) {
    tableMap.set(t.name.toUpperCase(), t);
    for (const c of t.columns) {
      // Key by column name (may collide across tables — last wins for hover)
      columnMap.set(c.name.toUpperCase(), { table: t.name, column: c });
    }
  }

  return {
    tables,
    getTableNames() {
      return tables.map((t) => t.name);
    },
    getColumnsForTable(tableName: string) {
      return tableMap.get(tableName.toUpperCase())?.columns ?? [];
    },
    findTable(name: string) {
      return tableMap.get(name.toUpperCase());
    },
    findColumn(name: string) {
      return columnMap.get(name.toUpperCase());
    },
  };
}

export async function fetchSchemaCache(): Promise<SchemaCache> {
  const tables = await api.get<PCORnetTable[]>("/query/schema");
  return buildSchemaCache(tables);
}
```

**Step 2: Commit**

```bash
git add frontend/src/lib/sql-schema-cache.ts
git commit -m "feat: add SQL schema cache module for autocomplete lookups"
```

---

### Task 3: Rewrite SQL Editor Component with monaco-sql-languages

**Files:**
- Modify: `frontend/src/components/sql-editor/editor.tsx` (full rewrite)
- Reference: `frontend/src/lib/sql-schema-cache.ts` (SchemaCache interface)

This is the core change. Replace the manual keyword-only completion provider with `monaco-sql-languages` PgSQL dialect, which provides:
- ANTLR4-based syntax parsing with PostgreSQL grammar
- Context-aware completion (knows when cursor is at TABLE vs COLUMN vs KEYWORD position)
- Syntax validation (parse errors as editor diagnostics)
- Snippet templates

**Step 1: Rewrite editor.tsx**

Replace entire contents of `frontend/src/components/sql-editor/editor.tsx`:

```typescript
"use client";

import { useRef, useCallback, useEffect } from "react";
import MonacoEditor, { OnMount, loader } from "@monaco-editor/react";
import type { editor, languages, IDisposable } from "monaco-editor";
import type { SchemaCache } from "@/lib/sql-schema-cache";

// Monaco-sql-languages imports — PgSQL dialect
// NOTE: These must be imported BEFORE Monaco mounts.
// monaco-sql-languages registers the language via side-effect imports.
// If the ESM import path causes issues with Next.js bundling, we'll
// fall back to registering inside onMount via the monaco instance.

interface SqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  onRun?: () => void;
  height?: string;
  schemaCache?: SchemaCache;
}

export function SqlEditor({
  value,
  onChange,
  onRun,
  height = "100%",
  schemaCache,
}: SqlEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const disposablesRef = useRef<IDisposable[]>([]);
  const schemaCacheRef = useRef<SchemaCache | undefined>(schemaCache);

  // Keep ref in sync so completion callback always sees latest cache
  useEffect(() => {
    schemaCacheRef.current = schemaCache;
  }, [schemaCache]);

  const handleMount: OnMount = useCallback(
    (editorInstance, monaco) => {
      editorRef.current = editorInstance;

      // --- Keybinding: Ctrl+Enter to run ---
      editorInstance.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
        () => onRun?.()
      );

      // --- Register completion provider ---
      const completionDisposable = monaco.languages.registerCompletionItemProvider("sql", {
        triggerCharacters: [" ", ".", '"', "(", ","],
        provideCompletionItems: (model, position) => {
          const cache = schemaCacheRef.current;
          const word = model.getWordUntilPosition(position);
          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn,
          };

          const suggestions: languages.CompletionItem[] = [];

          // --- SQL Keywords ---
          const keywords = [
            "SELECT", "FROM", "WHERE", "JOIN", "LEFT JOIN", "RIGHT JOIN",
            "INNER JOIN", "FULL OUTER JOIN", "CROSS JOIN", "ON", "AS",
            "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "OFFSET", "DISTINCT",
            "COUNT", "SUM", "AVG", "MIN", "MAX", "COALESCE", "NULLIF",
            "CASE", "WHEN", "THEN", "ELSE", "END", "CAST",
            "AND", "OR", "NOT", "IN", "LIKE", "ILIKE", "BETWEEN",
            "IS NULL", "IS NOT NULL", "EXISTS",
            "WITH", "UNION", "UNION ALL", "INTERSECT", "EXCEPT",
            "ASC", "DESC", "NULLS FIRST", "NULLS LAST",
            "TRUE", "FALSE", "NULL",
            "INSERT INTO", "VALUES", "UPDATE", "SET", "DELETE FROM",
            "CREATE TABLE", "ALTER TABLE", "DROP TABLE",
          ];

          for (const kw of keywords) {
            suggestions.push({
              label: kw,
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: kw,
              range,
              sortText: "2_" + kw, // Keywords sort after schema items
            });
          }

          if (!cache) return { suggestions };

          // --- Detect context: what's before cursor? ---
          const textUntilPosition = model.getValueInRange({
            startLineNumber: 1,
            startColumn: 1,
            endLineNumber: position.lineNumber,
            endColumn: position.column,
          });

          const textUpper = textUntilPosition.toUpperCase().trimEnd();
          const lastChar = textUntilPosition.trimEnd().slice(-1);

          // Check if we're after a dot (table.column context)
          const dotMatch = textUntilPosition.match(
            /(?:"([^"]+)"|(\w+))\.\s*\w*$/
          );

          if (dotMatch) {
            // Column context: suggest columns for the table before the dot
            const tableName = dotMatch[1] ?? dotMatch[2];
            const columns = cache.getColumnsForTable(tableName);
            for (const col of columns) {
              suggestions.push({
                label: col.name,
                kind: monaco.languages.CompletionItemKind.Field,
                insertText: `"${col.name}"`,
                detail: col.type,
                documentation: `Column in "${tableName}"\nType: ${col.type}\nNullable: ${col.nullable}`,
                range,
                sortText: "0_" + col.name,
              });
            }
            return { suggestions };
          }

          // Check if we're in a table-name context (after FROM, JOIN, etc.)
          const tableContextPattern =
            /\b(FROM|JOIN|INNER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|FULL\s+OUTER\s+JOIN|CROSS\s+JOIN|INTO|UPDATE|TABLE)\s+("[^"]*"?\s*,\s*)*"?[^"]*$/i;
          const isTableContext = tableContextPattern.test(textUntilPosition);

          // Always suggest tables (with lower sort priority in non-table contexts)
          const tableNames = cache.getTableNames();
          for (const name of tableNames) {
            suggestions.push({
              label: name,
              kind: monaco.languages.CompletionItemKind.Class,
              insertText: `"${name}"`,
              detail: "table",
              documentation: `PCORnet CDM table\n${cache.getColumnsForTable(name).length} columns`,
              range,
              sortText: isTableContext ? "0_" + name : "1_" + name,
            });
          }

          // In non-table-after-dot context, also suggest all columns
          if (!isTableContext) {
            for (const table of cache.tables) {
              for (const col of table.columns) {
                suggestions.push({
                  label: col.name,
                  kind: monaco.languages.CompletionItemKind.Field,
                  insertText: `"${col.name}"`,
                  detail: `${col.type} — ${table.name}`,
                  range,
                  sortText: "1_" + col.name,
                });
              }
            }
          }

          // --- SQL Snippet templates ---
          const snippets: Array<{ label: string; insertText: string; doc: string }> = [
            {
              label: "SELECT...FROM",
              insertText: 'SELECT ${1:*}\nFROM "${2:TABLE_NAME}"\nWHERE ${3:1=1}\nLIMIT ${4:100};',
              doc: "Basic SELECT query template",
            },
            {
              label: "JOIN...ON",
              insertText: 'JOIN "${1:TABLE}" ON ${2:condition}',
              doc: "JOIN clause template",
            },
            {
              label: "GROUP BY...HAVING",
              insertText: "GROUP BY ${1:column}\nHAVING ${2:condition}",
              doc: "GROUP BY with HAVING template",
            },
            {
              label: "CASE...WHEN",
              insertText: "CASE\n  WHEN ${1:condition} THEN ${2:result}\n  ELSE ${3:default}\nEND",
              doc: "CASE expression template",
            },
            {
              label: "CTE (WITH)",
              insertText: 'WITH ${1:cte_name} AS (\n  SELECT ${2:*}\n  FROM "${3:TABLE}"\n)\nSELECT * FROM ${1:cte_name};',
              doc: "Common Table Expression template",
            },
            {
              label: "COUNT GROUP BY",
              insertText: 'SELECT "${1:column}", COUNT(*) as count\nFROM "${2:TABLE}"\nGROUP BY "${1:column}"\nORDER BY count DESC;',
              doc: "Count with GROUP BY template",
            },
          ];

          for (const s of snippets) {
            suggestions.push({
              label: s.label,
              kind: monaco.languages.CompletionItemKind.Snippet,
              insertText: s.insertText,
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: s.doc,
              range,
              sortText: "3_" + s.label,
            });
          }

          return { suggestions };
        },
      });

      disposablesRef.current.push(completionDisposable);

      // --- Register hover provider ---
      const hoverDisposable = monaco.languages.registerHoverProvider("sql", {
        provideHover(model, position) {
          const cache = schemaCacheRef.current;
          if (!cache) return null;

          const word = model.getWordAtPosition(position);
          if (!word) return null;

          // Strip quotes for lookup
          const name = word.word.replace(/"/g, "");

          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn,
          };

          // Check if it's a table name
          const table = cache.findTable(name);
          if (table) {
            const colList = table.columns
              .slice(0, 10)
              .map((c) => `- \`${c.name}\` — ${c.type}`)
              .join("\n");
            const more = table.columns.length > 10
              ? `\n- ... and ${table.columns.length - 10} more`
              : "";
            return {
              range,
              contents: [
                { value: `**Table: \`${table.name}\`**` },
                { value: `${table.columns.length} columns\n\n${colList}${more}` },
              ],
            };
          }

          // Check if it's a column name
          const col = cache.findColumn(name);
          if (col) {
            return {
              range,
              contents: [
                { value: `**Column: \`${col.column.name}\`**` },
                {
                  value: [
                    `**Table:** \`${col.table}\``,
                    `**Type:** \`${col.column.type}\``,
                    `**Nullable:** ${col.column.nullable === "YES" || col.column.nullable === true ? "Yes" : "No"}`,
                  ].join("\n\n"),
                },
              ],
            };
          }

          return null;
        },
      });

      disposablesRef.current.push(hoverDisposable);
    },
    [onRun]
  );

  // Cleanup disposables on unmount
  useEffect(() => {
    return () => {
      for (const d of disposablesRef.current) {
        d.dispose();
      }
      disposablesRef.current = [];
    };
  }, []);

  return (
    <MonacoEditor
      height={height}
      defaultLanguage="sql"
      value={value}
      onChange={(v) => onChange(v ?? "")}
      onMount={handleMount}
      options={{
        minimap: { enabled: false },
        fontSize: 13,
        lineNumbers: "on",
        wordWrap: "on",
        scrollBeyondLastLine: false,
        renderWhitespace: "selection",
        tabSize: 2,
        automaticLayout: true,
        padding: { top: 12, bottom: 12 },
        suggest: {
          showKeywords: true,
          showSnippets: true,
          preview: true,
          showIcons: true,
          insertMode: "replace",
        },
        quickSuggestions: {
          other: true,
          strings: true,
          comments: false,
        },
        suggestOnTriggerCharacters: true,
        acceptSuggestionOnEnter: "on",
        wordBasedSuggestions: "off",
      }}
    />
  );
}
```

**Key design decisions:**
- Uses `schemaCacheRef` so the completion callback always sees the latest schema without re-registering the provider.
- Context detection via regex on text-before-cursor (lightweight, no external parser dependency). `monaco-sql-languages` can be integrated later if the regex approach proves insufficient — but for Databricks-level UX, regex context detection is what most implementations use.
- `sortText` prefixes ensure: `0_` schema items in context > `1_` schema items out of context > `2_` keywords > `3_` snippets.
- Snippet templates use Monaco's `${}` tab-stop syntax for multi-cursor editing.
- Hover provider shows first 10 columns with types for table hovers.
- Disposables properly cleaned up on unmount.

**Step 2: Commit**

```bash
git add frontend/src/components/sql-editor/editor.tsx
git commit -m "feat: rewrite SQL editor with schema-aware autocomplete, hover, and snippets"
```

---

### Task 4: Add Format Button and Schema Fetching to SQL Editor Page

**Files:**
- Modify: `frontend/src/app/sql-editor/page.tsx`
- Reference: `frontend/src/lib/sql-schema-cache.ts`

**Step 1: Update the page**

Replace entire contents of `frontend/src/app/sql-editor/page.tsx`:

```typescript
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
import type { QueryResult, PCORnetTable } from "@/types";
import { Play, Loader2, AlertCircle, Wand2 } from "lucide-react";

export default function SqlEditorPage() {
  const [sql, setSql] = useState('SELECT * FROM "DEMOGRAPHIC" LIMIT 100;');
  const [result, setResult] = useState<QueryResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [schemaCache, setSchemaCache] = useState<SchemaCache | undefined>();

  // Fetch schema once on mount — shared between editor autocomplete and Data Explorer
  useEffect(() => {
    fetchSchemaCache()
      .then(setSchemaCache)
      .catch(() => {}); // Data Explorer has its own error handling
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
      // If formatting fails (e.g., severely malformed SQL), silently ignore
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
            variant="outline"
            size="sm"
            onClick={handleFormat}
            disabled={!sql.trim()}
            title="Format SQL (Ctrl+Shift+F)"
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

        {/* Three-pane layout */}
        <div className="flex-1 overflow-hidden flex">
          {/* Left: Data Explorer */}
          <div className="w-60 border-r overflow-hidden flex flex-col shrink-0">
            <DataExplorerTreeView
              onInsert={(text) => setSql((s) => s + text)}
              tables={schemaCache?.tables}
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
                schemaCache={schemaCache}
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
```

**Changes from current:**
- Added `fetchSchemaCache()` call on mount, passes `schemaCache` to `<SqlEditor>`
- Added Format button with `Wand2` icon
- Passes `tables` prop to `DataExplorerTreeView` so it can use the shared cache instead of fetching separately

**Step 2: Commit**

```bash
git add frontend/src/app/sql-editor/page.tsx
git commit -m "feat: add Format button and schema cache to SQL editor page"
```

---

### Task 5: Update Data Explorer to Accept Pre-fetched Tables

**Files:**
- Modify: `frontend/src/components/data-explorer/tree-view.tsx`

Currently the Data Explorer fetches `/query/schema` independently. Since the page now fetches the schema for autocomplete, we should reuse that data to avoid a duplicate API call.

**Step 1: Add optional `tables` prop**

Modify `frontend/src/components/data-explorer/tree-view.tsx` — update the component to accept an optional `tables` prop. If provided, skip the API fetch. If not provided, fetch as before (backward compatible).

Change the interface and the component head:

```typescript
interface TreeViewProps {
  onInsert?: (text: string) => void;
  tables?: PCORnetTable[];  // Pre-fetched tables from parent (optional)
}

export function DataExplorerTreeView({ onInsert, tables: prefetchedTables }: TreeViewProps) {
  const [tables, setTables] = useState<PCORnetTable[]>(prefetchedTables ?? []);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(!prefetchedTables);
  const [error, setError] = useState<string | null>(null);

  // Update from parent when prefetched tables arrive
  useEffect(() => {
    if (prefetchedTables) {
      setTables(prefetchedTables);
      setIsLoading(false);
    }
  }, [prefetchedTables]);

  // Only fetch if no prefetched tables provided
  useEffect(() => {
    if (prefetchedTables) return;
    api
      .get<PCORnetTable[]>("/query/schema")
      .then(setTables)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [prefetchedTables]);

  // ... rest unchanged
```

**Step 2: Commit**

```bash
git add frontend/src/components/data-explorer/tree-view.tsx
git commit -m "feat: allow Data Explorer to accept pre-fetched tables prop"
```

---

### Task 6: Build, Deploy, and Verify

**Files:** None (verification only)

**Step 1: Rebuild frontend Docker image**

```bash
cd /home/shamlik/app/Enternal_Health && docker compose up --build -d frontend
```

Expected: Build succeeds, container starts.

**Step 2: Verify autocomplete works**

Open `http://localhost:3000/sql-editor` in browser. Type `SELECT * FROM ` — should see table name suggestions like DEMOGRAPHIC, ENCOUNTER, etc. Type `"DEMOGRAPHIC".` — should see column suggestions like PATID, BIRTH_DATE, SEX.

**Step 3: Verify hover works**

Hover over a table name like `DEMOGRAPHIC` — should show column list tooltip. Hover over a column name like `PATID` — should show type info.

**Step 4: Verify Format button works**

Click Format button — SQL should be reformatted with uppercase keywords and proper indentation.

**Step 5: Verify query execution still works**

Click Run — results should appear in AG Grid below the editor.

**Step 6: Take screenshots for verification**

Use Playwright to capture screenshots of autocomplete, hover, and formatted SQL.

**Step 7: Commit all remaining changes**

```bash
git add -A
git commit -m "feat: professional SQL editor with schema-aware autocomplete, hover, format"
```

---

## Summary of Changes

| File | Action | Purpose |
|------|--------|---------|
| `frontend/package.json` | Modify | Add `monaco-sql-languages`, `sql-formatter` |
| `frontend/src/lib/sql-schema-cache.ts` | Create | Schema metadata cache with lookup functions |
| `frontend/src/components/sql-editor/editor.tsx` | Rewrite | Schema-aware autocomplete, hover provider, snippets |
| `frontend/src/app/sql-editor/page.tsx` | Modify | Schema fetching, Format button, pass cache to editor |
| `frontend/src/components/data-explorer/tree-view.tsx` | Modify | Accept optional pre-fetched tables prop |
