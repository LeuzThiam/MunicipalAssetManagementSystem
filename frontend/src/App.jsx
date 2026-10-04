import { Navigate, Route, Routes } from 'react-router'
import { AppShell } from './components/AppShell'
import { ProtectedRoute, RoleRoute } from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'
import { AdministrationPage } from './pages/AdministrationPage'
import { DashboardPage } from './pages/DashboardPage'
import { LoginPage } from './pages/LoginPage'
import { InspectionsPage } from './pages/InspectionsPage'
import { MapPage } from './pages/MapPage'
import { ResourcePage } from './pages/ResourcePage'
import { WorkflowsPage } from './pages/WorkflowsPage'
import { ressources } from './resources'

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/connexion" element={<LoginPage />} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppShell />}>
            <Route index element={<Navigate to="/tableau-de-bord" replace />} />
            <Route path="/tableau-de-bord" element={<DashboardPage />} />
            <Route path="/bornes" element={<ResourcePage {...ressources.bornes} />} />
            <Route path="/batiments" element={<ResourcePage {...ressources.batiments} />} />
            <Route path="/rues" element={<ResourcePage {...ressources.rues} />} />
            <Route path="/carte" element={<MapPage />} />
            <Route path="/inspections" element={<InspectionsPage />} />
            <Route path="/interventions" element={<WorkflowsPage type="interventions" />} />
            <Route element={<RoleRoute role="ADMIN" />}>
              <Route path="/administration" element={<AdministrationPage />} />
            </Route>
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/tableau-de-bord" replace />} />
      </Routes>
    </AuthProvider>
  )
}

export default App
