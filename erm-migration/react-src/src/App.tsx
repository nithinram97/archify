import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import DashboardListPage from './pages/DashboardListPage';
import DashboardViewPage from './pages/DashboardViewPage';
import React, { useState, useEffect } from 'react';
import { client } from './client';
import { Users } from '@osdk/foundry.admin';
import { ToastProvider } from './context/ToastContext';

const Layout = ({ children }: { children: React.ReactNode }) => (
  <div className="min-h-screen bg-slate-50 font-sans">
    <main>{children}</main>
  </div>
);

export default function App() {
  const [userEmail, setUserEmail] = useState<string | null>(null);

  useEffect(() => {
    const fetchUser = async () => {
      try {
        const user = await Users.getCurrent(client);
        setUserEmail(user.email || user.username || user.id);
      } catch (error) {
        console.error('Failed to fetch user:', error);
      }
    };

    fetchUser();
  }, []);

  if (userEmail === null) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-slate-50">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-airbus-navy border-t-transparent"></div>
      </div>
    );
  }

  return (
    <ToastProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboards" replace />} />

            {/* Main Dashboards Listing Route */}
            <Route path="/dashboards" element={<DashboardListPage currentUserEmail={userEmail} />} />

            {/* New Dashboard View Route matching tabs like /maps, /table, /action-tracker, /summary, /report, /full-search */}
            <Route path="/dashboard/:dashboardId/*" element={<DashboardViewPage currentUserEmail={userEmail} />} />

            {/* Auth Callback Route */}
            <Route path="/auth/callback" element={<DashboardListPage currentUserEmail={userEmail} />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </ToastProvider>
  );
}
