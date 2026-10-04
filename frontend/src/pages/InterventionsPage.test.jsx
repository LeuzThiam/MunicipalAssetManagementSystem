import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import { AuthContextForTests } from '../test/AuthContextForTests'
import { InterventionsPage } from './InterventionsPage'

vi.mock('../api/client', () => ({ api: vi.fn() }))

describe('InterventionsPage', () => {
  it('enregistre une intervention pour la borne indiquée dans l’URL', async () => {
    api.mockResolvedValueOnce({ results: [] }).mockResolvedValueOnce({ id: 7, borne_identifiant: 'R01-061', type: 'REPARATION', priorite: 'HAUTE', statut: 'PLANIFIEE', planifiee_le: null, createur_nom: 'Moussa Ndiaye' })
    const utilisateur = userEvent.setup()

    render(<MemoryRouter initialEntries={['/interventions?borne=3348&action=nouvelle']}><AuthContextForTests value={{ utilisateur: { role: 'GESTIONNAIRE' } }}><InterventionsPage /></AuthContextForTests></MemoryRouter>)

    await utilisateur.selectOptions(screen.getByLabelText('Type'), 'REPARATION')
    await utilisateur.selectOptions(screen.getByLabelText('Priorité'), 'HAUTE')
    await utilisateur.selectOptions(screen.getByLabelText('Statut'), 'PLANIFIEE')
    await utilisateur.type(screen.getByLabelText('Description'), 'Remplacer la vanne principale.')
    await utilisateur.click(screen.getByRole('button', { name: 'Enregistrer l’intervention' }))

    await waitFor(() => expect(api).toHaveBeenCalledWith('/interventions/', expect.objectContaining({ method: 'POST' })))
    expect(await screen.findByText('R01-061')).toBeInTheDocument()
  })
})
