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
