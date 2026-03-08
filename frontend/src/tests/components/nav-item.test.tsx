/**
 * Unit tests for NavItem component.
 *
 * NavItem uses usePathname to determine if the current route matches
 * the item's href, and conditionally applies active styling.
 */
import { render, screen } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { NavItem } from "@/components/sidebar/nav-item";
import { BarChart2 } from "lucide-react";

// Mock next/navigation to control pathname without needing a real router
vi.mock("next/navigation", () => ({
  usePathname: vi.fn(),
}));

// Mock next/link to render a plain anchor (no Next.js router required)
vi.mock("next/link", () => ({
  default: ({ href, children, ...props }: React.AnchorHTMLAttributes<HTMLAnchorElement> & { href: string }) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

import { usePathname } from "next/navigation";

describe("NavItem", () => {
  beforeEach(() => {
    vi.mocked(usePathname).mockReturnValue("/other-page");
  });

  it("renders the label when not collapsed", () => {
    render(
      <NavItem href="/dashboard" label="Dashboard" icon={BarChart2} collapsed={false} />
    );
    expect(screen.getByText("Dashboard")).toBeInTheDocument();
  });

  it("does not render the label text when collapsed", () => {
    render(
      <NavItem href="/dashboard" label="Dashboard" icon={BarChart2} collapsed={true} />
    );
    expect(screen.queryByText("Dashboard")).not.toBeInTheDocument();
  });

  it("sets title attribute when collapsed (for tooltip)", () => {
    render(
      <NavItem href="/dashboard" label="Dashboard" icon={BarChart2} collapsed={true} />
    );
    const link = screen.getByRole("link");
    expect(link).toHaveAttribute("title", "Dashboard");
  });

  it("does not set title when not collapsed", () => {
    render(
      <NavItem href="/dashboard" label="Dashboard" icon={BarChart2} collapsed={false} />
    );
    const link = screen.getByRole("link");
    expect(link).not.toHaveAttribute("title");
  });

  it("links to the correct href", () => {
    render(
      <NavItem href="/sql-editor" label="SQL Editor" icon={BarChart2} collapsed={false} />
    );
    expect(screen.getByRole("link")).toHaveAttribute("href", "/sql-editor");
  });

  it("has active class when pathname matches href exactly", () => {
    vi.mocked(usePathname).mockReturnValue("/dashboard");
    render(
      <NavItem href="/dashboard" label="Dashboard" icon={BarChart2} collapsed={false} />
    );
    // Active state is applied via bg-[var(--sidebar-active)] class
    const link = screen.getByRole("link");
    expect(link.className).toContain("text-white");
  });

  it("has active class when pathname starts with href", () => {
    vi.mocked(usePathname).mockReturnValue("/dashboard/overview");
    render(
      <NavItem href="/dashboard" label="Dashboard" icon={BarChart2} collapsed={false} />
    );
    const link = screen.getByRole("link");
    expect(link.className).toContain("text-white");
  });

  it("does not have active class when pathname does not match", () => {
    vi.mocked(usePathname).mockReturnValue("/agent");
    render(
      <NavItem href="/dashboard" label="Dashboard" icon={BarChart2} collapsed={false} />
    );
    const link = screen.getByRole("link");
    // Should not have the active background class
    expect(link.className).not.toContain("bg-[var(--sidebar-active)]");
  });
});
