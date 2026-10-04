import { useEffect, useState } from 'react'
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
  const [page, setPage] = useState(1)
  const [pages, setPages] = useState({ suivante: false, precedente: false })
  const [etat, setEtat] = useState('chargement')

  useEffect(() => {
    const parametres = new URLSearchParams({ page })
    if (filtre.trim()) parametres.set('search', filtre.trim())
    const attente = setTimeout(() => {
      api(`${endpoint}?${parametres}`).then((reponse) => {
        const objets = extraireObjets(reponse)
        setDonnees(objets)
        setTotal(reponse.count ?? objets.length)
        setPages({ suivante: Boolean(reponse.next), precedente: Boolean(reponse.previous) })
        setEtat('pret')
      }).catch(() => setEtat('erreur'))
    }, 250)
    return () => clearTimeout(attente)
  }, [endpoint, filtre, page])

  function rechercher(event) {
    setEtat('chargement')
    setFiltre(event.target.value)
    setPage(1)
  }

  function changerPage(numero) {
    setEtat('chargement')
    setPage(numero)
  }

  return (
    <div className="page">
      <header className="page-header resource-header"><div><p className="eyebrow">Inventaire</p><h1>{titre}</h1><p>{description}</p></div><span className="count-chip">{total.toLocaleString('fr-CA')} éléments</span></header>
      <section className="panel table-panel">
        <div className="table-toolbar"><label className="search-field"><span aria-hidden="true">⌕</span><input type="search" placeholder={recherche} value={filtre} onChange={rechercher} /></label><span className="page-summary">Page {page}</span></div>
        {etat === 'chargement' && <p className="empty-state">Chargement des données…</p>}
        {etat === 'erreur' && <p className="empty-state error-state">Les données ne sont pas disponibles pour le moment.</p>}
        {etat === 'pret' && <><div className="table-scroll"><table><thead><tr>{colonnes.map(([, libelle]) => <th key={libelle}>{libelle}</th>)}</tr></thead><tbody>{donnees.map((ligne, index) => <tr key={ligne.id ?? index}>{colonnes.map(([cle]) => <td key={cle}>{afficherValeur(ligne[cle])}</td>)}</tr>)}</tbody></table>{!donnees.length && <p className="empty-state">Aucun résultat.</p>}</div><nav className="pagination" aria-label="Pagination"><button type="button" disabled={!pages.precedente} onClick={() => changerPage(page - 1)}>Précédent</button><span>Page {page}</span><button type="button" disabled={!pages.suivante} onClick={() => changerPage(page + 1)}>Suivant</button></nav></>}
      </section>
    </div>
  )
}
