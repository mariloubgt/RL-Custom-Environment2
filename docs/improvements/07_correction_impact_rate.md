# 07 - Correction du Taux d'Impact

## Problème

Malgré d'excellentes performances:
- ✅ **Hit Rate: 46-72%** (excellent!)
- ✅ **Destruction Rate: 95-106%** (excellent!)
- ✅ **Success Rate: 100%** (parfait!)
- ❌ **Impact Rate: 35-45%** (augmente!)

L'agent devient **trop agressif** - se concentre sur la destruction d'astéroïdes (récompenses élevées) mais laisse certains astéroïdes atteindre la planète.

## Cause Racine

La structure de récompense **favorise la destruction sur la survie**:
- Récompenses élevées pour touches (+50 à +95)
- Récompenses élevées pour détruire astéroïdes
- Mais **pas assez fortes** incitations à la survie

L'agent apprend: "Détruire beaucoup d'astéroïdes = récompense élevée, même si certains touchent la planète!"

## Solution: Augmenter Dramatiquement les Récompenses de Survie

### 1. Pénalité d'Impact Augmentée ✅

**Avant:**
- Pénalité d'impact: **-200.0**

**Après:**
- Pénalité d'impact: **-500.0** (+150% d'augmentation)

**Pourquoi:** Rendre les impacts BEAUCOUP plus coûteux. L'agent devrait craindre les impacts!

### 2. Récompenses de Survie Augmentées ✅

**Avant:**
- Récompense de survie par step: **0.5**
- Bonus de survie: (5 - remaining) * 0.3

**Après:**
- Récompense de survie par step: **1.0** (+100% d'augmentation)
- Bonus de survie: (5 - remaining) * **0.5** (+67% d'augmentation)
- **NOUVEAU:** Bonus prévention danger: **2.0 par astéroïde dangereux**

**Pourquoi:** Rappel constant fort que la survie est la priorité #1.

### 3. Bonus de Survie d'Épisode Augmenté ✅

**Avant:**
- Bonus de survie d'épisode: **30.0**
- Pénalité astéroïdes restants: **5.0 par astéroïde**

**Après:**
- Bonus de survie d'épisode: **100.0** (+233% d'augmentation!)
- Pénalité astéroïdes restants: **10.0 par astéroïde** (+100% d'augmentation)

**Pourquoi:** Énorme récompense pour survivre à l'épisode entière sans impact.

## Nouvelle Structure de Récompense

### Survie vs Destruction:

| Situation | Récompense | Priorité |
|-----------|------------|----------|
| **Survivre épisode** | +100.0 | ✅ La plus haute! |
| **Survivre step** | +1.0 par step | ✅ Élevée |
| **Prévenir astéroïde dangereux** | +2.0 par dangereux | ✅ Élevée |
| **Détruire astéroïde** | +50 à +95 | ✅ Bonne |
| **Impact planète** | **-500.0** | ❌ **TERRIBLE!** |

### Effet Net:

- **Survivre épisode:** +100.0 (énorme!)
- **Détruire tous astéroïdes:** +100.0 + bonus efficacité
- **Laisser astéroïde toucher:** -500.0 (catastrophique!)

L'agent devrait maintenant apprendre: **"La survie est plus importante que la destruction!"**

## Résultats Attendus

### Avant Correction:
- Impact Rate: **35-45%** (augmente)
- Agent priorise destruction
- Certains astéroïdes atteignent planète

### Après Correction:
- Impact Rate: **15-25%** (diminue)
- Agent priorise survie
- Meilleure priorisation astéroïdes
- Comportement plus défensif

---

**Fichier:** `docs/impact_rate_fix.md`  
**Date:** Après 50,000 épisodes  
**Statut:** ✅ Implémenté

