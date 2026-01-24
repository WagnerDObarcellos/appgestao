import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, Clock, ListTodo, User } from "lucide-react";

export default function UserDashboard() {
  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard do Usuário</h1>
      {/* Resumo */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="rounded-2xl shadow">
          <CardContent className="p-6 flex items-center gap-4">
            <ListTodo className="w-8 h-8" />
            <div>
              <p className="text-sm text-gray-500">Total de Tarefas</p>
              <p className="text-2xl font-semibold">12</p>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl shadow">
          <CardContent className="p-6 flex items-center gap-4">
            <Clock className="w-8 h-8" />
            <div>
              <p className="text-sm text-gray-500">Em Andamento</p>
              <p className="text-2xl font-semibold">5</p>
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl shadow">
          <CardContent className="p-6 flex items-center gap-4">
            <CheckCircle className="w-8 h-8" />
            <div>
              <p className="text-sm text-gray-500">Concluídas</p>
              <p className="text-2xl font-semibold">7</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Lista de tarefas */}
      <Card className="rounded-2xl shadow">
        <CardContent className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">Minhas Tarefas</h2>
            <Button>Nova Tarefa</Button>
          </div>

          <ul className="space-y-3">
            <li className="flex justify-between items-center p-3 bg-white rounded-xl shadow-sm">
              <span>Estudar FastAPI</span>
              <span className="text-sm text-yellow-600">Em andamento</span>
            </li>
            <li className="flex justify-between items-center p-3 bg-white rounded-xl shadow-sm">
              <span>Finalizar Dashboard</span>
              <span className="text-sm text-green-600">Concluída</span>
            </li>
            <li className="flex justify-between items-center p-3 bg-white rounded-xl shadow-sm">
              <span>Revisar testes</span>
              <span className="text-sm text-gray-500">Rascunho</span>
            </li>
          </ul>
        </CardContent>
      </Card>

      {/* Perfil rápido */}
      <div className="mt-8">
        <Card className="rounded-2xl shadow">
          <CardContent className="p-6 flex items-center gap-4">
            <User className="w-10 h-10" />
            <div>
              <p className="font-semibold">Usuário Logado</p>
              <p className="text-sm text-gray-500">role: user</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
