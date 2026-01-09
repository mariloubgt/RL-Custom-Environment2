# 05 - Pénalités de Tir Renforcées

## Problème

Même après avoir ajouté des pénalités, l'agent tire toujours à de mauvais angles:
- **Différence d'Angle Moyenne: 3.37 rad (193°)** - Toujours terrible!
- **Requis: < 0.25 rad (14.3°)**
- **Hit Rate: 11.7%** - Faible à cause de la mauvaise visée

Les pénalités n'étaient **pas assez fortes** pour décourager les mauvais tirs.

## Solution: Pénalités Dramatiquement Augmentées

### 1. Pénalité de Mauvaise Visée Augmentée ✅

**Avant:**
- Pénalité mauvaise visée: **-2.0** (trop faible)
- Pénalité raté sévère: **-3.0** (trop faible)

**Après:**
- Pénalité mauvaise visée: **-5.0** (échelonné selon la gravité)
- Pénalité raté sévère: **-10.0** (pour > 90°)
- Pénalité raté extrême: **-15.0** (pour > 115°)

**Pénalité totale pour très mauvais tir: Jusqu'à -30.0!**

### 2. Récompense de Touche Augmentée ✅

**Avant:**
- Récompense de touche de base: **30.0**

**Après:**
- Récompense de touche de base: **50.0** (+67% d'augmentation)

**Pourquoi:** Rend les bonnes touches beaucoup plus attractives comparées aux mauvais tirs.

### 3. Suppression de l'Incitation aux Mauvais Tirs ✅

**Avant:**
- Petite récompense (+0.2) pour tirer sur astéroïdes proches (même si mal visé)
- Cela **encourageait le mauvais comportement**!

**Après:**
- **AUCUNE récompense** pour tentatives de tir mal visées
- Les récompenses viennent seulement des **touches réelles**

## Nouvelle Structure de Récompense

### Récompenses de Tir:

| Situation | Récompense | Plage Totale |
|-----------|------------|--------------|
| **Touche Parfaite** | +50 à +95 | Excellent! |
| **Bonne Touche** | +50 à +75 | Bon! |
| **Raté (bien visé)** | -0.1 | Petite pénalité |
| **Raté (mal visé)** | -5.0 à -15.0 | Pénalité forte! |
| **Raté (très mal visé)** | -15.0 à -30.0 | **Pénalité extrême!** |

### Effet Net:

- **Tir bien visé:** +50 à +95 récompense
- **Tir mal visé:** -5.0 à -30.0 pénalité
- **Différence:** Jusqu'à **125.0** différence de récompense!

Cela crée un **signal très fort** que la mauvaise visée est terrible.

## Résultats Attendus

### Avant Pénalités Renforcées:
- Différence d'Angle Moyenne: **3.37 rad (193°)** - Terrible!
- Hit Rate: **11.7%** - Faible
- L'agent tire aléatoirement

### Après Pénalités Renforcées:
- Différence d'Angle Moyenne: **< 0.5 rad (29°)** - Beaucoup mieux!
- Hit Rate: **20-30%** - Amélioration significative
- L'agent apprend à viser avant de tirer

## Pourquoi Cela Fonctionnera

### Signal Négatif Fort

Les pénalités sont maintenant **5-15x plus fortes**:
- Mauvaise visée: -5.0 (était -2.0)
- Sévère: -10.0 (était -3.0)
- Extrême: -15.0 (nouveau!)

### Signal Positif Fort

La récompense de touche est maintenant **67% plus élevée**:
- Touche de base: +50.0 (était +30.0)
- Récompense totale de touche: Jusqu'à +95 (était +75)

### Contraste Clair

- **Bon tir:** +50 à +95
- **Mauvais tir:** -5 à -30
- **Différence:** Jusqu'à 125.0!

Cela crée un **signal indéniable** que l'agent ne peut ignorer.

---

**Fichier:** `docs/enhanced_firing_penalties.md`  
**Date:** Après première correction  
**Statut:** ✅ Implémenté

