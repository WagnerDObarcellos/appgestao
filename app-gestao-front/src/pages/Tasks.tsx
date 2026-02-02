// src/services/api.ts
const BASE_URL = "http://localhost:8000";

interface ApiOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE";
  body?: any;
  token?: string | null;
}

export async function apiFetch<T>(
  endpoint: string, 
  options: ApiOptions = {} // Agora usamos um objeto de opções
): Promise<T> {
  const { method = "GET", body, token } = options;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    const error = new Error("Erro na requisição");
    (error as any).status = response.status;
    throw error;
  }

  return response.json();
}
