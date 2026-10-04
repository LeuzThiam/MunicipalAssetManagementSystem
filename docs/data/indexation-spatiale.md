# Indexation spatiale PostGIS

Les colonnes `geometrie` des bornes, des batiments et des segments de rue sont
des colonnes `geography` en SRID 4326. GeoDjango cree un index spatial GiST pour
chacune d'elles. Le parametre `spatial_index=True` est aussi indique explicitement
dans les modeles afin de rendre cette exigence visible dans le code.

## Verifier les index et mesurer leur effet

Depuis la racine du projet :

```powershell
docker compose run --rm backend python manage.py analyser_indexation_spatiale
```

La commande :

1. interroge `pg_indexes` et echoue si un index GiST manque ;
2. execute `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` pour chaque jeu de donnees ;
3. mesure d'abord la requete avec les parcours d'index desactives localement ;
4. relance la meme requete avec le planificateur normal et affiche le facteur de gain.

Les index ne sont jamais supprimes pendant la comparaison. Les options permettent
de choisir un autre point et un autre rayon :

```powershell
docker compose run --rm backend python manage.py analyser_indexation_spatiale `
  --latitude 45.75 --longitude -73.46 --rayon 1000
```

Les temps dependent de la machine, du cache PostgreSQL, du volume de donnees et du
nombre d'objets dans le rayon. Il faut donc conserver les plans affiches avec les
mesures lors de toute comparaison de performance.

## Mesure de reference

Mesure realisee le 3 octobre 2026 avec le point `45.75, -73.46` et un rayon de
1 000 metres :

| Jeu de donnees | Resultats | Sans index | Avec index | Gain | Plan indexe |
| --- | ---: | ---: | ---: | ---: | --- |
| Bornes | 203 | 15,135 ms | 0,600 ms | x25,23 | Bitmap Heap Scan / Bitmap Index Scan |
| Batiments | 1 821 | 219,652 ms | 118,571 ms | x1,85 | Gather / Bitmap Heap Scan / Bitmap Index Scan |
| Segments de rue | 369 | 26,529 ms | 5,470 ms | x4,85 | Bitmap Heap Scan / Bitmap Index Scan |

Ces valeurs constituent une reference locale, pas une garantie de temps de reponse.
La presence de `Bitmap Index Scan` dans chaque plan confirme toutefois que PostgreSQL
emploie bien les index GiST pour ces recherches de proximite.
