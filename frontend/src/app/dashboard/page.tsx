"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { AppLayout } from "@/components/sidebar/app-layout";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Dashboard } from "@/types";
import { Plus, BarChart2, Loader2, LayoutDashboard } from "lucide-react";

export default function DashboardListPage() {
  const [dashboards, setDashboards] = useState<Dashboard[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<Dashboard[]>("/dashboards/")
      .then(setDashboards)
      .catch((err) => setError(err.message))
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <AppLayout>
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Dashboards</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Visualize your PCORnet data with charts and KPIs
            </p>
          </div>
          <Link href="/dashboard/new">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Dashboard
            </Button>
          </Link>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        )}

        {error && (
          <div className="rounded-md bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {!isLoading && !error && dashboards.length === 0 && (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <LayoutDashboard className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-medium">No dashboards yet</h3>
            <p className="text-sm text-muted-foreground mt-1 mb-4">
              Create your first dashboard to start visualizing data
            </p>
            <Link href="/dashboard/new">
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Create Dashboard
              </Button>
            </Link>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {dashboards.map((dashboard) => (
            <Link key={dashboard.id} href={`/dashboard/${dashboard.id}`}>
              <Card className="cursor-pointer hover:shadow-md transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <BarChart2 className="h-5 w-5 text-primary" />
                    {dashboard.is_public && (
                      <Badge variant="secondary">Public</Badge>
                    )}
                  </div>
                  <CardTitle className="text-base mt-2">{dashboard.name}</CardTitle>
                  {dashboard.description && (
                    <CardDescription className="text-xs">
                      {dashboard.description}
                    </CardDescription>
                  )}
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground">
                    {dashboard.widgets?.length ?? 0} widgets •{" "}
                    {new Date(dashboard.updated_at).toLocaleDateString()}
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </AppLayout>
  );
}
