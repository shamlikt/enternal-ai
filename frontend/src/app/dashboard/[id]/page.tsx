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
      .get<Dashboard>(`/dashboards/${id}`)
      .then(setDashboard)
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
      const newWidget = await api.post<DashboardWidget>(`/dashboards/${id}/widgets`, {
        ...widgetData,
        config: {},
      });
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
