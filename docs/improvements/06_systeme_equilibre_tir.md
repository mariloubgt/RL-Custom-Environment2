# 06 - Système Équilibré de Récompenses de Tir

## Problème

Après avoir ajouté des pénalités fortes, l'agent est devenu **trop conservateur**:
- ❌ **Tire seulement 4.7% des actions** (trop rare!)
- ❌ **Tourne 95.3% du temps** (trop!)
- ❌ **Évite de tirer** à cause des pénalités trop fortes

L'agent a appris: "Tirer est risqué! Mieux vaut juste tourner et éviter les pénalités!"

## Cause Racine

La structure de pénalité était:
- **Raté bien visé:** -0.1 (petit)
- **Raté mal visé:** -5.0 à -30.0 (très fort!)

L'agent a appris: "Tirer est risqué! Mieux vaut juste tourner et éviter les pénalités!"

## Solution: Système Équilibré Récompense/Pénalité

### Nouvelle Structure: Récompenser les Bonnes Tentatives, Pénaliser les Mauvaises

| Différence d'Angle | Récompense/Pénalité | Comportement Encouragé |
|---------------------|---------------------|------------------------|
| **< 0.3 rad (17°)** | **+2.0 à +0.5** | ✅ **Récompenser les bonnes tentatives!** |
| **0.3-0.5 rad (17-29°)** | **-0.5 à -2.0** | ⚠️ Petite pénalité |
| **0.5-1.0 rad (29-57°)** | **-2.0 à -5.0** | ❌ Pénalité modérée |
| **> 1.0 rad (57°+)** | **-5.0 à -10.0** | ❌ Pénalité forte |

### Changements Clés:

1. **Récompenser les Tentatives Bien Visées** ✅
   - Si angle < 0.3 rad: **+2.0 à +0.5 récompense** (était -0.1 pénalité)
   - Encourage à tirer quand bien aligné
   - Même si raté, bonne tentative est récompensée!

2. **Pénalités Graduées** ✅
   - Petite pénalité pour mauvais alignement modéré (-0.5 à -2.0)
   - Pénalité modérée pour mauvaise visée (-2.0 à -5.0)
   - Pénalité forte seulement pour très mauvaise visée (-5.0 à -10.0)

3. **Suppression des Pénalités Extrêmes** ✅
   - Plus de -15.0 ou -30.0 pénalités
   - Maximum: -10.0 (fort mais pas catastrophique)

## Résultats Attendus

### Avant Système Équilibré:
- Fréquence de tir: **4.7%** (trop faible!)
- Fréquence de rotation: **95.3%** (trop élevée!)
- Différence d'angle moyenne: **3.8 rad (218°)** (terrible!)

### Après Système Équilibré:
- Fréquence de tir: **15-25%** (beaucoup mieux!)
- Fréquence de rotation: **75-85%** (plus équilibré)
- Différence d'angle moyenne: **< 0.5 rad (29°)** (beaucoup mieux!)

## Pourquoi Cela Fonctionnera

### Renforcement Positif

- **Tentatives bien visées:** +2.0 récompense (même si raté!)
- **L'agent apprend:** "Bonne visée = récompense, même si je rate!"

### Pénalités Graduées

- **Petit mauvais alignement:** Petite pénalité (-0.5 à -2.0)
- **Mauvaise visée:** Pénalité modérée (-2.0 à -5.0)
- **Très mauvaise visée:** Pénalité forte (-5.0 à -10.0)

### Signal Clair

- **Bonne tentative:** +2.0
- **Mauvaise tentative:** -5.0 à -10.0
- **Différence:** 12.0 à 12.0 (clair, mais pas extrême)

---

**Fichier:** `docs/balanced_firing_rewards.md`  
**Date:** Après pénalités renforcées  
**Statut:** ✅ Implémenté

