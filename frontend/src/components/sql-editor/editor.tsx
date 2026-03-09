"use client";

import { useRef, useCallback, useEffect } from "react";
import MonacoEditor, { OnMount } from "@monaco-editor/react";
import type { editor, languages, IDisposable } from "monaco-editor";
import type { SchemaCache } from "@/lib/sql-schema-cache";

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
  const onRunRef = useRef(onRun);

  useEffect(() => {
    schemaCacheRef.current = schemaCache;
  }, [schemaCache]);

  useEffect(() => {
    onRunRef.current = onRun;
  }, [onRun]);

  const handleMount: OnMount = useCallback(
    (editorInstance, monaco) => {
      editorRef.current = editorInstance;

      editorInstance.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
        () => onRunRef.current?.()
      );

      const completionDisposable = monaco.languages.registerCompletionItemProvider("sql", {
        triggerCharacters: [" ", ".", '"', "(", ","],
        provideCompletionItems: (model: editor.ITextModel, position: { lineNumber: number; column: number }) => {
          const cache = schemaCacheRef.current;
          const word = model.getWordUntilPosition(position);
          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn,
          };

          const suggestions: languages.CompletionItem[] = [];

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
          ];

          for (const kw of keywords) {
            suggestions.push({
              label: kw,
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: kw,
              range,
              sortText: "2_" + kw,
            });
          }

          if (!cache) return { suggestions };

          const textUntilPosition = model.getValueInRange({
            startLineNumber: 1,
            startColumn: 1,
            endLineNumber: position.lineNumber,
            endColumn: position.column,
          });

          const dotMatch = textUntilPosition.match(
            /(?:"([^"]+)"|(\w+))\.\s*\w*$/
          );

          if (dotMatch) {
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

          const tableContextPattern =
            /\b(FROM|JOIN|INNER\s+JOIN|LEFT\s+JOIN|RIGHT\s+JOIN|FULL\s+OUTER\s+JOIN|CROSS\s+JOIN|INTO|UPDATE|TABLE)\s+("[^"]*"?\s*,\s*)*"?[^"]*$/i;
          const isTableContext = tableContextPattern.test(textUntilPosition);

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

      const hoverDisposable = monaco.languages.registerHoverProvider("sql", {
        provideHover(model: editor.ITextModel, position: { lineNumber: number; column: number }) {
          const cache = schemaCacheRef.current;
          if (!cache) return null;

          const word = model.getWordAtPosition(position);
          if (!word) return null;

          const name = word.word.replace(/"/g, "");

          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn,
          };

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
                    `**Nullable:** ${col.column.nullable ? "Yes" : "No"}`,
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
    []
  );

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
