const API_URL = import.meta.env.VITE_API_URL ?? '/api'

export const jetons = {
  lireAcces: () => sessionStorage.getItem('jeton_acces'),
  lireRafraichissement: () => sessionStorage.getItem('jeton_rafraichissement'),
  enregistrer({ access, refresh }) {
    sessionStorage.setItem('jeton_acces', access)
    sessionStorage.setItem('jeton_rafraichissement', refresh)
  },
  effacer() {
    sessionStorage.removeItem('jeton_acces')
    sessionStorage.removeItem('jeton_rafraichissement')
  },
}

export async function api(path, options = {}) {
  const headers = new Headers(options.headers)
  const acces = jetons.lireAcces()
  if (acces) headers.set('Authorization', `Bearer ${acces}`)
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const reponse = await fetch(`${API_URL}${path}`, { ...options, headers })
  if (reponse.status === 204 || reponse.status === 205) return null

  const contenu = await reponse.json().catch(() => ({}))
  if (!reponse.ok) {
    const erreur = new Error(contenu.detail ?? contenu.message ?? 'Une erreur est survenue.')
    erreur.status = reponse.status
    throw erreur
  }
  return contenu
}
