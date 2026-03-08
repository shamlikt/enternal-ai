"use client";

import { useEffect, useRef, useState } from "react";
import { AppLayout } from "@/components/sidebar/app-layout";
import { api } from "@/lib/api";
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
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Badge } from "@/components/ui/badge";
import { AgGridReact } from "ag-grid-react";
import {
  ModuleRegistry,
  ClientSideRowModelModule,
  ValidationModule,
} from "ag-grid-community";
import "ag-grid-community/styles/ag-grid.css";
import "ag-grid-community/styles/ag-theme-alpine.css";
import type { User, Role } from "@/types";
import { Plus, Loader2 } from "lucide-react";

ModuleRegistry.registerModules([
  ClientSideRowModelModule,
  ValidationModule,
]);

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [createOpen, setCreateOpen] = useState(false);
  const [newUsername, setNewUsername] = useState("");
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState<Role>("analyst");
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const gridRef = useRef<AgGridReact>(null);

  const loadUsers = () => {
    setIsLoading(true);
    api
      .get<User[]>("/auth/users")
      .then(setUsers)
      .catch(console.error)
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    loadUsers();
  }, []);

  const handleCreate = async () => {
    setCreating(true);
    setError(null);
    try {
      await api.post("/auth/users", {
        username: newUsername,
        email: newEmail,
        password: newPassword,
        role: newRole,
      });
      setCreateOpen(false);
      setNewUsername("");
      setNewEmail("");
      setNewPassword("");
      setNewRole("analyst");
      loadUsers();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create user");
    } finally {
      setCreating(false);
    }
  };

  const columnDefs = [
    { field: "id", headerName: "ID", width: 70 },
    { field: "username", headerName: "Username", flex: 1 },
    { field: "email", headerName: "Email", flex: 2 },
    {
      field: "role",
      headerName: "Role",
      width: 120,
      cellRenderer: ({ value }: { value: string }) => (
        <Badge
          variant={
            value === "admin"
              ? "default"
              : value === "analyst"
              ? "secondary"
              : "outline"
          }
        >
          {value}
        </Badge>
      ),
    },
    {
      field: "is_active",
      headerName: "Active",
      width: 100,
      cellRenderer: ({ value }: { value: boolean }) => (
        <span className={value ? "text-green-600" : "text-red-500"}>
          {value ? "Active" : "Inactive"}
        </span>
      ),
    },
    { field: "created_at", headerName: "Created", flex: 1, valueFormatter: ({ value }: { value: string }) => new Date(value).toLocaleDateString() },
  ];

  return (
    <AppLayout requiredRole="admin">
      <div className="p-6 flex flex-col h-full gap-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Users</h1>
            <p className="text-sm text-muted-foreground mt-1">
              Manage platform users and their roles
            </p>
          </div>
          <Button onClick={() => setCreateOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create User
          </Button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center flex-1">
            <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
          </div>
        ) : (
          <div className="ag-theme-alpine flex-1" style={{ height: "500px" }}>
            <AgGridReact
              ref={gridRef}
              columnDefs={columnDefs}
              rowData={users}
              defaultColDef={{ sortable: true, filter: true }}
            />
          </div>
        )}

        <Dialog open={createOpen} onOpenChange={setCreateOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Create User</DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label>Username</Label>
                <Input
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="johndoe"
                />
              </div>
              <div className="space-y-2">
                <Label>Email</Label>
                <Input
                  type="email"
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="john@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label>Password</Label>
                <Input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label>Role</Label>
                <Select value={newRole} onValueChange={(v) => setNewRole(v as Role)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="analyst">Analyst</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              {error && (
                <p className="text-sm text-red-600">{error}</p>
              )}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleCreate}
                disabled={creating || !newUsername || !newEmail || !newPassword}
              >
                {creating ? "Creating..." : "Create"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </AppLayout>
  );
}
