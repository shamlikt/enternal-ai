"use client";

import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import type { WidgetType } from "@/types";

const CHART_COLORS = [
  "#1463ff",
  "#06b6d4",
  "#8b5cf6",
  "#10b981",
  "#f59e0b",
  "#ef4444",
  "#ec4899",
  "#84cc16",
];

interface ChartData {
  [key: string]: string | number;
}

interface ChartWidgetProps {
  type: WidgetType;
  data: ChartData[];
  config: {
    xKey?: string;
    yKey?: string;
    valueKey?: string;
    nameKey?: string;
    title?: string;
    unit?: string;
    value?: string | number;
    description?: string;
  };
}

export function ChartWidget({ type, data, config }: ChartWidgetProps) {
  switch (type) {
    case "bar_chart":
      return <BarChartWidget data={data} config={config} />;
    case "line_chart":
      return <LineChartWidget data={data} config={config} />;
    case "pie_chart":
      return <PieChartWidget data={data} config={config} />;
    case "area_chart":
      return <AreaChartWidget data={data} config={config} />;
    case "donut_chart":
      return <DonutChartWidget data={data} config={config} />;
    case "kpi_card":
      return <KpiCardWidget config={config} />;
    case "data_table":
      return <DataTableWidget data={data} />;
    default:
      return <div className="text-sm text-muted-foreground">Unknown chart type</div>;
  }
}

function BarChartWidget({ data, config }: { data: ChartData[]; config: ChartWidgetProps["config"] }) {
  const xKey = config.xKey ?? "name";
  const yKey = config.yKey ?? "value";
  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Bar dataKey={yKey} fill={CHART_COLORS[0]} radius={[3, 3, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}

function LineChartWidget({ data, config }: { data: ChartData[]; config: ChartWidgetProps["config"] }) {
  const xKey = config.xKey ?? "name";
  const yKey = config.yKey ?? "value";
  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Line type="monotone" dataKey={yKey} stroke={CHART_COLORS[0]} strokeWidth={2} dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}

function AreaChartWidget({ data, config }: { data: ChartData[]; config: ChartWidgetProps["config"] }) {
  const xKey = config.xKey ?? "name";
  const yKey = config.yKey ?? "value";
  return (
    <ResponsiveContainer width="100%" height={220}>
      <AreaChart data={data} margin={{ top: 5, right: 10, left: 0, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis dataKey={xKey} tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Area
          type="monotone"
          dataKey={yKey}
          stroke={CHART_COLORS[0]}
          fill={`${CHART_COLORS[0]}20`}
          strokeWidth={2}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}

function PieChartWidget({ data, config }: { data: ChartData[]; config: ChartWidgetProps["config"] }) {
  const nameKey = config.nameKey ?? "name";
  const valueKey = config.valueKey ?? "value";
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie
          data={data}
          dataKey={valueKey}
          nameKey={nameKey}
          cx="50%"
          cy="50%"
          outerRadius={80}
          label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
          labelLine={false}
        >
          {data.map((_, index) => (
            <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

function DonutChartWidget({ data, config }: { data: ChartData[]; config: ChartWidgetProps["config"] }) {
  const nameKey = config.nameKey ?? "name";
  const valueKey = config.valueKey ?? "value";
  return (
    <ResponsiveContainer width="100%" height={220}>
      <PieChart>
        <Pie
          data={data}
          dataKey={valueKey}
          nameKey={nameKey}
          cx="50%"
          cy="50%"
          innerRadius={50}
          outerRadius={80}
        >
          {data.map((_, index) => (
            <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
          ))}
        </Pie>
        <Tooltip />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

function KpiCardWidget({ config }: { config: ChartWidgetProps["config"] }) {
  return (
    <div className="flex flex-col items-center justify-center h-full py-4 text-center">
      <p className="text-4xl font-bold text-primary">
        {config.value ?? "—"}
        {config.unit && <span className="text-xl ml-1 font-normal">{config.unit}</span>}
      </p>
      {config.description && (
        <p className="text-sm text-muted-foreground mt-2">{config.description}</p>
      )}
    </div>
  );
}

function DataTableWidget({ data }: { data: ChartData[] }) {
  if (!data || data.length === 0) {
    return <p className="text-sm text-muted-foreground">No data</p>;
  }
  const columns = Object.keys(data[0]);
  return (
    <div className="overflow-auto max-h-[200px]">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b">
            {columns.map((col) => (
              <th key={col} className="px-2 py-1 text-left font-medium text-muted-foreground">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="border-b last:border-0 hover:bg-muted/50">
              {columns.map((col) => (
                <td key={col} className="px-2 py-1">
                  {String(row[col] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
