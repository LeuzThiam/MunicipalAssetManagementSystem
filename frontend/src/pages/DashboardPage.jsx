import { useEffect, useState } from 'react'
import { api } from '../api/client'
import { useAuth } from '../context/auth'

const indicateurs = [['Bornes', '/bornes/', 'BO'], ['Bâtiments', '/batiments/', 'BA'], ['Segments de rue', '/segments-rue/', 'RR']]

export function DashboardPage() {
  const { utilisateur } = useAuth()
  const [totaux, setTotaux] = useState({})

  useEffect(() => {
    Promise.all(indicateurs.map(async ([libelle, endpoint]) => {
      const donnees = await api(endpoint)
      return [libelle, donnees.count ?? donnees.features?.length ?? 0]
    })).then((resultats) => setTotaux(Object.fromEntries(resultats))).catch(() => setTotaux({}))
  }, [])

  return (
    <div className="page">
      <header className="page-header">
        <div><p className="eyebrow">Vue d’ensemble</p><h1>Bonjour {utilisateur.prenom},</h1><p>Voici l’état actuel des données municipales.</p></div>
        <span className="date-chip">Données opérationnelles</span>
      </header>
      <section className="stats-grid" aria-label="Indicateurs principaux">
        {indicateurs.map(([libelle, , abreviation]) => (
          <article className="stat-card" key={libelle}><span className="stat-icon">{abreviation}</span><div><strong>{totaux[libelle]?.toLocaleString('fr-CA') ?? '—'}</strong><span>{libelle}</span></div></article>
        ))}
        <article className="stat-card accent-card"><span className="stat-icon">SIG</span><div><strong>3</strong><span>Couches spatiales</span></div></article>
      </section>
      <section className="dashboard-grid">
        <article className="panel map-preview">
          <div className="panel-heading"><div><p className="eyebrow">Territoire</p><h2>Aperçu cartographique</h2></div><span className="status-dot">Données disponibles</span></div>
          <div className="map-placeholder" aria-label="Emplacement réservé à la carte"><div className="map-grid" /><span className="map-pin pin-one">●</span><span className="map-pin pin-two">●</span><span className="map-pin pin-three">●</span><p>La carte interactive sera intégrée à la phase 17.</p></div>
        </article>
        <article className="panel next-actions">
          <p className="eyebrow">À surveiller</p><h2>Priorités opérationnelles</h2>
          <div className="action-item"><span>01</span><div><strong>Entretiens manquants</strong><small>Identifier les bornes à planifier</small></div></div>
          <div className="action-item"><span>02</span><div><strong>Inspections terrain</strong><small>Module prévu à la phase 19</small></div></div>
          <div className="action-item"><span>03</span><div><strong>Interventions ouvertes</strong><small>Module prévu à la phase 20</small></div></div>
        </article>
      </section>
    </div>
  )
}
