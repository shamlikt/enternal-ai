"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { AppLayout } from "@/components/sidebar/app-layout";
import { DashboardGrid } from "@/components/dashboard/dashboard-grid";
import { AddWidgetDialog } from "@/components/dashboard/dashboard-builder";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import type { Dashboard, DashboardWidget, WidgetLayout, WidgetType } from "@/types";
import { Plus, Edit3, Save, Loader2, AlertCircle } from "lucide-react";

// Backend widget_type → frontend WidgetType mapping
const WIDGET_TYPE_MAP: Record<string, WidgetType> = {
  bar: "bar_chart",
  line: "line_chart",
  pie: "pie_chart",
  area: "area_chart",
  donut: "donut_chart",
  kpi: "kpi_card",
  table: "data_table",
  funnel: "funnel_chart",
  // Already-mapped values pass through
  bar_chart: "bar_chart",
  line_chart: "line_chart",
  pie_chart: "pie_chart",
  area_chart: "area_chart",
  donut_chart: "donut_chart",
  kpi_card: "kpi_card",
  data_table: "data_table",
  funnel_chart: "funnel_chart",
};

// Transform backend API response to match frontend DashboardWidget type
// eslint-disable-next-line @typescript-eslint/no-explicit-any
function mapApiResponse(raw: any): Dashboard {
  return {
    id: raw.id,
    name: raw.name,
    description: raw.description,
    is_public: raw.is_public,
    created_by: raw.user_id ?? raw.created_by,
    created_at: raw.created_at,
    updated_at: raw.updated_at,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    widgets: (raw.widgets ?? []).map((w: any) => ({
      id: w.id,
      dashboard_id: w.dashboard_id,
      title: w.title,
      widget_type: WIDGET_TYPE_MAP[w.widget_type] ?? w.widget_type,
      query_id: w.query_id,
      sql: w.sql,
      config: w.config ?? (w.config_json ? JSON.parse(w.config_json) : {}),
      layout: w.layout ?? { x: w.grid_x ?? 0, y: w.grid_y ?? 0, w: w.grid_w ?? 6, h: w.grid_h ?? 4 },
    })),
  };
}

export default function DashboardViewPage() {
  const { id } = useParams<{ id: string }>();
  const [dashboard, setDashboard] = useState<Dashboard | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [addWidgetOpen, setAddWidgetOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [pendingLayouts, setPendingLayouts] = useState<Array<{ id: number; layout: WidgetLayout }>>([]);

  useEffect(() => {
    api
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      .get<any>(`/dashboards/${id}`)
      .then((raw) => setDashboard(mapApiResponse(raw)))
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, [id]);

  const handleAddWidget = async (widgetData: {
    title: string;
    widget_type: WidgetType;
    sql: string;
    layout: { x: number; y: number; w: number; h: number };
  }) => {
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const raw = await api.post<any>(`/dashboards/${id}/widgets`, {
        ...widgetData,
        config: {},
      });
      const newWidget: DashboardWidget = {
        id: raw.id,
        dashboard_id: raw.dashboard_id,
        title: raw.title,
        widget_type: WIDGET_TYPE_MAP[raw.widget_type] ?? raw.widget_type,
        query_id: raw.query_id,
        sql: raw.sql,
        config: raw.config ?? (raw.config_json ? JSON.parse(raw.config_json) : {}),
        layout: raw.layout ?? { x: raw.grid_x ?? 0, y: raw.grid_y ?? 0, w: raw.grid_w ?? 6, h: raw.grid_h ?? 4 },
      };
      setDashboard((d) => d ? { ...d, widgets: [...(d.widgets ?? []), newWidget] } : d);
    } catch (err) {
      console.error("Failed to add widget:", err);
    }
  };

  const handleSaveLayout = async () => {
    if (!pendingLayouts.length) {
      setEditMode(false);
      return;
    }
    setIsSaving(true);
    try {
      await api.patch(`/dashboards/${id}/layout`, { layouts: pendingLayouts });
      setPendingLayouts([]);
      setEditMode(false);
    } catch (err) {
      console.error("Failed to save layout:", err);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      </AppLayout>
    );
  }

  if (error || !dashboard) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center h-full">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            {error ?? "Dashboard not found"}
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">{dashboard.name}</h1>
            {dashboard.description && (
              <p className="text-sm text-muted-foreground mt-1">
                {dashboard.description}
              </p>
            )}
          </div>
          <div className="flex items-center gap-2">
            {editMode ? (
              <>
                <Button
                  variant="outline"
                  onClick={() => setAddWidgetOpen(true)}
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Widget
                </Button>
                <Button onClick={handleSaveLayout} disabled={isSaving}>
                  <Save className="h-4 w-4 mr-2" />
                  {isSaving ? "Saving..." : "Save Layout"}
                </Button>
              </>
            ) : (
              <Button variant="outline" onClick={() => setEditMode(true)}>
                <Edit3 className="h-4 w-4 mr-2" />
                Edit
              </Button>
            )}
          </div>
        </div>

        {dashboard.widgets?.length === 0 && !editMode ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <p className="text-muted-foreground">No widgets yet. Click Edit to add widgets.</p>
          </div>
        ) : (
          <DashboardGrid
            widgets={dashboard.widgets ?? []}
            editable={editMode}
            onLayoutChange={setPendingLayouts}
          />
        )}
      </div>

      <AddWidgetDialog
        open={addWidgetOpen}
        onOpenChange={setAddWidgetOpen}
        onAdd={handleAddWidget}
      />
    </AppLayout>
  );
}
