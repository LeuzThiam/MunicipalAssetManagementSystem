import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { AssetDetailsPanel } from './AssetDetailsPanel'

describe('AssetDetailsPanel', () => {
  it('présente les données métier et les actions d’une borne sélectionnée', () => {
    const selection = {
      couche: { cle: 'bornes', nom: 'Bornes d’incendie' },
      feature: {
        id: 'borne-42',
        properties: {
          identifiant_source: 'R01-061',
          municipalite: 'Montréal',
          pression_dynamique: 54,
          date_entretien: '2025-11-07',
        },
      },
    }

    render(<AssetDetailsPanel selection={selection} onClose={vi.fn()} />)

    expect(screen.getByRole('heading', { name: 'R01-061' })).toBeInTheDocument()
    expect(screen.getByText('54 kPa')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Inspections — phase 19' })).toBeDisabled()
  })

  it('utilise le nom lisible pour un segment de rue', () => {
    const selection = {
      couche: { cle: 'rues', nom: 'Réseau routier' },
      feature: {
        properties: {
          identifiant_source: 'SEG-1024',
          nom: 'Rue Exemple',
          type_rue: 'Locale',
        },
      },
    }

    render(<AssetDetailsPanel selection={selection} onClose={vi.fn()} />)

    expect(screen.getByRole('heading', { name: 'Rue Exemple' })).toBeInTheDocument()
  })
})
