/**
 * API client for Msg-Pilot backend.
 * All requests are proxied through Next.js rewrite to /api/*
 */

const BASE = "/api";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(opts.headers as Record<string, string> || {}),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (!(opts.body instanceof FormData)) headers["Content-Type"] = "application/json";

  const res = await fetch(`${BASE}${path}`, { ...opts, headers });

  if (res.status === 401) {
    localStorage.removeItem("token");
    window.location.href = "/auth";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ── Auth ──
export const auth = {
  signup: (data: { email: string; full_name: string; password: string }) =>
    request<{ access_token: string }>("/auth/signup", { method: "POST", body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    request<{ access_token: string }>("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  me: () => request<{ id: string; email: string; full_name: string; role: string }>("/auth/me"),
};

// ── Dashboard ──
export const dashboard = {
  stats: () => request<any>("/dashboard/stats"),
};

// ── Contacts ──
export const contacts = {
  list: (params?: string) => request<any[]>(`/contacts/${params ? "?" + params : ""}`),
  create: (data: any) => request<any>("/contacts/", { method: "POST", body: JSON.stringify(data) }),
  delete: (id: string) => request<void>(`/contacts/${id}`, { method: "DELETE" }),
  uploadPreview: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return request<any[]>("/contacts/upload/preview", { method: "POST", body: fd });
  },
  uploadConfirm: (file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return request<any>("/contacts/upload/confirm", { method: "POST", body: fd });
  },
  tags: () => request<any[]>("/contacts/tags"),
  createTag: (name: string) => request<any>("/contacts/tags", { method: "POST", body: JSON.stringify({ name }) }),
};

// ── Campaigns ──
export const campaigns = {
  list: () => request<any[]>("/campaigns/"),
  get: (id: string) => request<any>(`/campaigns/${id}`),
  create: (data: any) => request<any>("/campaigns/", { method: "POST", body: JSON.stringify(data) }),
  contacts: (id: string) => request<any[]>(`/campaigns/${id}/contacts`),
  start: (id: string) => request<any>(`/campaigns/${id}/start`, { method: "POST" }),
  pause: (id: string) => request<any>(`/campaigns/${id}/pause`, { method: "POST" }),
  stop: (id: string) => request<any>(`/campaigns/${id}/stop`, { method: "POST" }),
  uploadMedia: (id: string, file: File) => {
    const fd = new FormData();
    fd.append("file", file);
    return request<any>(`/campaigns/${id}/media`, { method: "POST", body: fd });
  },
};

// ── Logs ──
export const logs = {
  list: (skip = 0, limit = 100) => request<any[]>(`/logs/?skip=${skip}&limit=${limit}`),
};

// ── WhatsApp ──
export const whatsapp = {
  status: () => request<{ has_session: boolean }>("/whatsapp/session/status"),
  qr: () => request<{ qr: string | null; status: string }>("/whatsapp/session/qr", { method: "POST" }),
  logout: () => request<any>("/whatsapp/session/logout", { method: "POST" }),
};
