import { useEffect, useMemo, useState } from 'react'
import { api } from '../api/client'

function extraireObjets(donnees) {
  const elements = donnees.results?.features ?? donnees.features ?? donnees.results ?? []
  return elements.map((element) => ({ id: element.id ?? element.properties?.id, ...(element.properties ?? element) }))
}

function afficherValeur(valeur) {
  if (valeur === null || valeur === undefined || valeur === '') return 'Non renseigné'
  if (typeof valeur === 'boolean') return valeur ? 'Oui' : 'Non'
  return valeur
}

export function ResourcePage({ titre, description, endpoint, recherche, colonnes }) {
  const [donnees, setDonnees] = useState([])
  const [total, setTotal] = useState(0)
  const [filtre, setFiltre] = useState('')
  const [etat, setEtat] = useState('chargement')

  useEffect(() => {
    api(endpoint).then((reponse) => {
      const objets = extraireObjets(reponse)
      setDonnees(objets)
      setTotal(reponse.count ?? objets.length)
      setEtat('pret')
    }).catch(() => setEtat('erreur'))
  }, [endpoint])

  const lignes = useMemo(() => {
    const terme = filtre.trim().toLocaleLowerCase('fr-CA')
    if (!terme) return donnees
    return donnees.filter((objet) => colonnes.some(([cle]) => String(objet[cle] ?? '').toLocaleLowerCase('fr-CA').includes(terme)))
  }, [colonnes, donnees, filtre])

  return (
    <div className="page">
      <header className="page-header resource-header"><div><p className="eyebrow">Inventaire</p><h1>{titre}</h1><p>{description}</p></div><span className="count-chip">{total.toLocaleString('fr-CA')} éléments</span></header>
      <section className="panel table-panel">
        <div className="table-toolbar"><label className="search-field"><span aria-hidden="true">⌕</span><input type="search" placeholder={recherche} value={filtre} onChange={(event) => setFiltre(event.target.value)} /></label><button className="secondary-button" type="button">Filtres</button></div>
        {etat === 'chargement' && <p className="empty-state">Chargement des données…</p>}
        {etat === 'erreur' && <p className="empty-state error-state">Les données ne sont pas disponibles pour le moment.</p>}
        {etat === 'pret' && <div className="table-scroll"><table><thead><tr>{colonnes.map(([, libelle]) => <th key={libelle}>{libelle}</th>)}</tr></thead><tbody>{lignes.map((ligne, index) => <tr key={ligne.id ?? index}>{colonnes.map(([cle]) => <td key={cle}>{afficherValeur(ligne[cle])}</td>)}</tr>)}</tbody></table>{!lignes.length && <p className="empty-state">Aucun résultat.</p>}</div>}
      </section>
    </div>
  )
}
