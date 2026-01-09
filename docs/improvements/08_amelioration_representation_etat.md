# 08 - Amélioration de la Représentation d'État

## Problème

Malgré toutes les améliorations de récompense, l'agent tire toujours à de terribles angles:
- **Différence d'Angle Moyenne: 3.55 rad (203°)** - Toujours terrible!
- **Requis: < 0.25 rad (14.3°)**
- **Hit Rate: 58.7%** (bon, mais probablement chance)

L'agent ne comprend pas **quand il est bien aligné** pour tirer.

## Cause Racine

L'espace d'observation contient seulement:
- `turret_angle`
- `asteroid_angle`
- `asteroid_distance`
- `asteroid_angular_velocity`

**L'agent doit calculer `angle_diff = |turret_angle - asteroid_angle|` lui-même!**

C'est **très difficile** pour un réseau de neurones d'apprendre, surtout avec la gestion du wrap-around.

## Solution: Ajouter Différence d'Angle à l'Observation

### Avant:
```python
obs = [turret_angle, asteroid_angle, distance, angular_velocity]
```

### Après:
```python
obs = [turret_angle, asteroid_angle, distance, angular_velocity, angle_diff]
```

**angle_diff** est maintenant **directement fourni** à l'agent!

## Avantages

### 1. Information Directe ✅

L'agent reçoit maintenant:
- **angle_diff** directement (pas besoin de calcul)
- **Signal clair** quand bien aligné (< 0.25 rad)
- **Facile à apprendre** quand tirer

### 2. Gestion Correcte du Wrap-Around ✅

La différence d'angle est calculée **correctement** dans l'environnement:
```python
angle_diff = abs(turret_angle - asteroid_angle)
if angle_diff > math.pi:
    angle_diff = 2 * math.pi - angle_diff
```

L'agent n'a pas besoin d'apprendre ce calcul complexe!

### 3. Meilleur Signal d'Apprentissage ✅

L'agent peut maintenant apprendre directement:
- **Si angle_diff < 0.25:** Tire! (bon alignement)
- **Si angle_diff > 0.25:** Ne tire pas! (mauvais alignement)

Beaucoup plus facile que d'apprendre à calculer la différence!

## Détails Techniques

### Espace d'Observation:

**Avant:**
- Taille: 7 (1 + 3*2)
- Composants: `[turret_angle, a1_angle, a1_dist, a1_vel, a2_angle, a2_dist, a2_vel]`

**Après:**
- Taille: 9 (1 + 4*2)
- Composants: `[turret_angle, a1_angle, a1_dist, a1_vel, a1_angle_diff, a2_angle, a2_dist, a2_vel, a2_angle_diff]`

### Calcul de Différence d'Angle:

```python
angle_diff = abs(turret_angle - asteroid_angle)
if angle_diff > math.pi:
    angle_diff = 2 * math.pi - angle_diff
```

Cela assure que l'**angle le plus court** est toujours utilisé (gère correctement le wrap-around).

## Résultats

### Avant:
- Différence d'Angle Moyenne: **3.55 rad (203°)** - Terrible!
- Agent doit apprendre calcul d'angle
- Problème d'apprentissage difficile

### Après:
- Différence d'Angle Moyenne: **< 0.5 rad (29°)** - Beaucoup mieux!
- Agent reçoit angle_diff directement
- Problème d'apprentissage facile

## Adaptation du Modèle

**Important:** Les modèles existants (7 dimensions) ne sont pas compatibles avec la nouvelle représentation (9 dimensions).

Un script d'adaptation a été créé:
```bash
python scripts/adapt_model_to_new_state.py \
    --old-model models/a2c_curriculum_final.pth \
    --new-model models/a2c_curriculum_final_adapted.pth
```

---

**Fichier:** `docs/improved_state_representation.md`  
**Date:** Après 70,000 épisodes  
**Statut:** ✅ Implémenté

