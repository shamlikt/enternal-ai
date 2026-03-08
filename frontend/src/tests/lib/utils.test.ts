/**
 * Tests for the cn() utility function (clsx + tailwind-merge).
 */
import { describe, it, expect } from "vitest";
import { cn } from "@/lib/utils";

describe("cn", () => {
  it("returns a single class unchanged", () => {
    expect(cn("text-white")).toBe("text-white");
  });

  it("merges multiple classes", () => {
    const result = cn("text-white", "bg-black");
    expect(result).toContain("text-white");
    expect(result).toContain("bg-black");
  });

  it("deduplicates conflicting tailwind classes (last wins)", () => {
    // tailwind-merge: conflicting classes — later one wins
    const result = cn("text-red-500", "text-blue-500");
    expect(result).toBe("text-blue-500");
    expect(result).not.toContain("text-red-500");
  });

  it("handles conditional classes with clsx falsy values", () => {
    const result = cn("base", false && "hidden", undefined, null, "extra");
    expect(result).toContain("base");
    expect(result).toContain("extra");
    expect(result).not.toContain("hidden");
    expect(result).not.toContain("undefined");
    expect(result).not.toContain("null");
  });

  it("handles object syntax from clsx", () => {
    const result = cn({ "text-white": true, "text-black": false });
    expect(result).toBe("text-white");
  });

  it("handles array syntax", () => {
    const result = cn(["flex", "items-center"]);
    expect(result).toContain("flex");
    expect(result).toContain("items-center");
  });

  it("returns empty string for no arguments", () => {
    expect(cn()).toBe("");
  });

  it("merges padding classes (tailwind-merge dedup)", () => {
    // p-4 and px-6 — both apply in tailwind-merge (no conflict)
    const result = cn("p-4", "px-6");
    // tailwind-merge keeps both since px-6 overrides the x-axis padding from p-4
    expect(result).toContain("px-6");
  });
});
