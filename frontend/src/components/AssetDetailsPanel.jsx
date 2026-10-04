import { Link } from 'react-router'

function afficherDate(valeur) {
  if (!valeur) return 'Non renseigné'
  const date = new Date(`${valeur}T00:00:00`)
  return Number.isNaN(date.getTime()) ? valeur : date.toLocaleDateString('fr-CA')
}

export function AssetDetailsPanel({ selection, onClose }) {
  if (!selection) return null

  const { couche, feature } = selection
  const proprietes = feature.properties ?? {}
  const estBorne = couche.cle === 'bornes'
  const id = feature.id ?? proprietes.id
  const identifiant = estBorne
    ? proprietes.identifiant_source ?? couche.nom
    : proprietes.nom ?? proprietes.identifiant_source ?? couche.nom

  return (
    <aside className="asset-details" aria-label={`Détails de ${identifiant}`}>
      <div className="asset-details-heading">
        <div><p className="eyebrow">{couche.nom}</p><h2>{identifiant}</h2></div>
        <button type="button" className="close-button" onClick={onClose} aria-label="Fermer les détails">×</button>
      </div>

      {estBorne ? (
        <>
          <dl className="asset-facts">
            <div><dt>Municipalité</dt><dd>{proprietes.municipalite || 'Non renseignée'}</dd></div>
            <div><dt>Pression dynamique</dt><dd>{proprietes.pression_dynamique != null ? `${proprietes.pression_dynamique} kPa` : 'Non renseignée'}</dd></div>
            <div><dt>Dernier entretien</dt><dd>{afficherDate(proprietes.date_entretien)}</dd></div>
          </dl>
          <div className="asset-actions">
            <Link className="primary-link" to={`/inspections?borne=${id}`}>Voir les inspections</Link>
            <Link className="secondary-link" to={`/inspections?borne=${id}&action=nouvelle`}>Créer une inspection</Link>
            <Link className="secondary-link" to={`/interventions?borne=${id}`}>Voir les interventions</Link>
            <Link className="secondary-link" to={`/interventions?borne=${id}&action=nouvelle`}>Créer une intervention</Link>
          </div>
        </>
      ) : (
        <dl className="asset-facts">
          {proprietes.adresse && <div><dt>Adresse</dt><dd>{proprietes.adresse}</dd></div>}
          {proprietes.usage && <div><dt>Usage</dt><dd>{proprietes.usage}</dd></div>}
          {proprietes.type_rue && <div><dt>Type de rue</dt><dd>{proprietes.type_rue}</dd></div>}
          {proprietes.limite_vitesse != null && <div><dt>Vitesse</dt><dd>{proprietes.limite_vitesse} km/h</dd></div>}
        </dl>
      )}
    </aside>
  )
}
