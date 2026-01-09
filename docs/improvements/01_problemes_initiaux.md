# 01 - Problèmes Initiaux Identifiés

## 🔴 État Initial de l'Agent

### Diagnostic Initial
- **Distribution des Actions:** 100% rotation gauche, 0% tir, 0% rotation droite
- **Comportement de Tir:** L'agent NE TIRE JAMAIS
- **Politique:** Complètement cassée - a appris une politique "tourner seulement à gauche"

## Cause Racine

L'agent a convergé vers une politique dégénérée :
1. **Pas d'exploration** - Entropie trop faible pendant l'entraînement
2. **Structure de récompense** - Pénalité de raté décourage le tir
3. **Minimum local** - L'agent a trouvé une politique "sûre" (ne rien faire)

## Métriques Initiales

| Métrique | Valeur | Statut |
|----------|--------|--------|
| Hit Rate | **0%** | ❌ Cassé |
| Turret Movement | **0.0°** | ❌ Immobile |
| Impact Rate | **100%** | ❌ Tous les épisodes finissent par impact |
| Success Rate | **0-75%** | ❌ Incohérent |
| Mean Reward | **-61.21 à 55.56** | ❌ Très variable |

## Solution Recommandée

### Curriculum Learning (RECOMMANDÉ)

Démarrer un nouvel entraînement avec curriculum learning qui force l'exploration :

```bash
python training/train_curriculum_a2c.py --episodes 20000
```

**Pourquoi ça fonctionne :**
- Phase 1: Entropie élevée (0.2) force l'agent à essayer TOUTES les actions
- Empêche la convergence vers des politiques dégénérées
- Réduit graduellement l'entropie pendant que l'agent apprend

## Prochaines Étapes

1. ✅ Démarrer l'entraînement curriculum
2. ✅ Surveiller le progrès (rotation vs tir)
3. ✅ Ré-évaluer après l'entraînement

---

**Fichier:** `evaluation/fix_broken_agent.md`  
**Date:** Début du projet  
**Statut:** ✅ Résolu avec curriculum learning

