import L from 'leaflet'
import { useEffect, useMemo, useState } from 'react'
import { GeoJSON, LayersControl, MapContainer, ScaleControl, TileLayer, useMap } from 'react-leaflet'
import { AssetDetailsPanel } from '../components/AssetDetailsPanel'
import { chargerCouche } from './mapData'

const couches = [
  { cle: 'bornes', nom: 'Bornes d’incendie', endpoint: '/bornes/', couleur: '#d45d35' },
  { cle: 'batiments', nom: 'Bâtiments', endpoint: '/batiments/', couleur: '#24745a' },
  { cle: 'rues', nom: 'Réseau routier', endpoint: '/segments-rue/', couleur: '#3d5a80' },
]

function contenuInfo(feature, nomCouche) {
  const proprietes = feature.properties ?? {}
  const titre = proprietes.nom ?? proprietes.identifiant_source ?? nomCouche
  const details = [proprietes.adresse, proprietes.municipalite, proprietes.usage].filter(Boolean)
  const conteneur = document.createElement('div')
  const nom = document.createElement('strong')
  const description = document.createElement('p')
  nom.textContent = String(titre)
  description.textContent = details.join(' · ') || 'Information municipale'
  conteneur.className = 'map-popup'
  conteneur.append(nom, description)
  return conteneur
}

function AjusterVue({ donnees }) {
  const carte = useMap()
  useEffect(() => {
    const features = Object.values(donnees).flatMap((collection) => collection.features)
    if (!features.length) return
    const limites = L.geoJSON({ type: 'FeatureCollection', features }).getBounds()
    if (limites.isValid()) carte.fitBounds(limites, { padding: [24, 24], maxZoom: 15 })
  }, [carte, donnees])
  return null
}

function RafraichirTaille({ selection }) {
  const carte = useMap()
  useEffect(() => {
    carte.invalidateSize()
    const minuterie = window.setTimeout(() => carte.invalidateSize(), 200)
    return () => window.clearTimeout(minuterie)
  }, [carte, selection])
  return null
}

export function MapPage() {
  const [donnees, setDonnees] = useState({})
  const [etat, setEtat] = useState('chargement')
  const [selection, setSelection] = useState(null)

  useEffect(() => {
    Promise.all(couches.map(async (couche) => [couche.cle, await chargerCouche(couche.endpoint)]))
      .then((resultats) => {
        setDonnees(Object.fromEntries(resultats))
        setEtat('pret')
      })
      .catch(() => setEtat('erreur'))
  }, [])

  const total = useMemo(
    () => Object.values(donnees).reduce((somme, collection) => somme + collection.features.length, 0),
    [donnees],
  )

  return (
    <div className="page map-page">
      <header className="page-header"><div><p className="eyebrow">Analyse spatiale</p><h1>Carte municipale</h1><p>Explorez les actifs, activez les couches et sélectionnez un élément pour afficher ses informations.</p></div><span className="count-chip">{total.toLocaleString('fr-CA')} objets</span></header>
      <section className={`panel map-workspace${selection ? ' has-selection' : ''}`}>
        <div className="map-panel">
          {etat === 'chargement' && <div className="map-status">Chargement des données cartographiques…</div>}
          {etat === 'erreur' && <div className="map-status error-state">La carte ne peut pas charger les données pour le moment.</div>}
          <MapContainer center={[45.5, -73.56]} zoom={11} className="municipal-map" scrollWheelZoom>
            <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
            <LayersControl position="topright">
              {couches.map((couche) => donnees[couche.cle] && (
                <LayersControl.Overlay checked key={couche.cle} name={`${couche.nom} (${donnees[couche.cle].features.length})`}>
                  <GeoJSON
                    key={`${couche.cle}-${donnees[couche.cle].features.length}`}
                    data={donnees[couche.cle]}
                    style={{ color: couche.couleur, fillColor: couche.couleur, fillOpacity: 0.35, weight: 3 }}
                    pointToLayer={(_, latlng) => L.circleMarker(latlng, { radius: 6, color: '#fff', weight: 2, fillColor: couche.couleur, fillOpacity: 0.95 })}
                    onEachFeature={(feature, layer) => {
                      layer.bindPopup(contenuInfo(feature, couche.nom))
                      layer.on('click', () => setSelection({ couche, feature }))
                    }}
                  />
                </LayersControl.Overlay>
              ))}
            </LayersControl>
            <ScaleControl imperial={false} />
            <RafraichirTaille selection={selection} />
            {etat === 'pret' && <AjusterVue donnees={donnees} />}
          </MapContainer>
        </div>
        <AssetDetailsPanel selection={selection} onClose={() => setSelection(null)} />
      </section>
    </div>
  )
}
