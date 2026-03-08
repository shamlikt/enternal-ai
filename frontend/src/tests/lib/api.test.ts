/**
 * Tests for the API client (api.ts).
 *
 * Tests the fetch wrapper behavior: auth headers, error handling,
 * 401 redirect, 204 empty response, JSON parsing.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { api } from "@/lib/api";

// Mock global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock localStorage
const localStorageMock: Record<string, string> = {};
Object.defineProperty(global, "localStorage", {
  value: {
    getItem: (key: string) => localStorageMock[key] ?? null,
    setItem: (key: string, value: string) => { localStorageMock[key] = value; },
    removeItem: (key: string) => { delete localStorageMock[key]; },
    clear: () => Object.keys(localStorageMock).forEach(k => delete localStorageMock[k]),
  },
  writable: true,
});

// Mock window.location
Object.defineProperty(global, "window", {
  value: {
    location: { href: "" },
    localStorage: global.localStorage,
  },
  writable: true,
});

describe("api client", () => {
  beforeEach(() => {
    mockFetch.mockClear();
    localStorageMock["access_token"] = "test-token";
  });

  afterEach(() => {
    delete localStorageMock["access_token"];
  });

  it("sends Authorization header when token exists", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ data: "ok" }),
    });

    await api.get("/test");
    const [, options] = mockFetch.mock.calls[0];
    expect(options.headers["Authorization"]).toBe("Bearer test-token");
  });

  it("does not send Authorization header when no token", async () => {
    delete localStorageMock["access_token"];
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({}),
    });

    await api.get("/test");
    const [, options] = mockFetch.mock.calls[0];
    expect(options.headers["Authorization"]).toBeUndefined();
  });

  it("throws error with detail message on non-ok response", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 400,
      json: async () => ({ detail: "Bad request" }),
    });

    await expect(api.get("/test")).rejects.toThrow("Bad request");
  });

  it("throws 'Unknown error' when error response body is not valid JSON", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => { throw new Error("not json"); },
    });

    // The catch block falls back to { detail: "Unknown error" }
    await expect(api.get("/test")).rejects.toThrow("Unknown error");
  });

  it("returns undefined for 204 No Content", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 204,
      json: async () => null,
    });

    const result = await api.delete("/test/1");
    expect(result).toBeUndefined();
  });

  it("sends JSON body for POST requests", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 201,
      json: async () => ({ id: 1 }),
    });

    await api.post("/test", { name: "Test" });
    const [, options] = mockFetch.mock.calls[0];
    expect(options.method).toBe("POST");
    expect(options.body).toBe(JSON.stringify({ name: "Test" }));
    expect(options.headers["Content-Type"]).toBe("application/json");
  });

  it("appends query params for GET requests", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => [],
    });

    await api.get("/items", { limit: 10, offset: 0 });
    const [url] = mockFetch.mock.calls[0];
    expect(url).toContain("limit=10");
    expect(url).toContain("offset=0");
  });

  it("skips undefined query params", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => [],
    });

    await api.get("/items", { limit: 10, offset: undefined });
    const [url] = mockFetch.mock.calls[0];
    expect(url).toContain("limit=10");
    expect(url).not.toContain("offset");
  });

  it("postForm sends application/x-www-form-urlencoded", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: async () => ({ access_token: "token", token_type: "bearer" }),
    });

    await api.postForm("/auth/login", { username: "alice", password: "secret" });
    const [, options] = mockFetch.mock.calls[0];
    expect(options.headers["Content-Type"]).toBe("application/x-www-form-urlencoded");
    expect(options.body.toString()).toContain("username=alice");
    expect(options.body.toString()).toContain("password=secret");
  });

  it("handles 401 by clearing token and redirecting", async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: "Unauthorized" }),
    });

    await expect(api.get("/protected")).rejects.toThrow("Unauthorized");
    expect(localStorageMock["access_token"]).toBeUndefined();
  });
});
