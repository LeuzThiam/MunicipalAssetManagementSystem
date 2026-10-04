import { useEffect, useState } from 'react'
import { api } from '../api/client'

const roles = ['LECTEUR', 'INSPECTEUR', 'GESTIONNAIRE', 'ADMIN']
const formulaireInitial = { email: '', prenom: '', nom: '', role: 'LECTEUR', mot_de_passe: '' }

export function AdministrationPage() {
  const [utilisateurs, setUtilisateurs] = useState([])
  const [formulaire, setFormulaire] = useState(formulaireInitial)
  const [erreur, setErreur] = useState('')
  const [chargement, setChargement] = useState(true)

  async function chargerUtilisateurs() {
    try {
      const donnees = await api('/utilisateurs/?page_size=100')
      setUtilisateurs(donnees.results ?? donnees)
      setErreur('')
    } catch (exception) {
      setErreur(exception.message)
    } finally {
      setChargement(false)
    }
  }

  // Le chargement initial synchronise la page avec la liste conservée par l'API.
  // oxlint-disable-next-line react/set-state-in-effect
  useEffect(() => { chargerUtilisateurs() }, [])

  async function creerUtilisateur(event) {
    event.preventDefault()
    try {
      await api('/utilisateurs/', { method: 'POST', body: JSON.stringify(formulaire) })
      setFormulaire(formulaireInitial)
      await chargerUtilisateurs()
    } catch (exception) {
      setErreur(exception.message)
    }
  }

  async function modifierUtilisateur(utilisateur, changements) {
    try {
      const resultat = await api(`/utilisateurs/${utilisateur.id}/`, {
        method: 'PATCH', body: JSON.stringify(changements),
      })
      setUtilisateurs((liste) => liste.map((element) => element.id === resultat.id ? resultat : element))
      setErreur('')
    } catch (exception) {
      setErreur(exception.message)
    }
  }

  return (
    <div className="page">
      <header className="page-header"><div><p className="eyebrow">Configuration</p><h1>Utilisateurs</h1><p>Créez les comptes et attribuez les accès selon les responsabilités municipales.</p></div></header>
      {erreur && <p className="form-error" role="alert">{erreur}</p>}
      <section className="panel admin-create-panel">
        <h2>Créer un utilisateur</h2>
        <form className="admin-user-form" onSubmit={creerUtilisateur}>
          <label>Prénom<input required value={formulaire.prenom} onChange={(e) => setFormulaire({ ...formulaire, prenom: e.target.value })} /></label>
          <label>Nom<input required value={formulaire.nom} onChange={(e) => setFormulaire({ ...formulaire, nom: e.target.value })} /></label>
          <label>Adresse courriel<input required type="email" value={formulaire.email} onChange={(e) => setFormulaire({ ...formulaire, email: e.target.value })} /></label>
          <label>Rôle<select value={formulaire.role} onChange={(e) => setFormulaire({ ...formulaire, role: e.target.value })}>{roles.map((role) => <option key={role}>{role}</option>)}</select></label>
          <label>Mot de passe temporaire<input required minLength="8" type="password" value={formulaire.mot_de_passe} onChange={(e) => setFormulaire({ ...formulaire, mot_de_passe: e.target.value })} /></label>
          <button className="primary-button" type="submit">Créer le compte</button>
        </form>
      </section>
      <section className="panel">
        <h2>Comptes existants</h2>
        {chargement ? <p>Chargement des utilisateurs…</p> : (
          <div className="table-scroll"><table><thead><tr><th>Utilisateur</th><th>Courriel</th><th>Rôle</th><th>Accès</th></tr></thead><tbody>
            {utilisateurs.map((utilisateur) => <tr key={utilisateur.id}>
              <td><strong>{utilisateur.prenom} {utilisateur.nom}</strong></td>
              <td>{utilisateur.email}</td>
              <td><select aria-label={`Rôle de ${utilisateur.email}`} value={utilisateur.role} onChange={(e) => modifierUtilisateur(utilisateur, { role: e.target.value })}>{roles.map((role) => <option key={role}>{role}</option>)}</select></td>
              <td><button className="secondary-button" type="button" onClick={() => modifierUtilisateur(utilisateur, { is_active: !utilisateur.is_active })}>{utilisateur.is_active ? 'Désactiver' : 'Réactiver'}</button></td>
            </tr>)}
          </tbody></table></div>
        )}
      </section>
    </div>
  )
}
