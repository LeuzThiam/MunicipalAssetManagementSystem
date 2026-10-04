import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router'
import { useAuth } from '../context/auth'

export function LoginPage() {
  const { utilisateur, connexion } = useAuth()
  const [email, setEmail] = useState('')
  const [motDePasse, setMotDePasse] = useState('')
  const [erreur, setErreur] = useState('')
  const [envoi, setEnvoi] = useState(false)
  const navigation = useNavigate()
  const emplacement = useLocation()

  if (utilisateur) return <Navigate to="/tableau-de-bord" replace />

  async function soumettre(event) {
    event.preventDefault()
    setErreur('')
    setEnvoi(true)
    try {
      await connexion(email, motDePasse)
      navigation(emplacement.state?.from?.pathname ?? '/tableau-de-bord', { replace: true })
    } catch {
      setErreur('Courriel ou mot de passe incorrect.')
    } finally {
      setEnvoi(false)
    }
  }

  return (
    <main className="login-page">
      <section className="login-intro">
        <div className="brand brand-light"><span className="brand-mark">MA</span><strong>Actifs municipaux</strong></div>
        <div>
          <p className="eyebrow">Gestion territoriale</p>
          <h1>Les infrastructures de la ville, réunies au même endroit.</h1>
          <p>Localisez les actifs, préparez les inspections et prenez des décisions à partir de données fiables.</p>
        </div>
        <small>Plateforme interne · Accès sécurisé</small>
      </section>
      <section className="login-panel">
        <form className="login-form" onSubmit={soumettre}>
          <p className="eyebrow">Bienvenue</p>
          <h2>Connexion</h2>
          <p className="muted">Utilisez votre compte municipal pour continuer.</p>
          <label>Adresse courriel<input type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" required /></label>
          <label>Mot de passe<input type="password" value={motDePasse} onChange={(event) => setMotDePasse(event.target.value)} autoComplete="current-password" required /></label>
          {erreur && <p className="form-error" role="alert">{erreur}</p>}
          <button className="primary-button" type="submit" disabled={envoi}>{envoi ? 'Connexion…' : 'Se connecter'}</button>
        </form>
      </section>
    </main>
  )
}
