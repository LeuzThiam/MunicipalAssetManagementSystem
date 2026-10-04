# Indexation spatiale

Les géométries des bornes, bâtiments et segments de rue utilisent PostGIS en
SRID 4326. GeoDjango crée un index GiST sur chaque colonne. Ce choix est déclaré
explicitement avec `spatial_index=True` dans les modèles.

Pour vérifier les index et comparer les performances :

```powershell
docker compose run --rm backend python manage.py analyser_indexation_spatiale
```

La commande vérifie `pg_indexes`, puis exécute `EXPLAIN ANALYZE` avec et sans
parcours d'index. Elle ne supprime aucun index et ne modifie pas la configuration
permanente de PostgreSQL. Le point et le rayon peuvent être changés avec les options
`--latitude`, `--longitude` et `--rayon`.

## Mesure de reference

Mesure réalisée le 3 octobre 2026 avec le point `45.75, -73.46` et un rayon de
1 000 metres :

| Jeu de donnees | Resultats | Sans index | Avec index | Gain | Plan indexe |
| --- | ---: | ---: | ---: | ---: | --- |
| Bornes | 203 | 15,135 ms | 0,600 ms | x25,23 | Bitmap Heap Scan / Bitmap Index Scan |
| Batiments | 1 821 | 219,652 ms | 118,571 ms | x1,85 | Gather / Bitmap Heap Scan / Bitmap Index Scan |
| Segments de rue | 369 | 26,529 ms | 5,470 ms | x4,85 | Bitmap Heap Scan / Bitmap Index Scan |

Ces temps sont une référence locale. Le `Bitmap Index Scan` observé dans chaque
plan confirme que PostgreSQL utilise bien les index GiST.
