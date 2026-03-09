"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { ChevronRight, ChevronDown, Table2, Columns, Loader2 } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import type { PCORnetTable } from "@/types";
import { cn } from "@/lib/utils";

interface TreeViewProps {
  onInsert?: (text: string) => void;
  tables?: PCORnetTable[];
}

export function DataExplorerTreeView({ onInsert, tables: prefetchedTables }: TreeViewProps) {
  const [tables, setTables] = useState<PCORnetTable[]>(prefetchedTables ?? []);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const [isLoading, setIsLoading] = useState(!prefetchedTables);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (prefetchedTables) {
      setTables(prefetchedTables);
      setIsLoading(false);
    }
  }, [prefetchedTables]);

  useEffect(() => {
    if (prefetchedTables) return;
    api
      .get<PCORnetTable[]>("/query/schema")
      .then(setTables)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [prefetchedTables]);

  const toggle = (tableName: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(tableName)) {
        next.delete(tableName);
      } else {
        next.add(tableName);
      }
      return next;
    });
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full p-4">
        <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-xs text-red-600">{error}</div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="px-3 py-2 border-b">
        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
          PCORnet CDM v7.0
        </p>
      </div>
      <ScrollArea className="flex-1">
        <div className="py-1">
          {tables.map((table) => (
            <TableNode
              key={table.name}
              table={table}
              expanded={expanded.has(table.name)}
              onToggle={() => toggle(table.name)}
              onInsert={onInsert}
            />
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}

function TableNode({
  table,
  expanded,
  onToggle,
  onInsert,
}: {
  table: PCORnetTable;
  expanded: boolean;
  onToggle: () => void;
  onInsert?: (text: string) => void;
}) {
  return (
    <div>
      <button
        onClick={onToggle}
        className="flex items-center gap-1.5 w-full px-3 py-1 text-left hover:bg-muted/50 text-sm"
      >
        {expanded ? (
          <ChevronDown className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
        ) : (
          <ChevronRight className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
        )}
        <Table2 className="h-3.5 w-3.5 text-primary shrink-0" />
        <span
          className="font-medium truncate cursor-pointer hover:text-primary"
          onDoubleClick={() => onInsert?.(`"${table.name}"`)}
          title="Double-click to insert"
        >
          {table.name}
        </span>
      </button>
      {expanded && (
        <div className="pl-8">
          {table.columns.map((col) => (
            <button
              key={col.name}
              onClick={() => onInsert?.(`"${col.name}"`)}
              className={cn(
                "flex items-center gap-1.5 w-full px-3 py-0.5 text-left hover:bg-muted/50 text-xs",
                "text-muted-foreground hover:text-foreground"
              )}
              title={`${col.type}${col.nullable ? " (nullable)" : ""}`}
            >
              <Columns className="h-3 w-3 shrink-0" />
              <span className="truncate">{col.name}</span>
              <span className="ml-auto shrink-0 text-muted-foreground/60">{col.type}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
