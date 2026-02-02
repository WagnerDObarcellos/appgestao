import { useState } from "react";
import { useAuth } from "@/contexts/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { signIn } = useAuth();

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault()

  const formData = new URLSearchParams()
  formData.append("username", email)
  formData.append("password", password)
  
try{
  const response = await fetch("http://localhost:8000/auth/token", {
    method: "POST",
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    body: formData,
  })

  if (!response.ok) {
    throw new Error("Credenciais inválidas")
  }

  const data = await response.json()
  signIn(data.access_token, data.user)
}catch (err) {
      console.error(err);
      alert("Falha no login. Verifique seus dados.");
    }
  };


  return (
    <form onSubmit={handleSubmit}>
      <input placeholder="Email" onChange={e => setEmail(e.target.value)} />
      <input type="password" placeholder="Senha" onChange={e => setPassword(e.target.value)} />
      <button>Entrar</button>
    </form>
  );
}
