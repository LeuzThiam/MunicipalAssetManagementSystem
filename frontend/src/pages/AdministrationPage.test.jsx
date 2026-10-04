import { render, screen, waitFor, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import { AdministrationPage } from './AdministrationPage'

vi.mock('../api/client', () => ({ api: vi.fn() }))

describe('AdministrationPage', () => {
  beforeEach(() => {
    api.mockReset()
    api.mockResolvedValueOnce({ results: [{ id: 1, prenom: 'Lina', nom: 'Roy', email: 'lina@ville.ca', role: 'LECTEUR', is_active: true }] })
  })

  it('affiche les comptes existants', async () => {
    render(<AdministrationPage />)
    expect(await screen.findByText('Lina Roy')).toBeInTheDocument()
    expect(screen.getByText('lina@ville.ca')).toBeInTheDocument()
  })

  it('crée un compte avec le rôle choisi', async () => {
    api.mockResolvedValueOnce({ id: 2 }).mockResolvedValueOnce({ results: [] })
    const utilisateur = userEvent.setup()
    const vue = render(<AdministrationPage />)
    const page = within(vue.container)
    await page.findByText('Lina Roy')
    await utilisateur.type(page.getByLabelText('Prénom'), 'Samir')
    await utilisateur.type(page.getByLabelText('Nom'), 'Diallo')
    await utilisateur.type(page.getByLabelText('Adresse courriel'), 'samir@ville.ca')
    await utilisateur.selectOptions(page.getByLabelText('Rôle'), 'INSPECTEUR')
    await utilisateur.type(page.getByLabelText('Mot de passe temporaire'), 'mot-de-passe-solide')
    await utilisateur.click(page.getByRole('button', { name: 'Créer le compte' }))
    await waitFor(() => expect(api).toHaveBeenCalledWith('/utilisateurs/', expect.objectContaining({ method: 'POST' })))
    expect(JSON.parse(api.mock.calls[1][1].body).role).toBe('INSPECTEUR')
  })
})
