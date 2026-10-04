import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import { AuthContextForTests } from '../test/AuthContextForTests'
import { InspectionsPage } from './InspectionsPage'

vi.mock('../api/client', () => ({ api: vi.fn() }))

describe('InspectionsPage', () => {
  it('enregistre une inspection pour la borne indiquée dans l’URL', async () => {
    api
      .mockResolvedValueOnce({ results: [] })
      .mockResolvedValueOnce({
        id: 1,
        borne_identifiant: 'R01-061',
        date_inspection: '2026-10-04',
        etat: 'BON',
        pression_observee: 54,
        inspecteur_nom: 'Awa Diop',
      })
    const utilisateur = userEvent.setup()

    render(
      <MemoryRouter initialEntries={['/inspections?borne=3348&action=nouvelle']}>
        <AuthContextForTests value={{ utilisateur: { role: 'INSPECTEUR' } }}>
          <InspectionsPage />
        </AuthContextForTests>
      </MemoryRouter>,
    )

    await utilisateur.type(screen.getByLabelText('Pression observée (kPa)'), '54')
    await utilisateur.type(screen.getByLabelText('Commentaires'), 'Borne accessible.')
    await utilisateur.click(screen.getByRole('button', { name: 'Enregistrer l’inspection' }))

    await waitFor(() => expect(api).toHaveBeenCalledWith('/inspections/', expect.objectContaining({ method: 'POST' })))
    expect(await screen.findByText('R01-061')).toBeInTheDocument()
  })
})
