import { api } from '../api/client'

export async function chargerCouche(endpoint) {
  const features = []
  let page = 1
  let suivante = true

  while (suivante && page <= 100) {
    const reponse = await api(`${endpoint}?page=${page}`)
    features.push(...(reponse.results?.features ?? reponse.features ?? []))
    suivante = Boolean(reponse.next)
    page += 1
  }

  return { type: 'FeatureCollection', features }
}
