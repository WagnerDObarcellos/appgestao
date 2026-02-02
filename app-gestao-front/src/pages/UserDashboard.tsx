import { useEffect, useState, type ReactNode } from "react";
import { apiFetch } from "@/services/api";
import { useAuth } from "@/contexts/AuthContext";
import { Card, CardContent } from "@/components/ui/card";

import {
  DndContext,
  PointerSensor,
  useSensor,
  useSensors,
  useDroppable,
} from "@dnd-kit/core";

import type { DragEndEvent } from "@dnd-kit/core";

import {
  SortableContext,
  verticalListSortingStrategy,
  useSortable,
} from "@dnd-kit/sortable";

import { CSS } from "@dnd-kit/utilities";

/* =========================
   TIPOS
========================= */

type TodoState = "draft" | "todo" | "doing" | "done" | "trash";
type KanbanState = "todo" | "doing" | "done";

type Todo = {
  id: number;
  title: string;
  state: TodoState;
};

interface TodoListResponse<T> {
  todos: T[];
}

/* =========================
   ESTILOS
========================= */

const stateStyle: Record<TodoState, string> = {
  draft: "bg-gray-200 text-gray-700",
  todo: "bg-blue-100 text-blue-700",
  doing: "bg-amber-100 text-amber-700",
  done: "bg-green-100 text-green-700",
  trash: "bg-red-100 text-red-700",
};

/* =========================
   COMPONENTES
========================= */

function KanbanColumn({
  id,
  title,
  count,
  children,
}: {
  id: KanbanState;
  title: string;
  count: number;
  children: ReactNode;
}) {
  const { setNodeRef, isOver } = useDroppable({ id });

  return (
    <div
      ref={setNodeRef}
      className={`bg-gray-50 rounded-xl p-4 border transition
        ${isOver ? "border-blue-400 bg-blue-50" : "border-gray-200"}`}
    >
      <h3 className="font-semibold mb-4 text-gray-700">
        {title}
        <span className="ml-2 text-sm text-gray-400">({count})</span>
      </h3>

      <ul className="space-y-3 min-h-[60px]">{children}</ul>
    </div>
  );
}

function DraggableTodo({ todo }: { todo: Todo }) {
  const { attributes, listeners, setNodeRef, transform, transition } =
    useSortable({ id: todo.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <li
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      className="bg-white p-4 rounded-lg border border-gray-100 hover:shadow-sm transition cursor-grab active:cursor-grabbing"
    >
      <p className="font-medium text-gray-700">{todo.title}</p>

      <span
        className={`inline-block mt-2 text-xs px-2 py-1 rounded-full uppercase font-bold ${stateStyle[todo.state]}`}
      >
        {todo.state}
      </span>
    </li>
  );
}

/* =========================
   DASHBOARD
========================= */

export default function UserDashboard() {
  const { token, signOut } = useAuth();

  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(true);

  /* Hooks SEMPRE no topo */
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 5 },
    })
  );

  useEffect(() => {
    if (!token) {
      setLoading(false);
      return;
    }

    let mounted = true;

    apiFetch<TodoListResponse<Todo>>("/todos/", "GET", undefined, token)
      .then((data) => mounted && setTodos(data?.todos ?? []))
      .catch((err) => {
        console.error(err);
        if (err?.status === 401) signOut();
      })
      .finally(() => mounted && setLoading(false));

    return () => {
      mounted = false;
    };
  }, [token, signOut]);

  /* =========================
     DERIVAÇÕES
  ========================= */

  const columns = [
    { id: "todo", title: "A fazer" },
    { id: "doing", title: "Em andamento" },
    { id: "done", title: "Concluídas" },
  ] as const;

  const todosByState: Record<KanbanState, Todo[]> = {
    todo: todos.filter((t) => t.state === "todo"),
    doing: todos.filter((t) => t.state === "doing"),
    done: todos.filter((t) => t.state === "done"),
  };

  const stats = {
    todo: todosByState.todo.length,
    doing: todosByState.doing.length,
    done: todosByState.done.length,
  };

  /* =========================
     DRAG
  ========================= */

  function handleDragEnd({ active, over }: DragEndEvent) {
    if (!over) return;

    const draggedId = Number(active.id);

    // drop em coluna
    if (typeof over.id === "string") {
      const newState = over.id as KanbanState;

      setTodos((prev) =>
        prev.map((todo) =>
          todo.id === draggedId ? { ...todo, state: newState } : todo
        )
      );
    }
  }

  /* =========================
     RENDER
  ========================= */

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <p className="text-gray-500 animate-pulse">
          Carregando dashboard...
        </p>
      </div>
    );
  }

  return (
    <div className="p-1">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">
        Dashboard do Usuário
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {columns.map((c) => (
          <Card key={c.id}>
            <CardContent className="p-6">
              <p className="text-sm text-gray-500 font-medium">{c.title}</p>
              <p className={`text-xs font-bold ${stateStyle[c.id]}`}>
                {stats[c.id]}
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <DndContext sensors={sensors} onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {columns.map((column) => (
            <KanbanColumn
              key={column.id}
              id={column.id}
              title={column.title}
              count={todosByState[column.id].length}
            >
              <SortableContext
                items={todosByState[column.id].map((t) => t.id)}
                strategy={verticalListSortingStrategy}
              >
                {todosByState[column.id].map((todo) => (
                  <DraggableTodo key={todo.id} todo={todo} />
                ))}
              </SortableContext>
            </KanbanColumn>
          ))}
        </div>
      </DndContext>
    </div>
  );
}
