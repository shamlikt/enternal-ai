"use client";

import { useRef, useCallback } from "react";
import MonacoEditor, { OnMount } from "@monaco-editor/react";
import type { editor } from "monaco-editor";

interface SqlEditorProps {
  value: string;
  onChange: (value: string) => void;
  onRun?: () => void;
  height?: string;
}

export function SqlEditor({ value, onChange, onRun, height = "100%" }: SqlEditorProps) {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);

  const handleMount: OnMount = useCallback(
    (editorInstance, monaco) => {
      editorRef.current = editorInstance;

      // Ctrl+Enter to run query
      editorInstance.addCommand(
        monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter,
        () => {
          onRun?.();
        }
      );

      // SQL keywords for basic autocomplete
      const sqlKeywords = [
        "SELECT", "FROM", "WHERE", "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN",
        "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "OFFSET", "DISTINCT",
        "COUNT", "SUM", "AVG", "MIN", "MAX", "AS", "ON", "AND", "OR", "NOT",
        "IN", "LIKE", "BETWEEN", "IS NULL", "IS NOT NULL", "CASE", "WHEN",
        "THEN", "ELSE", "END", "WITH", "UNION", "INTERSECT", "EXCEPT",
      ];

      monaco.languages.registerCompletionItemProvider("sql", {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        provideCompletionItems: (model: any, position: any) => {
          const word = model.getWordUntilPosition(position);
          const range = {
            startLineNumber: position.lineNumber,
            endLineNumber: position.lineNumber,
            startColumn: word.startColumn,
            endColumn: word.endColumn,
          };
          return {
            suggestions: sqlKeywords.map((kw) => ({
              label: kw,
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: kw,
              range,
            })),
          };
        },
      });
    },
    [onRun]
  );

  const insertText = useCallback((text: string) => {
    const editor = editorRef.current;
    if (!editor) return;
    const selection = editor.getSelection();
    if (!selection) return;
    editor.executeEdits("", [
      {
        range: selection,
        text,
        forceMoveMarkers: true,
      },
    ]);
    editor.focus();
  }, []);

  // Expose insertText via ref-like pattern
  (editorRef as unknown as { insertText: typeof insertText }).insertText = insertText;

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
        },
      }}
    />
  );
}
