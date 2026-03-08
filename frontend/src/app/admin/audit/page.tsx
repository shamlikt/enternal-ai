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
import type { AuditLog } from "@/types";
import { Loader2 } from "lucide-react";

ModuleRegistry.registerModules([
  ClientSideRowModelModule,
  ValidationModule,
  PaginationModule,
]);

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const gridRef = useRef<AgGridReact>(null);

  useEffect(() => {
    api
      .get<AuditLog[]>("/audit/")
      .then(setLogs)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  }, []);

  const columnDefs = [
    {
      field: "created_at",
      headerName: "Time",
      width: 180,
      valueFormatter: ({ value }: { value: string }) =>
        new Date(value).toLocaleString(),
      sort: "desc" as const,
    },
    { field: "username", headerName: "User", width: 140 },
    { field: "action", headerName: "Action", width: 160 },
    { field: "resource_type", headerName: "Resource", width: 140 },
    { field: "resource_id", headerName: "Resource ID", width: 120 },
    { field: "ip_address", headerName: "IP", width: 130 },
  ];

  return (
    <AppLayout requiredRole="admin">
      <div className="p-6 flex flex-col gap-4 h-full">
        <div>
          <h1 className="text-2xl font-semibold">Audit Log</h1>
          <p className="text-sm text-muted-foreground mt-1">
            All user actions and data access events
          </p>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center flex-1">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="ag-theme-alpine flex-1" style={{ height: "600px" }}>
            <AgGridReact
              ref={gridRef}
              columnDefs={columnDefs}
              rowData={logs}
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
