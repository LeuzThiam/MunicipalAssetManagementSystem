import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import { ResourcePage } from './ResourcePage'

vi.mock('../api/client', () => ({ api: vi.fn() }))

const proprietes = {
  titre: 'Bornes d’incendie',
  description: 'Inventaire des bornes.',
  endpoint: '/bornes/',
  recherche: 'Rechercher par identifiant…',
  colonnes: [['identifiant_source', 'Identifiant']],
}

describe('ResourcePage', () => {
  beforeEach(() => vi.clearAllMocks())

  it('envoie le filtre saisi à l’API', async () => {
    api.mockResolvedValue({ count: 1, next: null, previous: null, results: [{ id: 1, identifiant_source: 'R01-061' }] })
    render(<ResourcePage {...proprietes} />)

    fireEvent.change(screen.getByPlaceholderText('Rechercher par identifiant…'), { target: { value: 'R01-061' } })

    await waitFor(() => expect(api).toHaveBeenLastCalledWith('/bornes/?page=1&search=R01-061'), { timeout: 1000 })
    expect(await screen.findByText('R01-061')).toBeInTheDocument()
  })

  it('permet de charger la page suivante', async () => {
    api
      .mockResolvedValueOnce({ count: 2, next: 'page-2', previous: null, results: [{ id: 1, identifiant_source: 'R01-061' }] })
      .mockResolvedValueOnce({ count: 2, next: null, previous: 'page-1', results: [{ id: 2, identifiant_source: 'R01-062' }] })
    const utilisateur = userEvent.setup()
    render(<ResourcePage {...proprietes} />)

    await utilisateur.click(await screen.findByRole('button', { name: 'Suivant' }))

    expect(await screen.findByText('R01-062')).toBeInTheDocument()
    expect(api).toHaveBeenLastCalledWith('/bornes/?page=2')
  })

  it('affiche un état clair lorsque l’API est indisponible', async () => {
    api.mockRejectedValue(new Error('API indisponible'))
    render(<ResourcePage {...proprietes} />)

    expect(await screen.findByText('Les données ne sont pas disponibles pour le moment.')).toBeInTheDocument()
  })
})
