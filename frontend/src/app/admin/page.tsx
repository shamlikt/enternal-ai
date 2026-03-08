"use client";

import Link from "next/link";
import { AppLayout } from "@/components/sidebar/app-layout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Users, Activity, Shield, FileText } from "lucide-react";

const ADMIN_SECTIONS = [
  {
    href: "/admin/users",
    title: "User Management",
    description: "Create, edit, and manage user accounts and roles",
    icon: Users,
  },
  {
    href: "/admin/health",
    title: "System Health",
    description: "Monitor database, ingestion health and error counts",
    icon: Activity,
  },
  {
    href: "/admin/audit",
    title: "Audit Log",
    description: "View all user actions and data access logs",
    icon: Shield,
  },
  {
    href: "/admin/logs",
    title: "Application Logs",
    description: "View application and ingestion logs",
    icon: FileText,
  },
];

export default function AdminPage() {
  return (
    <AppLayout requiredRole="admin">
      <div className="p-6 space-y-6">
        <div>
          <h1 className="text-2xl font-semibold">Admin</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Platform administration and monitoring
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {ADMIN_SECTIONS.map((section) => {
            const Icon = section.icon;
            return (
              <Link key={section.href} href={section.href}>
                <Card className="cursor-pointer hover:shadow-md transition-shadow h-full">
                  <CardHeader className="pb-2">
                    <Icon className="h-6 w-6 text-primary mb-2" />
                    <CardTitle className="text-base">{section.title}</CardTitle>
                    <CardDescription className="text-xs">
                      {section.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent />
                </Card>
              </Link>
            );
          })}
        </div>
      </div>
    </AppLayout>
  );
}
