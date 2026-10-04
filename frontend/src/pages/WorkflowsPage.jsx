const contenu = {
  inspections: ['Inspections', 'Suivez les contrôles terrain des bornes.', 'IN', 'phase 19'],
  interventions: ['Interventions', 'Planifiez et suivez les travaux municipaux.', 'IT', 'phase 20'],
}

export function WorkflowsPage({ type }) {
  const [titre, description, icone, phase] = contenu[type]
  return <div className="page"><header className="page-header"><div><p className="eyebrow">Opérations</p><h1>{titre}</h1><p>{description}</p></div></header><section className="panel coming-soon"><span className="coming-icon">{icone}</span><h2>Module prêt à être connecté</h2><p>La navigation et l’espace de travail sont en place. Les règles métier seront développées à la {phase}.</p></section></div>
}
