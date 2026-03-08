"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import { Sidebar } from "./sidebar";
import { CommandPalette } from "@/components/ui/command-palette";
import type { Role } from "@/types";

interface AppLayoutProps {
  children: React.ReactNode;
  requiredRole?: Role;
}

export function AppLayout({ children, requiredRole }: AppLayoutProps) {
  const { isAuthenticated, isLoading, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace("/login");
    }
  }, [isAuthenticated, isLoading, router]);

  useEffect(() => {
    if (!isLoading && isAuthenticated && requiredRole && user) {
      const roleHierarchy: Record<Role, number> = {
        admin: 3,
        analyst: 2,
        viewer: 1,
      };
      if (roleHierarchy[user.role] < roleHierarchy[requiredRole]) {
        router.replace("/dashboard");
      }
    }
  }, [isLoading, isAuthenticated, user, requiredRole, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        {children}
      </main>
      <CommandPalette />
    </div>
  );
}
