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

const messagesParStatut = {
  400: 'La requête est invalide.',
  401: 'Votre session a expiré. Veuillez vous reconnecter.',
  403: 'Vous n’avez pas l’autorisation d’effectuer cette action.',
  404: 'La ressource demandée est introuvable.',
  500: 'Une erreur interne est survenue. Réessayez plus tard.',
}

function premierMessage(erreurs) {
  if (typeof erreurs === 'string') return erreurs
  if (Array.isArray(erreurs)) {
    for (const erreur of erreurs) {
      const message = premierMessage(erreur)
      if (message) return message
    }
  }
  if (erreurs && typeof erreurs === 'object') {
    for (const erreur of Object.values(erreurs)) {
      const message = premierMessage(erreur)
      if (message) return message
    }
  }
  return ''
}

function creerErreur(reponse, contenu) {
  const message = (premierMessage(contenu.erreurs) || contenu.message)
    ?? contenu.detail
    ?? messagesParStatut[reponse.status]
    ?? 'Une erreur est survenue.'
  const erreur = new Error(message)
  erreur.status = reponse.status
  erreur.code = contenu.code
  erreur.erreurs = contenu.erreurs
  return erreur
}

async function appelerService(url, options) {
  try {
    return await fetch(url, options)
  } catch (cause) {
    const erreur = new Error('Le service est indisponible. Vérifiez votre connexion et réessayez.')
    erreur.status = 0
    erreur.cause = cause
    throw erreur
  }
}

async function executerRequete(path, options, nouvelleTentative) {
  const headers = new Headers(options.headers)
  const acces = jetons.lireAcces()
  if (acces) headers.set('Authorization', `Bearer ${acces}`)
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const reponse = await appelerService(`${API_URL}${path}`, { ...options, headers })

  if (reponse.status === 401 && !nouvelleTentative && path !== '/connexion/rafraichir/') {
    const refresh = jetons.lireRafraichissement()
    if (refresh) {
      const rafraichissement = await appelerService(`${API_URL}/connexion/rafraichir/`, {
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
    throw creerErreur(reponse, contenu)
  }
  return contenu
}

export function api(path, options = {}) {
  return executerRequete(path, options, false)
}
