import { Navigate, Outlet, useLocation } from 'react-router'
import { useAuth } from '../context/auth'

export function ProtectedRoute() {
  const { utilisateur, chargement } = useAuth()
  const emplacement = useLocation()
  if (chargement) return <div className="page-loading">Chargement de votre espace…</div>
  if (!utilisateur) return <Navigate to="/connexion" state={{ from: emplacement }} replace />
  return <Outlet />
}
