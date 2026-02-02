import { createContext, useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

type User = {
  email: string;
  role: "user" | "admin";
};

type AuthContextType = {
  user: User | null;
  token: string | null;
  signIn: (token: string, user: User) => void;
  signOut: () => void;
  isAuthenticated: boolean;
};

const AuthContext = createContext<AuthContextType>({} as AuthContextType);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // 1. useEffect movido para o escopo correto (fora das funções)
  useEffect(() => {
  const storedToken = localStorage.getItem("token");
  const storedUser = localStorage.getItem("user");

  if (storedToken && storedUser && storedUser !== "undefined") {
    try {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    } catch {
      localStorage.clear();
    }
  }

  setLoading(false);
}, []);


  // 2. Apenas UMA declaração da função signIn
  function signIn(receivedToken: string, receivedUser: User) {
    if (!receivedToken || !receivedUser) {
      throw new Error("Dados de autenticação inválidos");
    }

    localStorage.setItem("token", receivedToken);
    localStorage.setItem("user", JSON.stringify(receivedUser));

    setToken(receivedToken);
    setUser(receivedUser);

    navigate("/dashboard");
  }

  function signOut() {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
    navigate("/");
  }

  return (
    <AuthContext.Provider value={{ 
      user, 
      token, 
      signIn, 
      signOut, 
      isAuthenticated: !!token 
    }}>
      {!loading && children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
