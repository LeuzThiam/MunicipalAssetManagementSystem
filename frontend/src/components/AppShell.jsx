import { NavLink, Outlet } from 'react-router'
import { useAuth } from '../context/auth'

const navigation = [
  ['Tableau de bord', '/tableau-de-bord', 'TB'],
  ['Bornes', '/bornes', 'BO'],
  ['Bâtiments', '/batiments', 'BA'],
  ['Réseau routier', '/rues', 'RR'],
  ['Carte', '/carte', 'CA'],
  ['Inspections', '/inspections', 'IN'],
  ['Interventions', '/interventions', 'IT'],
]

export function AppShell() {
  const { utilisateur, deconnexion } = useAuth()
  const liens = utilisateur.role === 'ADMIN'
    ? [...navigation, ['Administration', '/administration', 'AD']]
    : navigation

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark">MA</span>
          <span><strong>Actifs municipaux</strong><small>Centre opérationnel</small></span>
        </div>
        <nav aria-label="Navigation principale">
          {liens.map(([libelle, chemin, abreviation]) => (
            <NavLink key={chemin} to={chemin}>
              <span className="nav-icon" aria-hidden="true">{abreviation}</span>
              {libelle}
            </NavLink>
          ))}
        </nav>
        <div className="user-card">
          <span className="avatar">{utilisateur.prenom?.[0]}{utilisateur.nom?.[0]}</span>
          <span className="user-info"><strong>{utilisateur.prenom} {utilisateur.nom}</strong><small>{utilisateur.role}</small></span>
          <button type="button" onClick={deconnexion} aria-label="Se déconnecter">↗</button>
        </div>
      </aside>
      <main className="main-content"><Outlet /></main>
    </div>
  )
}
