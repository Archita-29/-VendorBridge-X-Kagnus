
const API_BASE = "http://localhost:8000";

export type Vendor = {
  id: number;
  vendor_name: string;
  category: string;
  contact_name: string;
  contact_email: string;
  contact_phone: string;
  gstin: string | null;
  pan: string | null;
  address: string | null;
  status: string;
};

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed (${response.status})`);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const api = {
  login: (email: string, password: string) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request("/auth/me"),

  logout: () => request<void>("/auth/logout", { method: "POST" }),

forgotPassword: (email: string) =>
  request<{ message: string; reset_token?: string }>(
    "/auth/forgot-password",
    {
      method: "POST",
      body: JSON.stringify({ email }),
    }
  ),

  resetPassword: (token: string, new_password: string) =>
    request<{ message: string }>(
      "/auth/reset-password",
      {
        method: "POST",
        body: JSON.stringify({ token, new_password }),
      }
    ),

  listVendors: () => request<Vendor[]>("/vendors/"),

  createVendor: (vendor: {
    vendor_name: string;
    category: string;
    contact_name: string;
    contact_email: string;
    contact_phone: string;
    gstin?: string;
    pan?: string;
    address?: string;
  }) =>
    request<Vendor>("/vendors/", {
      method: "POST",
      body: JSON.stringify(vendor),
    }),

  dashboardSummary: () =>
    request<{
      total_vendors: number;
      pending_vendors: number;
      approved_vendors: number;
    }>("/dashboard/summary"),

};
