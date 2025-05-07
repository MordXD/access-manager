// frontend/src/App.tsx
import { useState, useEffect } from 'react';
import LoginForm from './components/LoginForm';
import UserList from './components/UserList';

function App() {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('accessToken');
    if (storedToken) {
      setToken(storedToken);
    }
  }, []);

  const handleLoginSuccess = (newToken: string) => {
    localStorage.setItem('accessToken', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    setToken(null);
    // Можно добавить редирект на страницу логина или обновление состояния для UI
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-sky-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-400 to-light-blue-500 shadow-lg transform -skew-y-6 sm:skew-y-0 sm:-rotate-6 sm:rounded-3xl"></div>
        <div className="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <div className="max-w-md mx-auto">
            <div>
              <h1 className="text-4xl font-extrabold text-center text-gray-800 tracking-tight sm:text-5xl">
                Access Manager
              </h1>
            </div>
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                {token && (
                  <div className="flex justify-end">
                    <button
                      onClick={handleLogout}
                      className="mb-6 px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      Logout
                    </button>
                  </div>
                )}
                {!token ? (
                  <LoginForm onLoginSuccess={handleLoginSuccess} />
                ) : (
                  <div>
                    <p className="text-center text-green-600 mb-4 text-lg">
                      You are logged in!
                    </p>
                    <UserList />
                    {/* Сюда можно добавить другие компоненты, защищенные аутентификацией */}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
export default App;