"use client";

import { useRouter } from "next/navigation";
import { LogOut, User } from "lucide-react";
import { useAuth } from "@/lib/auth";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

interface SidebarUserMenuProps {
  collapsed: boolean;
}

export function SidebarUserMenu({ collapsed }: SidebarUserMenuProps) {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (!user) return null;

  const initials = user.username.slice(0, 2).toUpperCase();

  return (
    <div className={cn("px-2 py-3", collapsed && "flex flex-col items-center")}>
      {collapsed ? (
        <div className="flex flex-col items-center gap-2">
          <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-white text-xs font-medium">
            {initials}
          </div>
          <button
            onClick={handleLogout}
            title="Logout"
            className="flex items-center justify-center w-8 h-8 rounded-md text-[var(--sidebar-muted)] hover:text-white hover:bg-[var(--sidebar-hover)] transition-colors"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center gap-2 px-1">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-primary text-white text-xs font-medium shrink-0">
              {initials}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {user.username}
              </p>
              <p className="text-xs text-[var(--sidebar-muted)] truncate">
                {user.email}
              </p>
            </div>
          </div>
          <div className="flex items-center justify-between px-1">
            <Badge
              variant="secondary"
              className="text-xs bg-[var(--sidebar-active)] text-[var(--sidebar-fg)] border-0"
            >
              <User className="h-3 w-3 mr-1" />
              {user.role}
            </Badge>
            <button
              onClick={handleLogout}
              className="flex items-center gap-1 text-xs text-[var(--sidebar-muted)] hover:text-white transition-colors"
            >
              <LogOut className="h-3 w-3" />
              Logout
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
