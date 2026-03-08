"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ChartWidget } from "./chart-widgets";
import { api } from "@/lib/api";
import type { DashboardWidget, QueryResult } from "@/types";
import { Loader2, AlertCircle } from "lucide-react";

interface WidgetCardProps {
  widget: DashboardWidget;
}

export function WidgetCard({ widget }: WidgetCardProps) {
  const [data, setData] = useState<Record<string, unknown>[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!widget.sql && !widget.query_id) return;
    if (widget.widget_type === "kpi_card") return;

    setIsLoading(true);
    const promise = widget.query_id
      ? api.post<QueryResult>(`/query/saved/${widget.query_id}/run`)
      : api.post<QueryResult>("/query/execute", { sql: widget.sql });

    promise
      .then((result) => {
        setData(result.rows as Record<string, unknown>[]);
      })
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [widget.sql, widget.query_id, widget.widget_type]);

  return (
    <Card className="h-full overflow-hidden">
      <CardHeader className="pb-2 pt-3 px-4">
        <CardTitle className="text-sm font-medium">{widget.title}</CardTitle>
      </CardHeader>
      <CardContent className="px-4 pb-3">
        {isLoading && (
          <div className="flex items-center justify-center h-32">
            <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
          </div>
        )}
        {error && (
          <div className="flex items-center gap-2 text-xs text-red-600 h-32">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}
        {!isLoading && !error && (
          <ChartWidget
            type={widget.widget_type}
            data={data as { [key: string]: string | number }[]}
            config={widget.config as Parameters<typeof ChartWidget>[0]["config"]}
          />
        )}
      </CardContent>
    </Card>
  );
}
