# 04 - Correction des Tirs à Mauvais Angles

## 🔴 Problème Identifié

Le diagnostic a montré:
- **Différence d'Angle Moyenne (Tous): 9.5 rad (544°)** - L'agent tire à des angles terribles!
- **Différence d'Angle Moyenne (Touches): 13.9 rad (795°)** - Même les touches sont à mauvais angles (probablement chance)
- **Différence d'Angle Moyenne (Ratés): 8.5 rad (489°)** - Les ratés sont à très mauvais angles

L'agent ne comprend pas **quand tirer** - il tire aléatoirement peu importe l'alignement.

## Cause Racine

L'agent recevait:
- ✅ Petite récompense pour tentatives de tir (0.2)
- ✅ Petite pénalité pour ratés (-0.1)
- ❌ **AUCUNE pénalité pour tirer quand mal aligné**

Cela signifiait que l'agent apprenait: "Tire quand tu veux, peu importe si tu vises!"

## Solution Implémentée

### 1. Pénalité Forte pour Mauvaise Visée ✅

Ajout d'une **pénalité pour tirer quand PAS bien aligné** :

```python
# PÉNALITÉ FORTE pour tirer quand PAS bien aligné
if not hit and closest_asteroid_for_fire:
    # Calculer à quel point la visée est mauvaise
    bad_aim_penalty = -2.0 * min(min_angle_diff / math.pi, 1.0)  # Jusqu'à -2.0
    reward += bad_aim_penalty
    
    # Pénalité supplémentaire si très loin de la cible
    if min_angle_diff > 0.5:  # Plus de 90 degrés
        severe_miss_penalty = -3.0
        reward += severe_miss_penalty
```

**Structure de Pénalité:**
- **Mauvaise visée (< 0.5 rad):** -0 à -2.0 (échelonné selon la gravité)
- **Très mauvaise visée (> 0.5 rad):** -2.0 à -5.0 (pénalité sévère)

### 2. Calcul d'Angle Correct ✅

Correction du calcul de différence d'angle pour gérer le wrap-around correctement:

```python
# Calculer différence d'angle avec gestion correcte du wrap-around
angle_diff = abs(self.turret_angle - a["angle"])
# Gérer wrap-around (différence d'angle la plus courte)
if angle_diff > math.pi:
    angle_diff = 2 * math.pi - angle_diff
```

**Avantages:**
- Calculs d'angle corrects (pas de faux grands angles)
- Calcul de pénalité correct
- Récompenses de visée précises

## Résultats Attendus

### Avant Correction:
- ❌ Différence d'Angle Moyenne: **9.5 rad (544°)** - Terrible!
- ❌ L'agent tire aléatoirement
- ❌ Pas de compréhension de quand tirer

### Après Correction:
- ✅ Différence d'Angle Moyenne: **< 0.5 rad (29°)** - Beaucoup mieux!
- ✅ L'agent apprend à viser avant de tirer
- ✅ Pénalité forte décourage les mauvais tirs

## Structure de Récompense Maintenant

### Récompenses de Tir:
1. **Touche:** +30 à +75 (selon précision, distance, série)
2. **Raté (bien visé):** -0.1 (petite pénalité)
3. **Raté (mal visé):** -0.1 à -5.0 (pénalité forte!)
4. **Tirer sur astéroïde proche:** +0.2 (encourage la défense)

### Effet Net:
- **Tir bien visé:** Potentiel de récompense élevé (+30 à +75)
- **Tir mal visé:** Pénalité forte (-2.0 à -5.0)
- **L'agent apprend:** "Tire seulement quand bien aligné!"

## Recommandations d'Entraînement

### 1. Continuer l'Entraînement avec Nouvelles Pénalités

```bash
python training/train_curriculum_a2c.py \
    --episodes 60000 \
    --resume-from models/a2c_curriculum_final.pth
```

**Améliorations attendues:**
- Différence d'Angle Moyenne: 9.5 rad → **< 0.5 rad**
- Hit Rate: 14.0% → **20-25%**
- Meilleures décisions de tir

### 2. Surveiller l'Entraînement

Surveiller:
- **Différences d'angle lors du tir** (devrait diminuer)
- **Hit rate** (devrait augmenter)
- **Fréquence de tir** (peut diminuer initialement, puis se stabiliser)

---

**Fichier:** `docs/firing_penalty_fix.md`  
**Date:** Après diagnostic  
**Statut:** ✅ Implémenté

