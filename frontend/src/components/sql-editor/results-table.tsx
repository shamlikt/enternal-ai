"use client";

import { useRef } from "react";
import { AgGridReact } from "ag-grid-react";
import {
  ModuleRegistry,
  ClientSideRowModelModule,
  ValidationModule,
  PaginationModule,
  ColumnAutoSizeModule,
} from "ag-grid-community";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import { Button } from "@/components/ui/button";
import type { QueryResult } from "@/types";
import { Download, FileSpreadsheet } from "lucide-react";

ModuleRegistry.registerModules([
  ClientSideRowModelModule,
  ValidationModule,
  PaginationModule,
  ColumnAutoSizeModule,
]);

interface ResultsTableProps {
  result: QueryResult | null;
}

export function ResultsTable({ result }: ResultsTableProps) {
  const gridRef = useRef<AgGridReact>(null);

  if (!result) {
    return (
      <div className="flex items-center justify-center h-full text-sm text-muted-foreground">
        Run a query to see results
      </div>
    );
  }

  const columnDefs = result.columns.map((col) => ({
    field: col,
    headerName: col,
    sortable: true,
    filter: true,
    resizable: true,
    minWidth: 100,
  }));

  const exportCsv = () => {
    gridRef.current?.api.exportDataAsCsv({ fileName: "query_results.csv" });
  };

  const exportExcel = async () => {
    const { utils, writeFile } = await import("xlsx");
    const ws = utils.json_to_sheet(result.rows);
    const wb = utils.book_new();
    utils.book_append_sheet(wb, ws, "Results");
    writeFile(wb, "query_results.xlsx");
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center justify-between px-3 py-2 border-b bg-gray-50">
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span>
            {result.row_count.toLocaleString()} row{result.row_count !== 1 ? "s" : ""}
          </span>
          <span>{result.execution_time_ms}ms</span>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs gap-1"
            onClick={exportCsv}
          >
            <Download className="h-3 w-3" />
            CSV
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="h-7 text-xs gap-1"
            onClick={exportExcel}
          >
            <FileSpreadsheet className="h-3 w-3" />
            Excel
          </Button>
        </div>
      </div>
      <div className="flex-1 ag-theme-alpine">
        <AgGridReact
          ref={gridRef}
          columnDefs={columnDefs}
          rowData={result.rows as Record<string, unknown>[]}
          pagination
          paginationPageSize={100}
          domLayout="normal"
          defaultColDef={{
            sortable: true,
            filter: true,
            resizable: true,
          }}
        />
      </div>
    </div>
  );
}
