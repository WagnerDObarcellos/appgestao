import { createContext, useContext, useState, type ReactNode } from "react"
import api from "../api/client"

type User = {
  email: string
}

type AuthContextData = {
  user: User | null
  token: string | null
  signIn: (email: string, password: string) => Promise<void>
  signOut: () => void
}

const AuthContext = createContext<AuthContextData>({} as AuthContextData)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)

  async function signIn(email: string, password: string) {
    const data = new URLSearchParams()
    data.append("username", email) // OAuth2 espera "username"
    data.append("password", password)

    const response = await api.post("/auth/token", data, {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    })

    const { access_token } = response.data

    setToken(access_token)
    setUser({ email })
  }

  function signOut() {
    setUser(null)
    setToken(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, signIn, signOut }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
