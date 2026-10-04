const API_URL = import.meta.env.VITE_API_URL ?? '/api'

export const jetons = {
  lireAcces: () => sessionStorage.getItem('jeton_acces'),
  lireRafraichissement: () => sessionStorage.getItem('jeton_rafraichissement'),
  enregistrer({ access, refresh }) {
    sessionStorage.setItem('jeton_acces', access)
    if (refresh) sessionStorage.setItem('jeton_rafraichissement', refresh)
  },
  effacer() {
    sessionStorage.removeItem('jeton_acces')
    sessionStorage.removeItem('jeton_rafraichissement')
  },
}

async function executerRequete(path, options, nouvelleTentative) {
  const headers = new Headers(options.headers)
  const acces = jetons.lireAcces()
  if (acces) headers.set('Authorization', `Bearer ${acces}`)
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  let reponse = await fetch(`${API_URL}${path}`, { ...options, headers })

  if (reponse.status === 401 && !nouvelleTentative && path !== '/connexion/rafraichir/') {
    const refresh = jetons.lireRafraichissement()
    if (refresh) {
      const rafraichissement = await fetch(`${API_URL}/connexion/rafraichir/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh }),
      })
      if (rafraichissement.ok) {
        jetons.enregistrer(await rafraichissement.json())
        return executerRequete(path, options, true)
      }
    }
    jetons.effacer()
  }

  if (reponse.status === 204 || reponse.status === 205) return null

  const contenu = await reponse.json().catch(() => ({}))
  if (!reponse.ok) {
    const erreur = new Error(contenu.detail ?? contenu.message ?? 'Une erreur est survenue.')
    erreur.status = reponse.status
    throw erreur
  }
  return contenu
}

export function api(path, options = {}) {
  return executerRequete(path, options, false)
}
