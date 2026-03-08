"use client";

import { useCallback, useState } from "react";
import { GridLayout } from "react-grid-layout";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";
import { WidgetCard } from "./widget-card";
import type { DashboardWidget, WidgetLayout } from "@/types";

// LayoutItem shape for react-grid-layout v5
interface LayoutItem {
  i: string;
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  minH?: number;
}

type RglLayout = readonly LayoutItem[];

interface DashboardGridProps {
  widgets: DashboardWidget[];
  editable?: boolean;
  onLayoutChange?: (layouts: Array<{ id: number; layout: WidgetLayout }>) => void;
}

export function DashboardGrid({
  widgets,
  editable = false,
  onLayoutChange,
}: DashboardGridProps) {
  const [containerWidth, setContainerWidth] = useState(1200);

  const refCallback = useCallback((node: HTMLDivElement | null) => {
    if (node) {
      setContainerWidth(node.offsetWidth);
    }
  }, []);

  const layout: LayoutItem[] = widgets.map((w) => ({
    i: String(w.id),
    x: w.layout.x,
    y: w.layout.y,
    w: w.layout.w,
    h: w.layout.h,
    minW: 2,
    minH: 3,
  }));

  const handleLayoutChange = (newLayout: RglLayout) => {
    if (!onLayoutChange) return;
    const updated = newLayout.map((l) => ({
      id: parseInt(l.i),
      layout: { x: l.x, y: l.y, w: l.w, h: l.h },
    }));
    onLayoutChange(updated);
  };

  return (
    <div ref={refCallback} className="w-full">
      <GridLayout
        layout={layout as RglLayout}
        width={containerWidth}
        gridConfig={{
          cols: 12,
          rowHeight: 60,
          margin: [12, 12],
          containerPadding: [0, 0],
          maxRows: Infinity,
        }}
        dragConfig={{ enabled: editable, bounded: false, threshold: 3 }}
        resizeConfig={{ enabled: editable }}
        onLayoutChange={handleLayoutChange}
      >
        {widgets.map((widget) => (
          <div key={String(widget.id)} className="h-full">
            <WidgetCard widget={widget} />
          </div>
        ))}
      </GridLayout>
    </div>
  );
}
