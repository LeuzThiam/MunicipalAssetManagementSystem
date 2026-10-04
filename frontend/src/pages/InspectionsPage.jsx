import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router'
import { api } from '../api/client'
import { useAuth } from '../context/auth'

const etats = [
  ['BON', 'Bon état'],
  ['A_SURVEILLER', 'À surveiller'],
  ['REPARATION_REQUISE', 'Réparation requise'],
  ['HORS_SERVICE', 'Hors service'],
]
const aujourdHui = new Date().toISOString().slice(0, 10)

export function InspectionsPage() {
  const { utilisateur } = useAuth()
  const [parametres, setParametres] = useSearchParams()
  const borne = parametres.get('borne') ?? ''
  const [inspections, setInspections] = useState([])
  const [etatPage, setEtatPage] = useState('chargement')
  const [erreur, setErreur] = useState('')
  const [formulaire, setFormulaire] = useState({
    date_inspection: aujourdHui,
    etat: 'BON',
    pression_observee: '',
    commentaire: '',
  })
  const peutCreer = ['ADMIN', 'GESTIONNAIRE', 'INSPECTEUR'].includes(utilisateur?.role)
  const creationOuverte = parametres.get('action') === 'nouvelle' && borne && peutCreer

  useEffect(() => {
    const suffixe = borne ? `?borne=${borne}` : ''
    api(`/inspections/${suffixe}`)
      .then((reponse) => {
        setInspections(reponse.results ?? [])
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
      const inspection = await api('/inspections/', {
        method: 'POST',
        body: JSON.stringify({
          ...formulaire,
          borne: Number(borne),
          pression_observee: formulaire.pression_observee === '' ? null : Number(formulaire.pression_observee),
        }),
      })
      setInspections((courantes) => [inspection, ...courantes])
      setParametres(borne ? { borne } : {})
    } catch (cause) {
      setErreur(cause.message)
    }
  }

  return (
    <div className="page">
      <header className="page-header"><div><p className="eyebrow">Opérations terrain</p><h1>Inspections</h1><p>Consignez l’état des bornes et conservez leur historique de contrôle.</p></div>{borne && peutCreer && <button className="secondary-button" type="button" onClick={() => setParametres({ borne, action: 'nouvelle' })}>Nouvelle inspection</button>}</header>
      {creationOuverte && <section className="panel inspection-form-panel"><div className="panel-heading"><div><p className="eyebrow">Borne #{borne}</p><h2>Nouvelle inspection</h2></div><button className="close-button" type="button" aria-label="Fermer le formulaire" onClick={() => setParametres({ borne })}>×</button></div><form className="inspection-form" onSubmit={enregistrer}><label>Date<input type="date" max={aujourdHui} value={formulaire.date_inspection} onChange={(event) => modifier('date_inspection', event.target.value)} required /></label><label>État<select value={formulaire.etat} onChange={(event) => modifier('etat', event.target.value)}>{etats.map(([valeur, libelle]) => <option key={valeur} value={valeur}>{libelle}</option>)}</select></label><label>Pression observée (kPa)<input type="number" min="0" value={formulaire.pression_observee} onChange={(event) => modifier('pression_observee', event.target.value)} /></label><label className="full-field">Commentaires<textarea rows="4" value={formulaire.commentaire} onChange={(event) => modifier('commentaire', event.target.value)} /></label>{erreur && <p className="form-error full-field">{erreur}</p>}<button className="primary-button form-submit" type="submit">Enregistrer l’inspection</button></form></section>}
      <section className="panel table-panel"><div className="table-toolbar"><strong>{borne ? `Historique de la borne #${borne}` : 'Toutes les inspections'}</strong><span className="page-summary">{inspections.length} résultat(s)</span></div>{etatPage === 'chargement' && <p className="empty-state">Chargement des inspections…</p>}{etatPage === 'erreur' && <p className="empty-state error-state">Les inspections ne sont pas disponibles.</p>}{etatPage === 'pret' && <div className="table-scroll"><table><thead><tr><th>Borne</th><th>Date</th><th>État</th><th>Pression</th><th>Inspecteur</th></tr></thead><tbody>{inspections.map((inspection) => <tr key={inspection.id}><td>{inspection.borne_identifiant}</td><td>{inspection.date_inspection}</td><td>{etats.find(([valeur]) => valeur === inspection.etat)?.[1] ?? inspection.etat}</td><td>{inspection.pression_observee ?? 'Non renseignée'}</td><td>{inspection.inspecteur_nom}</td></tr>)}</tbody></table>{!inspections.length && <p className="empty-state">Aucune inspection enregistrée.</p>}</div>}</section>
    </div>
  )
}
