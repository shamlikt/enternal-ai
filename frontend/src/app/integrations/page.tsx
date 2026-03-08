"use client";

import { useEffect, useState } from "react";
import { AppLayout } from "@/components/sidebar/app-layout";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { Integration, IntegrationType, IngestionRun } from "@/types";
import { Plus, Play, CheckCircle2, XCircle, Loader2, Plug } from "lucide-react";

export default function IntegrationsPage() {
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [runs, setRuns] = useState<IngestionRun[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [addOpen, setAddOpen] = useState(false);
  const [integrationType, setIntegrationType] = useState<IntegrationType>("fhir");
  const [formData, setFormData] = useState<Record<string, string>>({});
  const [testing, setTesting] = useState<number | null>(null);
  const [triggering, setTriggering] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = () => {
    setIsLoading(true);
    Promise.all([
      api.get<Integration[]>("/integrations/"),
      api.get<IngestionRun[]>("/ingestion/runs"),
    ])
      .then(([ints, r]) => {
        setIntegrations(ints);
        setRuns(r);
      })
      .catch(console.error)
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    load();
  }, []);

  const handleTest = async (id: number) => {
    setTesting(id);
    try {
      await api.post(`/integrations/${id}/test`);
      alert("Connection test passed!");
    } catch (err) {
      alert(`Connection test failed: ${err instanceof Error ? err.message : "Unknown error"}`);
    } finally {
      setTesting(null);
    }
  };

  const handleTrigger = async (id: number) => {
    setTriggering(id);
    try {
      await api.post(`/ingestion/${id}/run`);
      load();
    } catch (err) {
      console.error(err);
    } finally {
      setTriggering(null);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    setError(null);
    try {
      await api.post("/integrations/", {
        type: integrationType,
        name: formData.name,
        config: formData,
      });
      setAddOpen(false);
      setFormData({});
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  };

  const statusBadgeVariant = (status: string) =>
    status === "active" ? "success" : status === "error" ? "destructive" : "secondary";

  const runStatusBadge = (status: string) =>
    status === "completed"
      ? "success"
      : status === "failed"
      ? "destructive"
      : status === "running"
      ? "default"
      : "secondary";

  return (
    <AppLayout requiredRole="admin">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Integrations</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Configure FHIR and Snowflake data connections
            </p>
          </div>
          <Button onClick={() => setAddOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Integration
          </Button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <Tabs defaultValue="integrations">
            <TabsList>
              <TabsTrigger value="integrations">Integrations</TabsTrigger>
              <TabsTrigger value="runs">Ingestion History</TabsTrigger>
            </TabsList>

            <TabsContent value="integrations" className="mt-4">
              {integrations.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                  <Plug className="h-12 w-12 text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium">No integrations</h3>
                  <p className="text-sm text-muted-foreground mt-1 mb-4">
                    Add a FHIR server or Snowflake connection to start ingesting data
                  </p>
                  <Button onClick={() => setAddOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add Integration
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {integrations.map((integration) => (
                    <Card key={integration.id}>
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-base">{integration.name}</CardTitle>
                          <Badge variant={statusBadgeVariant(integration.status)}>
                            {integration.status}
                          </Badge>
                        </div>
                        <p className="text-xs text-muted-foreground uppercase">
                          {integration.type}
                        </p>
                      </CardHeader>
                      <CardContent>
                        <div className="flex gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleTest(integration.id)}
                            disabled={testing === integration.id}
                          >
                            {testing === integration.id ? (
                              <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                            ) : (
                              <CheckCircle2 className="h-3 w-3 mr-1" />
                            )}
                            Test
                          </Button>
                          <Button
                            size="sm"
                            onClick={() => handleTrigger(integration.id)}
                            disabled={triggering === integration.id}
                          >
                            {triggering === integration.id ? (
                              <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                            ) : (
                              <Play className="h-3 w-3 mr-1" />
                            )}
                            Run Ingestion
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            <TabsContent value="runs" className="mt-4">
              <div className="rounded-lg border overflow-hidden">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-gray-50 border-b">
                      <th className="px-4 py-2 text-left font-medium text-muted-foreground">ID</th>
                      <th className="px-4 py-2 text-left font-medium text-muted-foreground">Status</th>
                      <th className="px-4 py-2 text-left font-medium text-muted-foreground">Processed</th>
                      <th className="px-4 py-2 text-left font-medium text-muted-foreground">Failed</th>
                      <th className="px-4 py-2 text-left font-medium text-muted-foreground">Started</th>
                      <th className="px-4 py-2 text-left font-medium text-muted-foreground">Completed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runs.map((run) => (
                      <tr key={run.id} className="border-b last:border-0 hover:bg-muted/30">
                        <td className="px-4 py-2">{run.id}</td>
                        <td className="px-4 py-2">
                          <Badge variant={runStatusBadge(run.status)} className="text-xs">
                            {run.status}
                          </Badge>
                        </td>
                        <td className="px-4 py-2">{run.records_processed.toLocaleString()}</td>
                        <td className="px-4 py-2">
                          {run.records_failed > 0 ? (
                            <span className="text-red-600 flex items-center gap-1">
                              <XCircle className="h-3 w-3" />
                              {run.records_failed}
                            </span>
                          ) : (
                            "0"
                          )}
                        </td>
                        <td className="px-4 py-2 text-xs">
                          {new Date(run.started_at).toLocaleString()}
                        </td>
                        <td className="px-4 py-2 text-xs">
                          {run.completed_at
                            ? new Date(run.completed_at).toLocaleString()
                            : "—"}
                        </td>
                      </tr>
                    ))}
                    {runs.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-4 py-8 text-center text-muted-foreground text-sm">
                          No ingestion runs yet
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </TabsContent>
          </Tabs>
        )}

        {/* Add Integration Dialog */}
        <Dialog open={addOpen} onOpenChange={setAddOpen}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Add Integration</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Name</Label>
                <Input
                  value={formData.name ?? ""}
                  onChange={(e) => setFormData((f) => ({ ...f, name: e.target.value }))}
                  placeholder="Production FHIR Server"
                />
              </div>
              <div className="space-y-2">
                <Label>Type</Label>
                <Select
                  value={integrationType}
                  onValueChange={(v) => setIntegrationType(v as IntegrationType)}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="fhir">FHIR</SelectItem>
                    <SelectItem value="snowflake">Snowflake</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {integrationType === "fhir" && (
                <>
                  <div className="space-y-2">
                    <Label>Server URL</Label>
                    <Input
                      value={formData.server_url ?? ""}
                      onChange={(e) => setFormData((f) => ({ ...f, server_url: e.target.value }))}
                      placeholder="https://fhir.example.com/R4"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Auth Type</Label>
                    <Select
                      value={formData.auth_type ?? "none"}
                      onValueChange={(v) => setFormData((f) => ({ ...f, auth_type: v }))}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="none">None</SelectItem>
                        <SelectItem value="bearer">Bearer Token</SelectItem>
                        <SelectItem value="basic">Basic Auth</SelectItem>
                        <SelectItem value="client_credentials">Client Credentials</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  {(formData.auth_type === "client_credentials") && (
                    <>
                      <div className="space-y-2">
                        <Label>Client ID</Label>
                        <Input
                          value={formData.client_id ?? ""}
                          onChange={(e) => setFormData((f) => ({ ...f, client_id: e.target.value }))}
                        />
                      </div>
                      <div className="space-y-2">
                        <Label>Client Secret</Label>
                        <Input
                          type="password"
                          value={formData.client_secret ?? ""}
                          onChange={(e) => setFormData((f) => ({ ...f, client_secret: e.target.value }))}
                        />
                      </div>
                    </>
                  )}
                </>
              )}

              {integrationType === "snowflake" && (
                <>
                  {[
                    { key: "account", label: "Account", placeholder: "xy12345.us-east-1" },
                    { key: "username", label: "Username", placeholder: "" },
                    { key: "password", label: "Password", placeholder: "", type: "password" },
                    { key: "database", label: "Database", placeholder: "" },
                    { key: "schema", label: "Schema", placeholder: "" },
                    { key: "warehouse", label: "Warehouse", placeholder: "" },
                    { key: "role", label: "Role", placeholder: "" },
                  ].map(({ key, label, placeholder, type }) => (
                    <div key={key} className="space-y-2">
                      <Label>{label}</Label>
                      <Input
                        type={type ?? "text"}
                        value={formData[key] ?? ""}
                        onChange={(e) => setFormData((f) => ({ ...f, [key]: e.target.value }))}
                        placeholder={placeholder}
                      />
                    </div>
                  ))}
                </>
              )}

              {error && <p className="text-sm text-red-600">{error}</p>}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setAddOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={saving || !formData.name}>
                {saving ? "Saving..." : "Save"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
}
