import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import { chargerCouche } from './mapData'

vi.mock('../api/client', () => ({ api: vi.fn() }))

describe('chargement des couches cartographiques', () => {
  beforeEach(() => vi.clearAllMocks())

  it('regroupe toutes les pages GeoJSON retournées par l’API', async () => {
    api
      .mockResolvedValueOnce({
        next: 'http://api.test/bornes/?page=2',
        results: { features: [{ type: 'Feature', id: 1 }] },
      })
      .mockResolvedValueOnce({
        next: null,
        results: { features: [{ type: 'Feature', id: 2 }] },
      })

    await expect(chargerCouche('/bornes/')).resolves.toEqual({
      type: 'FeatureCollection',
      features: [
        { type: 'Feature', id: 1 },
        { type: 'Feature', id: 2 },
      ],
    })
    expect(api).toHaveBeenNthCalledWith(1, '/bornes/?page=1')
    expect(api).toHaveBeenNthCalledWith(2, '/bornes/?page=2')
  })
})
