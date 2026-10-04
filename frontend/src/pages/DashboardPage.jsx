import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { api } from '../api/client'
import { useAuth } from '../context/auth'

const libellesStatuts = { OUVERTE: 'Ouvertes', PLANIFIEE: 'Planifiées', EN_COURS: 'En cours', TERMINEE: 'Terminées', ANNULEE: 'Annulées' }
const libellesEtats = { BON: 'Bon état', A_SURVEILLER: 'À surveiller', REPARATION_REQUISE: 'Réparation requise', HORS_SERVICE: 'Hors service' }

function nombre(valeur) {
  return valeur?.toLocaleString('fr-CA') ?? '—'
}

function Repartition({ titre, donnees, cleLibelle, libelles }) {
  const maximum = Math.max(...donnees.map((element) => element.total), 1)
  return <article className="panel chart-card"><div className="panel-heading"><div><p className="eyebrow">Répartition</p><h2>{titre}</h2></div></div><div className="bar-chart">{donnees.map((element) => <div className="bar-row" key={element[cleLibelle]}><span>{libelles[element[cleLibelle]] ?? element[cleLibelle]}</span><div className="bar-track"><div className="bar-fill" style={{ width: `${(element.total / maximum) * 100}%` }} /></div><strong>{element.total}</strong></div>)}{!donnees.length && <p className="empty-chart">Aucune donnée enregistrée.</p>}</div></article>
}

export function DashboardPage() {
  const { utilisateur } = useAuth()
  const [donnees, setDonnees] = useState(null)
  const [erreur, setErreur] = useState(false)

  useEffect(() => {
    api('/tableau-de-bord/').then(setDonnees).catch(() => setErreur(true))
  }, [])

  const indicateurs = [
    ['BO', 'Bornes', donnees?.bornes_total],
    ['SE', 'Sans entretien', donnees?.bornes_sans_entretien],
    ['kPa', 'Pression moyenne', donnees?.pression_moyenne],
    ['IT', 'Interventions ouvertes', donnees?.interventions_ouvertes],
    ['IN', 'Inspections ce mois', donnees?.inspections_ce_mois],
  ]

  return <div className="page"><header className="page-header"><div><p className="eyebrow">Vue d’ensemble</p><h1>Bonjour {utilisateur.prenom},</h1><p>Voici la situation opérationnelle du patrimoine municipal.</p></div><span className="date-chip">Données actualisées</span></header>{erreur && <p className="empty-state error-state">Le tableau de bord n’est pas disponible pour le moment.</p>}<section className="stats-grid dashboard-stats" aria-label="Indicateurs principaux">{indicateurs.map(([abreviation, libelle, valeur], index) => <article className={`stat-card${index === 3 ? ' accent-card' : ''}`} key={libelle}><span className="stat-icon">{abreviation}</span><div><strong>{nombre(valeur)}</strong><span>{libelle}</span></div></article>)}</section><section className="dashboard-charts"><Repartition titre="Interventions par statut" donnees={donnees?.interventions_par_statut ?? []} cleLibelle="statut" libelles={libellesStatuts} /><Repartition titre="Inspections par état" donnees={donnees?.inspections_par_etat ?? []} cleLibelle="etat" libelles={libellesEtats} /></section><section className="panel dashboard-assets"><div><p className="eyebrow">Inventaire</p><h2>Couverture des données</h2></div><div className="asset-totals"><Link to="/bornes"><strong>{nombre(donnees?.bornes_total)}</strong><span>Bornes</span></Link><Link to="/batiments"><strong>{nombre(donnees?.batiments_total)}</strong><span>Bâtiments</span></Link><Link to="/rues"><strong>{nombre(donnees?.segments_rue_total)}</strong><span>Segments de rue</span></Link><Link to="/carte"><strong>3</strong><span>Couches cartographiques</span></Link></div></section></div>
}
