"use client";

import { useEffect, useRef, useState } from "react";
import { AppLayout } from "@/components/sidebar/app-layout";
import { api } from "@/lib/api";
import { AgGridReact } from "ag-grid-react";
import {
  ModuleRegistry,
  ClientSideRowModelModule,
  ValidationModule,
  PaginationModule,
} from "ag-grid-community";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { QuarantineRecord, QuarantineStats } from "@/types";
import { AlertTriangle, Loader2 } from "lucide-react";

ModuleRegistry.registerModules([
  ClientSideRowModelModule,
  ValidationModule,
  PaginationModule,
]);

export default function QuarantinePage() {
  const [records, setRecords] = useState<QuarantineRecord[]>([]);
  const [stats, setStats] = useState<QuarantineStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const gridRef = useRef<AgGridReact>(null);

  useEffect(() => {
    Promise.all([
      api.get<QuarantineRecord[]>("/quarantine/"),
      api.get<QuarantineStats>("/quarantine/stats"),
    ])
      .then(([recs, s]) => {
        setRecords(recs);
        setStats(s);
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  const columnDefs = [
    { field: "id", headerName: "ID", width: 80 },
    { field: "source_table", headerName: "Source Table", width: 160 },
    { field: "ingestion_run_id", headerName: "Run ID", width: 100 },
    { field: "error_message", headerName: "Error", flex: 2 },
    {
      field: "created_at",
      headerName: "Quarantined",
      width: 180,
      valueFormatter: ({ value }: { value: string }) =>
        new Date(value).toLocaleString(),
      sort: "desc" as const,
    },
  ];

  return (
    <AppLayout requiredRole="admin">
      <div className="p-6 flex flex-col gap-6 h-full">
        <div className="flex items-center gap-2">
          <AlertTriangle className="h-6 w-6 text-yellow-500" />
          <div>
            <h1 className="text-2xl font-semibold">Quarantine</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Records that failed validation during ingestion
            </p>
          </div>
        </div>

        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-1">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Total Quarantined
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold text-yellow-600">
                  {stats.total.toLocaleString()}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-1">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  By Table
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1">
                  {Object.entries(stats.by_table)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 3)
                    .map(([table, count]) => (
                      <div key={table} className="flex justify-between text-sm">
                        <span className="text-muted-foreground truncate">{table}</span>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-1">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  By Error Type
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-1">
                  {Object.entries(stats.by_error_type)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 3)
                    .map(([errType, count]) => (
                      <div key={errType} className="flex justify-between text-sm">
                        <span className="text-muted-foreground truncate">{errType}</span>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {isLoading ? (
          <div className="flex items-center justify-center flex-1">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="ag-theme-alpine flex-1" style={{ height: "500px" }}>
            <AgGridReact
              ref={gridRef}
              columnDefs={columnDefs}
              rowData={records}
              defaultColDef={{ sortable: true, filter: true, resizable: true }}
              pagination
              paginationPageSize={50}
            />
          </div>
        )}
      </div>
    </AppLayout>
  );
}
