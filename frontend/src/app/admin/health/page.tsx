"use client";

import { useEffect, useState } from "react";
import { AppLayout } from "@/components/sidebar/app-layout";
import { api } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { SystemHealth } from "@/types";
import { Activity, Database, Zap, AlertTriangle, Loader2, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function HealthPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setIsLoading(true);
    api
      .get<SystemHealth>("/health/")
      .then(setHealth)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 30000);
    return () => clearInterval(interval);
  }, []);

  const statusColor = (status: string) =>
    status === "healthy" || status === "connected"
      ? "bg-green-400"
      : status === "degraded"
      ? "bg-yellow-400"
      : "bg-red-500";

  return (
    <AppLayout requiredRole="admin">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">System Health</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Live system status — refreshes every 30 seconds
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={load} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
            Refresh
          </Button>
        </div>

        {isLoading && !health && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {error && (
          <div className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {health && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Overall status */}
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <Activity className="h-5 w-5 text-primary" />
                  <CardTitle className="text-base">Overall Status</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <span className={`w-3 h-3 rounded-full ${statusColor(health.status)}`} />
                  <Badge
                    variant={
                      health.status === "healthy"
                        ? "success"
                        : health.status === "degraded"
                        ? "warning"
                        : "destructive"
                    }
                  >
                    {health.status}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Uptime: {Math.floor(health.api.uptime_seconds / 3600)}h{" "}
                  {Math.floor((health.api.uptime_seconds % 3600) / 60)}m
                </p>
                <p className="text-xs text-muted-foreground">
                  Version: {health.api.version}
                </p>
              </CardContent>
            </Card>

            {/* Database */}
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-primary" />
                  <CardTitle className="text-base">Database</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <div className="flex items-center gap-2">
                  <span className={`w-3 h-3 rounded-full ${statusColor(health.database.status)}`} />
                  <Badge variant={health.database.status === "connected" ? "success" : "destructive"}>
                    {health.database.status}
                  </Badge>
                </div>
                {health.database.latency_ms !== undefined && (
                  <p className="text-xs text-muted-foreground mt-2">
                    Latency: {health.database.latency_ms}ms
                  </p>
                )}
              </CardContent>
            </Card>

            {/* Ingestion */}
            <Card>
              <CardHeader className="pb-2">
                <div className="flex items-center gap-2">
                  <Zap className="h-5 w-5 text-primary" />
                  <CardTitle className="text-base">Ingestion</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                {health.ingestion.status && (
                  <div className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${statusColor(health.ingestion.status)}`} />
                    <Badge variant="secondary">{health.ingestion.status}</Badge>
                  </div>
                )}
                {health.ingestion.last_run && (
                  <p className="text-xs text-muted-foreground mt-2">
                    Last run: {new Date(health.ingestion.last_run).toLocaleString()}
                  </p>
                )}
                <div className="flex items-center gap-1 mt-1">
                  <AlertTriangle className="h-3 w-3 text-yellow-500" />
                  <p className="text-xs text-muted-foreground">
                    {health.ingestion.error_count_24h} errors in last 24h
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
