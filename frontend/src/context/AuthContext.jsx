import { useEffect, useMemo, useState } from 'react'
import { api, jetons } from '../api/client'
import { AuthContext } from './auth'

export function AuthProvider({ children }) {
  const [utilisateur, setUtilisateur] = useState(null)
  const [chargement, setChargement] = useState(Boolean(jetons.lireAcces()))

  useEffect(() => {
    if (!jetons.lireAcces()) return
    api('/utilisateur-courant/')
      .then(setUtilisateur)
      .catch(jetons.effacer)
      .finally(() => setChargement(false))
  }, [])

  async function connexion(email, password) {
    const nouveauxJetons = await api('/connexion/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    jetons.enregistrer(nouveauxJetons)
    setUtilisateur(await api('/utilisateur-courant/'))
  }

  async function deconnexion() {
    const refresh = jetons.lireRafraichissement()
    try {
      if (refresh) {
        await api('/deconnexion/', {
          method: 'POST',
          body: JSON.stringify({ refresh }),
        })
      }
    } finally {
      jetons.effacer()
      setUtilisateur(null)
    }
  }

  const valeur = useMemo(
    () => ({ utilisateur, chargement, connexion, deconnexion }),
    [utilisateur, chargement],
  )

  return <AuthContext.Provider value={valeur}>{children}</AuthContext.Provider>
}
