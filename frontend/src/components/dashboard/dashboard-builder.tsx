"use client";

import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import type { WidgetType } from "@/types";

const WIDGET_TYPES: { value: WidgetType; label: string }[] = [
  { value: "bar_chart", label: "Bar Chart" },
  { value: "line_chart", label: "Line Chart" },
  { value: "pie_chart", label: "Pie Chart" },
  { value: "area_chart", label: "Area Chart" },
  { value: "donut_chart", label: "Donut Chart" },
  { value: "kpi_card", label: "KPI Card" },
  { value: "data_table", label: "Data Table" },
];

interface AddWidgetDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onAdd: (widget: {
    title: string;
    widget_type: WidgetType;
    sql: string;
    layout: { x: number; y: number; w: number; h: number };
  }) => void;
}

export function AddWidgetDialog({ open, onOpenChange, onAdd }: AddWidgetDialogProps) {
  const [title, setTitle] = useState("");
  const [widgetType, setWidgetType] = useState<WidgetType>("bar_chart");
  const [sql, setSql] = useState("");

  const handleAdd = () => {
    onAdd({
      title,
      widget_type: widgetType,
      sql,
      layout: { x: 0, y: 0, w: 6, h: 5 },
    });
    setTitle("");
    setSql("");
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Add Widget</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label>Title</Label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Widget title"
            />
          </div>
          <div className="space-y-2">
            <Label>Chart Type</Label>
            <Select
              value={widgetType}
              onValueChange={(v) => setWidgetType(v as WidgetType)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {WIDGET_TYPES.map((t) => (
                  <SelectItem key={t.value} value={t.value}>
                    {t.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label>SQL Query</Label>
            <textarea
              value={sql}
              onChange={(e) => setSql(e.target.value)}
              placeholder="SELECT ... FROM ..."
              rows={5}
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm font-mono focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={handleAdd} disabled={!title || !widgetType}>
            Add Widget
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
