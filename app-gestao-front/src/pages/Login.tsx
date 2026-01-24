import { useState, type FormEvent } from "react"
import { useNavigate } from "react-router-dom" // Importe o useNavigate
import { useAuth } from "../contexts/AuthContext"

const Login = () => {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const { signIn } = useAuth()
  const navigate = useNavigate() // Inicialize o hook

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    try {
      await signIn(email, password)
      navigate("/dashboard") // Redireciona para a rota do dashboard após o sucesso
    } catch (error) {
      console.error("Falha no login:", error)
      alert("Falha no login. Verifique o CORS ou credenciais.")
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Login</h2>

      <input
        placeholder="Email"
        value={email}
        onChange={e => setEmail(e.target.value)}
      />

      <input
        type="password"
        placeholder="Senha"
        value={password}
        onChange={e => setPassword(e.target.value)}
      />

      <button type="submit">Entrar</button>
    </form>
  )
}

export default Login

