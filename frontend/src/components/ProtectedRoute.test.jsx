import { render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router'
import { describe, expect, it } from 'vitest'
import { AuthContextForTests } from '../test/AuthContextForTests'
import { ProtectedRoute, RoleRoute } from './ProtectedRoute'

describe('routes protégées', () => {
  it('redirige un visiteur anonyme vers la connexion', () => {
    render(
      <MemoryRouter initialEntries={['/administration']}>
        <AuthContextForTests value={{ utilisateur: null, chargement: false }}>
          <Routes>
            <Route path="/connexion" element={<p>Page de connexion</p>} />
            <Route element={<ProtectedRoute />}>
              <Route path="/administration" element={<p>Administration</p>} />
            </Route>
          </Routes>
        </AuthContextForTests>
      </MemoryRouter>,
    )

    expect(screen.getByText('Page de connexion')).toBeInTheDocument()
  })

  it('redirige un non-administrateur vers le tableau de bord', () => {
    render(
      <MemoryRouter initialEntries={['/administration']}>
        <AuthContextForTests value={{ utilisateur: { role: 'LECTEUR' }, chargement: false }}>
          <Routes>
            <Route path="/tableau-de-bord" element={<p>Tableau de bord</p>} />
            <Route element={<RoleRoute role="ADMIN" />}>
              <Route path="/administration" element={<p>Administration</p>} />
            </Route>
          </Routes>
        </AuthContextForTests>
      </MemoryRouter>,
    )

    expect(screen.getByText('Tableau de bord')).toBeInTheDocument()
  })
})
