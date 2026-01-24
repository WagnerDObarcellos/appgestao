import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
// 1. Importe o AuthProvider que você criou:
import { AuthProvider } from './contexts/AuthContext.tsx'; 

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {/* 2. Envolva o App com o AuthProvider: */}
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
