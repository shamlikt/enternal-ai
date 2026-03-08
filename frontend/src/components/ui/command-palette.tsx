"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import {
  BarChart2,
  Code2,
  Bot,
  Settings,
  AlertTriangle,
  Plug,
  Users,
  Activity,
  FileText,
  Shield,
} from "lucide-react";
import { Dialog, DialogContent } from "./dialog";

const NAVIGATION_ITEMS = [
  { label: "Dashboard", href: "/dashboard", icon: BarChart2 },
  { label: "SQL Editor", href: "/sql-editor", icon: Code2 },
  { label: "Agent Search", href: "/agent", icon: Bot },
  { label: "Integrations", href: "/integrations", icon: Plug },
  { label: "Quarantine", href: "/quarantine", icon: AlertTriangle },
  { label: "Admin - Users", href: "/admin/users", icon: Users },
  { label: "Admin - Health", href: "/admin/health", icon: Activity },
  { label: "Admin - Audit", href: "/admin/audit", icon: Shield },
  { label: "Admin - Logs", href: "/admin/logs", icon: FileText },
  { label: "Admin", href: "/admin", icon: Settings },
];

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      setOpen((prev) => !prev);
    }
  }, []);

  useEffect(() => {
    document.addEventListener("keydown", handleKeyDown);
    return () => document.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  const navigate = (href: string) => {
    setOpen(false);
    router.push(href);
  };

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogContent className="p-0 max-w-xl overflow-hidden">
        <Command className="rounded-lg border-0">
          <div className="flex items-center border-b px-3">
            <Command.Input
              placeholder="Search pages and commands..."
              className="flex h-11 w-full rounded-md bg-transparent py-3 text-sm outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed disabled:opacity-50"
            />
          </div>
          <Command.List className="max-h-80 overflow-y-auto p-2">
            <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
              No results found.
            </Command.Empty>
            <Command.Group heading="Navigation" className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1.5 [&_[cmdk-group-heading]]:text-xs [&_[cmdk-group-heading]]:font-medium [&_[cmdk-group-heading]]:text-muted-foreground">
              {NAVIGATION_ITEMS.map((item) => {
                const Icon = item.icon;
                return (
                  <Command.Item
                    key={item.href}
                    value={item.label}
                    onSelect={() => navigate(item.href)}
                    className="flex items-center gap-2 rounded-sm px-2 py-1.5 text-sm cursor-pointer hover:bg-accent hover:text-accent-foreground aria-selected:bg-accent aria-selected:text-accent-foreground"
                  >
                    <Icon className="h-4 w-4 text-muted-foreground" />
                    {item.label}
                  </Command.Item>
                );
              })}
            </Command.Group>
          </Command.List>
          <div className="border-t px-3 py-2 flex items-center gap-4 text-xs text-muted-foreground">
            <span><kbd className="font-mono">Enter</kbd> to select</span>
            <span><kbd className="font-mono">Esc</kbd> to close</span>
          </div>
        </Command>
      </DialogContent>
    </Dialog>
  );
}
