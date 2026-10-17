import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api, jetons } from './client'

function reponseJson(statut, contenu) {
  return {
    status: statut,
    ok: statut >= 200 && statut < 300,
    json: vi.fn().mockResolvedValue(contenu),
  }
}

describe('client API', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    sessionStorage.clear()
  })

  it('présente le détail utile d’une erreur de validation', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(reponseJson(400, {
      code: 'ValidationError',
      message: 'Erreur de validation.',
      erreurs: { date_inspection: ['Une inspection ne peut pas avoir une date future.'] },
    })))

    await expect(api('/inspections/', { method: 'POST' })).rejects.toMatchObject({
      message: 'Une inspection ne peut pas avoir une date future.',
      status: 400,
      code: 'ValidationError',
    })
  })

  it('explique clairement une panne réseau', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))

    await expect(api('/bornes/')).rejects.toMatchObject({
      message: 'Le service est indisponible. Vérifiez votre connexion et réessayez.',
      status: 0,
    })
  })

  it('utilise un message sûr pour une réponse 500 non JSON', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      status: 500,
      ok: false,
      json: vi.fn().mockRejectedValue(new SyntaxError('HTML reçu')),
    }))

    await expect(api('/tableau-de-bord/')).rejects.toThrow(
      'Une erreur interne est survenue. Réessayez plus tard.',
    )
  })

  it('rafraîchit le jeton puis rejoue la requête une seule fois', async () => {
    jetons.enregistrer({ access: 'expire', refresh: 'valide' })
    const fetchSimule = vi.fn()
      .mockResolvedValueOnce(reponseJson(401, { code: 'NotAuthenticated' }))
      .mockResolvedValueOnce(reponseJson(200, { access: 'nouveau' }))
      .mockResolvedValueOnce(reponseJson(200, { results: [] }))
    vi.stubGlobal('fetch', fetchSimule)

    await expect(api('/bornes/')).resolves.toEqual({ results: [] })
    expect(fetchSimule).toHaveBeenCalledTimes(3)
    expect(jetons.lireAcces()).toBe('nouveau')
  })
})
