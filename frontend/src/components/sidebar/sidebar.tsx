"use client";

import { useState } from "react";
import {
  BarChart2,
  Code2,
  Bot,
  Plug,
  AlertTriangle,
  Settings,
  ChevronLeft,
  ChevronRight,
  Activity,
  Dna,
} from "lucide-react";
import { NavItem } from "./nav-item";
import { SidebarUserMenu } from "./user-menu";
import { cn } from "@/lib/utils";
import { useAuth } from "@/lib/auth";

const NAV_ITEMS: Array<{
  href: string;
  label: string;
  icon: typeof BarChart2;
  adminOnly?: boolean;
}> = [
  { href: "/dashboard", label: "Dashboard", icon: BarChart2 },
  { href: "/sql-editor", label: "SQL Editor", icon: Code2 },
  { href: "/agent", label: "Agent Search", icon: Bot },
  { href: "/integrations", label: "Integrations", icon: Plug, adminOnly: true },
  { href: "/quarantine", label: "Quarantine", icon: AlertTriangle, adminOnly: true },
  { href: "/admin", label: "Admin", icon: Settings, adminOnly: true },
];

export function Sidebar() {
  const [collapsed, setCollapsed] = useState(false);
  const { user } = useAuth();

  const visibleItems = NAV_ITEMS.filter(
    (item) => !item.adminOnly || user?.role === "admin"
  );

  return (
    <aside
      className={cn(
        "flex flex-col h-screen bg-[var(--sidebar-bg)] border-r border-[var(--sidebar-border)] transition-all duration-200 shrink-0",
        collapsed ? "w-[var(--sidebar-collapsed-width)]" : "w-[var(--sidebar-width)]"
      )}
    >
      {/* Logo */}
      <div
        className={cn(
          "flex items-center gap-2 px-3 py-4 border-b border-[var(--sidebar-border)]",
          collapsed && "justify-center"
        )}
      >
        <div className="flex items-center justify-center w-7 h-7 rounded-md bg-primary">
          <Dna className="h-4 w-4 text-white" />
        </div>
        {!collapsed && (
          <span className="text-sm font-semibold text-white">Enternal Health</span>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-3 space-y-1 overflow-y-auto">
        {visibleItems.map((item) => (
          <NavItem
            key={item.href}
            href={item.href}
            label={item.label}
            icon={item.icon}
            collapsed={collapsed}
          />
        ))}
      </nav>

      {/* System health indicator */}
      {!collapsed && (
        <div className="px-3 py-2 border-t border-[var(--sidebar-border)]">
          <div className="flex items-center gap-2 text-xs text-[var(--sidebar-muted)]">
            <Activity className="h-3 w-3 text-green-400" />
            <span>System healthy</span>
          </div>
        </div>
      )}

      {/* User menu */}
      <div className="border-t border-[var(--sidebar-border)]">
        <SidebarUserMenu collapsed={collapsed} />
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed((c) => !c)}
        className={cn(
          "flex items-center justify-center h-8 w-full border-t border-[var(--sidebar-border)] text-[var(--sidebar-muted)] hover:text-white hover:bg-[var(--sidebar-hover)] transition-colors"
        )}
        aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
      >
        {collapsed ? (
          <ChevronRight className="h-4 w-4" />
        ) : (
          <ChevronLeft className="h-4 w-4" />
        )}
      </button>
    </aside>
  );
}
