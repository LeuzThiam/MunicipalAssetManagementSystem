import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router'
import { describe, expect, it, vi } from 'vitest'
import { AuthContextForTests } from '../test/AuthContextForTests'
import { LoginPage } from './LoginPage'

describe('LoginPage', () => {
  it('envoie les identifiants saisis', async () => {
    const connexion = vi.fn().mockResolvedValue(undefined)
    const utilisateur = userEvent.setup()
    render(<MemoryRouter><AuthContextForTests value={{ utilisateur: null, connexion }}><LoginPage /></AuthContextForTests></MemoryRouter>)
    await utilisateur.type(screen.getByLabelText('Adresse courriel'), 'agent@ville.ca')
    await utilisateur.type(screen.getByLabelText('Mot de passe'), 'secret-solide')
    await utilisateur.click(screen.getByRole('button', { name: 'Se connecter' }))
    expect(connexion).toHaveBeenCalledWith('agent@ville.ca', 'secret-solide')
  })
})
