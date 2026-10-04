import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'
import { api } from '../api/client'
import { useAuth } from '../context/auth'

const types = [['ENTRETIEN', 'Entretien'], ['REPARATION', 'Réparation'], ['REMPLACEMENT', 'Remplacement'], ['URGENCE', 'Urgence']]
const priorites = [['BASSE', 'Basse'], ['NORMALE', 'Normale'], ['HAUTE', 'Haute'], ['URGENTE', 'Urgente']]
const statuts = [['OUVERTE', 'Ouverte'], ['PLANIFIEE', 'Planifiée'], ['EN_COURS', 'En cours'], ['TERMINEE', 'Terminée'], ['ANNULEE', 'Annulée']]

function libelle(options, valeur) {
  return options.find(([code]) => code === valeur)?.[1] ?? valeur
}

function dateLisible(valeur) {
  if (!valeur) return 'Non planifiée'
  return new Date(valeur).toLocaleString('fr-CA', { dateStyle: 'medium', timeStyle: 'short' })
}

function maintenantISO() {
  return new Date().toISOString()
}

export function InterventionsPage() {
  const { utilisateur } = useAuth()
  const [parametres, setParametres] = useSearchParams()
  const borne = parametres.get('borne') ?? ''
  const [interventions, setInterventions] = useState([])
  const [etatPage, setEtatPage] = useState('chargement')
  const [erreur, setErreur] = useState('')
  const [formulaire, setFormulaire] = useState({ type: 'ENTRETIEN', priorite: 'NORMALE', statut: 'OUVERTE', description: '', planifiee_le: '' })
  const peutGerer = ['ADMIN', 'GESTIONNAIRE'].includes(utilisateur?.role)
  const creationOuverte = parametres.get('action') === 'nouvelle' && borne && peutGerer

  useEffect(() => {
    const suffixe = borne ? `?borne=${borne}` : ''
    api(`/interventions/${suffixe}`)
      .then((reponse) => {
        setInterventions(reponse.results ?? [])
        setEtatPage('pret')
      })
      .catch(() => setEtatPage('erreur'))
  }, [borne])

  function modifier(champ, valeur) {
    setFormulaire((courant) => ({ ...courant, [champ]: valeur }))
  }

  async function enregistrer(event) {
    event.preventDefault()
    setErreur('')
    try {
      const intervention = await api('/interventions/', {
        method: 'POST',
        body: JSON.stringify({ ...formulaire, borne: Number(borne), planifiee_le: formulaire.planifiee_le || null }),
      })
      setInterventions((courantes) => [intervention, ...courantes])
      setParametres({ borne })
    } catch (cause) {
      setErreur(cause.message)
    }
  }

  async function changerStatut(intervention, statut) {
    setErreur('')
    try {
      const termineeLe = statut === 'TERMINEE' ? maintenantISO() : intervention.terminee_le
      const miseAJour = await api(`/interventions/${intervention.id}/`, {
        method: 'PATCH',
        body: JSON.stringify({ statut, terminee_le: termineeLe }),
      })
      setInterventions((courantes) => courantes.map((element) => element.id === miseAJour.id ? miseAJour : element))
    } catch (cause) {
      setErreur(cause.message)
    }
  }

  return (
    <div className="page">
      <header className="page-header"><div><p className="eyebrow">Travaux municipaux</p><h1>Interventions</h1><p>Planifiez les travaux sur les bornes et suivez leur progression.</p></div>{borne && peutGerer && <button className="secondary-button" type="button" onClick={() => setParametres({ borne, action: 'nouvelle' })}>Nouvelle intervention</button>}</header>
      {creationOuverte && <section className="panel inspection-form-panel"><div className="panel-heading"><div><p className="eyebrow">Borne #{borne}</p><h2>Nouvelle intervention</h2></div><button className="close-button" type="button" aria-label="Fermer le formulaire" onClick={() => setParametres({ borne })}>×</button></div><form className="inspection-form" onSubmit={enregistrer}><label>Type<select value={formulaire.type} onChange={(event) => modifier('type', event.target.value)}>{types.map(([valeur, texte]) => <option key={valeur} value={valeur}>{texte}</option>)}</select></label><label>Priorité<select value={formulaire.priorite} onChange={(event) => modifier('priorite', event.target.value)}>{priorites.map(([valeur, texte]) => <option key={valeur} value={valeur}>{texte}</option>)}</select></label><label>Statut<select value={formulaire.statut} onChange={(event) => modifier('statut', event.target.value)}>{statuts.filter(([valeur]) => valeur !== 'TERMINEE').map(([valeur, texte]) => <option key={valeur} value={valeur}>{texte}</option>)}</select></label><label>Date planifiée<input type="datetime-local" value={formulaire.planifiee_le} onChange={(event) => modifier('planifiee_le', event.target.value)} /></label><label className="full-field">Description<textarea rows="4" value={formulaire.description} onChange={(event) => modifier('description', event.target.value)} required /></label>{erreur && <p className="form-error full-field">{erreur}</p>}<button className="primary-button form-submit" type="submit">Enregistrer l’intervention</button></form></section>}
      {!creationOuverte && erreur && <p className="form-error">{erreur}</p>}
      <section className="panel table-panel"><div className="table-toolbar"><strong>{borne ? `Historique de la borne #${borne}` : 'Toutes les interventions'}</strong><span className="page-summary">{interventions.length} résultat(s)</span></div>{etatPage === 'chargement' && <p className="empty-state">Chargement des interventions…</p>}{etatPage === 'erreur' && <p className="empty-state error-state">Les interventions ne sont pas disponibles.</p>}{etatPage === 'pret' && <div className="table-scroll"><table><thead><tr><th>Borne</th><th>Type</th><th>Priorité</th><th>Statut</th><th>Planification</th><th>Créée par</th></tr></thead><tbody>{interventions.map((intervention) => <tr key={intervention.id}><td>{intervention.borne_identifiant}</td><td>{libelle(types, intervention.type)}</td><td>{libelle(priorites, intervention.priorite)}</td><td>{peutGerer ? <select aria-label={`Statut de l’intervention ${intervention.id}`} value={intervention.statut} onChange={(event) => changerStatut(intervention, event.target.value)}>{statuts.map(([valeur, texte]) => <option key={valeur} value={valeur}>{texte}</option>)}</select> : libelle(statuts, intervention.statut)}</td><td>{dateLisible(intervention.planifiee_le)}</td><td>{intervention.createur_nom}</td></tr>)}</tbody></table>{!interventions.length && <p className="empty-state">Aucune intervention enregistrée.</p>}</div>}</section>
    </div>
  )
}
