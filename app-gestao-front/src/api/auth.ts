// api/auth.ts
import api from "./client"

export async function login(email: string, password: string) {
  const response = await api.post("/auth/login", { email, password })
  return response.data
}
