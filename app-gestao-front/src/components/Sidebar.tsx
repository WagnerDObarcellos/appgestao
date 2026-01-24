export default function Sidebar() {
  return (
    <nav className="w-64 h-full bg-gray-800 text-white p-4">
      <h2 className="text-xl font-bold mb-4">Menu</h2>
      <ul>
        <li className="mb-2"><a href="/dashboard">Home</a></li>
        <li className="mb-2"><a href="/user-dashboard">Meu Perfil</a></li>
      </ul>
    </nav>
  );
}
