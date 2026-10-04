export const ressources = {
  bornes: {
    titre: 'Bornes d’incendie',
    description: 'Consultez les bornes, leur entretien et leur pression dynamique.',
    endpoint: '/bornes/',
    recherche: 'Rechercher par identifiant…',
    colonnes: [['identifiant_source', 'Identifiant'], ['municipalite', 'Municipalité'], ['date_entretien', 'Dernier entretien'], ['pression_dynamique', 'Pression']],
  },
  batiments: {
    titre: 'Bâtiments',
    description: 'Explorez les bâtiments municipaux et leurs caractéristiques.',
    endpoint: '/batiments/',
    recherche: 'Rechercher une adresse…',
    colonnes: [['nom', 'Nom'], ['usage', 'Usage'], ['adresse', 'Adresse'], ['superficie', 'Superficie']],
  },
  rues: {
    titre: 'Réseau routier',
    description: 'Consultez les segments de rue et leurs règles de circulation.',
    endpoint: '/segments-rue/',
    recherche: 'Rechercher une rue…',
    colonnes: [['nom', 'Nom'], ['type_rue', 'Type'], ['limite_vitesse', 'Vitesse'], ['statut', 'Statut']],
  },
}
