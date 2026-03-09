# SQL Editor Optimization — Databricks/Snowflake-Style

**Date:** 2026-03-09
**Status:** Approved

---

## Goal

Transform the basic SQL editor into a professional, Databricks/Snowflake-grade experience with schema-aware autocomplete, syntax validation, hover info, and SQL formatting.

## Architecture

Keep Monaco Editor. Add `monaco-sql-languages` (DTStack, ANTLR4-based PgSQL parser) for schema-aware autocomplete + syntax validation. Add `sql-formatter` for formatting. Custom hover provider for column type info.

```
┌─────────────────────────────────────────────────┐
│  SQL Editor Page                                │
│  ┌───────────┐  ┌────────────────────────────┐  │
│  │  Data      │  │  Monaco Editor             │  │
│  │  Explorer  │  │  + monaco-sql-languages    │  │
│  │  (tree)    │  │    (PgSQL dialect)         │  │
│  │            │  │  + completionService       │  │
│  │            │  │    (schema-aware)          │  │
│  │            │  │  + hover provider          │  │
│  │            │  │  + sql-formatter           │  │
│  │            │  │  + syntax validation       │  │
│  └───────────┘  └────────────────────────────┘  │
│                 ┌────────────────────────────┐  │
│                 │  Results Table (AG Grid)    │  │
│                 └────────────────────────────┘  │
└─────────────────────────────────────────────────┘
        │
        ▼  GET /query/schema (on mount, cached)
┌─────────────────┐
│  Backend API     │
│  - schema meta   │──→  SchemaMetadataCache
│  - query execute │      (tables + columns + types)
└─────────────────┘
```

**Data flow:**
1. On mount → fetch `GET /query/schema` → cache table/column metadata
2. User types SQL → ANTLR4 parser determines syntax context (TABLE, COLUMN, KEYWORD)
3. `completionService` fires → checks `EntityContextType` → returns matching items from cache
4. User sees contextual suggestions

## New Packages

```
npm install monaco-sql-languages sql-formatter
```

- `monaco-sql-languages` — bundles `dt-sql-parser` (ANTLR4 PgSQL grammar)
- `sql-formatter` — standalone SQL pretty-printer

No backend changes needed.

## Features

| Feature | Implementation | Library |
|---------|---------------|---------|
| Schema-aware autocomplete | `completionService` callback with cached schema | `monaco-sql-languages` |
| Table suggestions | After `FROM`, `JOIN`, `INTO` → suggest table names | `monaco-sql-languages` |
| Column suggestions | After `SELECT`, `WHERE`, `table.` → suggest columns | `monaco-sql-languages` |
| SQL keyword completion | Built-in from ANTLR4 grammar | `monaco-sql-languages` |
| SQL snippets | `SELECT...FROM`, `JOIN...ON`, `CASE...WHEN` | `monaco-sql-languages` |
| Syntax validation | Real-time red squiggles for parse errors | `dt-sql-parser` (bundled) |
| Hover on table/column | Shows column type, nullable, description | Custom Monaco hover provider |
| Format SQL | "Format" button in toolbar | `sql-formatter` |
| Trigger characters | `.` triggers column completion, ` ` triggers keywords | Config |
| Quoted identifiers | Auto-quote uppercase PCORnet names in insertText | Custom in completionService |
| Dark theme | Match sidebar theme | Monaco theme API |

## Files to Modify

| File | Change |
|------|--------|
| `frontend/package.json` | Add `monaco-sql-languages`, `sql-formatter` |
| `frontend/src/components/sql-editor/editor.tsx` | Rewrite — replace manual keyword provider with `monaco-sql-languages` PgSQL, `completionService`, hover provider |
| `frontend/src/app/sql-editor/page.tsx` | Add schema fetching + caching, pass schema to editor, add Format button |

## New Files

| File | Purpose |
|------|---------|
| `frontend/src/lib/sql-schema-cache.ts` | Schema metadata cache — fetches `/query/schema`, provides `getTableNames()`, `getColumnsForTable(name)`, `getColumnType(table, col)` |

## Key Implementation Details

### completionService

```typescript
import 'monaco-sql-languages/esm/languages/pgsql/pgsql.contribution';
import { setupLanguageFeatures, LanguageIdEnum, EntityContextType } from 'monaco-sql-languages';

setupLanguageFeatures(LanguageIdEnum.PG, {
  completionItems: {
    enable: true,
    triggerCharacters: [' ', '.', '"'],
    completionService: async (model, position, context, suggestions, entities) => {
      const items = [];
      // Keywords from parser
      items.push(...suggestions.keywords.map(kw => ({ label: kw, kind: Keyword, insertText: kw })));
      // Schema-aware table/column suggestions
      for (const entity of entities) {
        if (entity.syntaxContextType === EntityContextType.TABLE) {
          items.push(...cache.getTableNames().map(t => ({
            label: t, kind: Class, insertText: `"${t}"`, detail: 'table',
          })));
        }
        if (entity.syntaxContextType === EntityContextType.COLUMN) {
          const table = extractTableFromContext(entity);
          items.push(...cache.getColumns(table).map(c => ({
            label: c.name, kind: Field, insertText: `"${c.name}"`, detail: c.type,
          })));
        }
      }
      return items;
    },
  },
});
```

### Hover Provider

```typescript
monaco.languages.registerHoverProvider(LanguageIdEnum.PG, {
  provideHover(model, position) {
    const word = model.getWordAtPosition(position);
    if (!word) return null;
    const table = cache.findTable(word.word);
    if (table) return { contents: [{ value: `**Table:** ${table.name}\n\n${table.columns.length} columns` }] };
    const col = cache.findColumn(word.word);
    if (col) return { contents: [{ value: `**${col.name}**\n\nType: \`${col.type}\`\nNullable: ${col.nullable}` }] };
    return null;
  }
});
```

### SQL Formatter

```typescript
import { format } from 'sql-formatter';
const formatted = format(sql, { language: 'postgresql', tabWidth: 2, keywordCase: 'upper' });
```

### Toolbar

```
[SQL Editor] [Ctrl+Enter hint] [Format] [Run ▶]
```
