import { Navigate, Outlet, useLocation } from 'react-router'
import { useAuth } from '../context/auth'

export function ProtectedRoute() {
  const { utilisateur, chargement } = useAuth()
  const emplacement = useLocation()
  if (chargement) return <div className="page-loading">Chargement de votre espace…</div>
  if (!utilisateur) return <Navigate to="/connexion" state={{ from: emplacement }} replace />
  return <Outlet />
}

export function RoleRoute({ role }) {
  const { utilisateur } = useAuth()
  if (utilisateur?.role !== role) return <Navigate to="/tableau-de-bord" replace />
  return <Outlet />
}
