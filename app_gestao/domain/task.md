# Task

## Descrição
Uma Task representa uma demanda administrativa que precisa ser executada
por um usuário dentro do sistema.

## Campos

- id: Identificador único da task
- title: Título curto da tarefa
- description: Descrição detalhada
- status: Estado atual da task
- priority: Nível de prioridade
- due_date: Data limite para conclusão
- created_at: Data de criação
- updated_at: Última atualização
- created_by: Usuário que criou a task
- assigned_to: Usuário responsável pela execução

## Regras de Negócio

- Toda task deve ter um `created_by`
- Toda task deve ter um `status`
- `assigned_to` pode ser nulo no momento da criação
- Apenas administradores podem atribuir responsáveis
