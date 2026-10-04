import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import { AuthContextForTests } from '../test/AuthContextForTests'
import { DashboardPage } from './DashboardPage'

vi.mock('../api/client', () => ({ api: vi.fn() }))

describe('DashboardPage', () => {
  beforeEach(() => vi.clearAllMocks())

  it('affiche les indicateurs et les répartitions métier', async () => {
    api.mockResolvedValue({ bornes_total: 3369, batiments_total: 27412, segments_rue_total: 789, bornes_sans_entretien: 1061, pression_moyenne: 54.2, interventions_ouvertes: 8, inspections_ce_mois: 12, interventions_par_statut: [{ statut: 'OUVERTE', total: 8 }], inspections_par_etat: [{ etat: 'BON', total: 12 }] })

    render(<MemoryRouter><AuthContextForTests value={{ utilisateur: { prenom: 'Modou' } }}><DashboardPage /></AuthContextForTests></MemoryRouter>)

    expect(await screen.findAllByText('3 369')).not.toHaveLength(0)
    expect(screen.getByText('Interventions ouvertes')).toBeInTheDocument()
    expect(screen.getByText('Ouvertes')).toBeInTheDocument()
    expect(screen.getByText('Bon état')).toBeInTheDocument()
    expect(api).toHaveBeenCalledWith('/tableau-de-bord/')
  })
})
