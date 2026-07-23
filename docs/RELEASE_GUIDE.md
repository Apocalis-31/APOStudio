# Guide de publication - APO Studio

Ce guide explique comment publier une nouvelle version d'APO Studio.

---

## Prérequis

Installer sur votre PC :
- **Git** : https://git-scm.com/download/win
- **GitHub CLI** : https://cli.github.com/
  - Ouvrir un terminal et taper : `gh auth login`
  - Suivre les instructions pour se connecter à votre compte GitHub

---

## Étape 1 — Modifier le code

Ouvrir le fichier `src/app_info.py` et changer la version :

```python
VERSION = "1.2.0"   # <-- mettre le nouveau numéro de version ici
```

Règle : `1.0.0` → `1.0.1` (bugfix) → `1.1.0` (nouvelle feature) → `2.0.0` (gros changement)

---

## Étape 2 — Écrire les notes de mise à jour

Ouvrir le fichier `installer/changelog.txt` et écrire ce qui a changé.
Ce texte apparaît dans la release GitHub ET dans l'installateur.

Exemple :
```
🚀 APO Studio v1.2.0

✨ Nouveautés
- Ajout du bouton magique
- Amélioration de la vitesse

🔧 Corrections
- Fix du crash au démarrage
```

---

## Étape 3 — Envoyer sur GitHub

Ouvrir un terminal (PowerShell ou CMD) dans le dossier du projet, puis taper ces commandes une par une :

```bash
git add -A
git commit -m "release: v1.2.0"
git push origin main
```

Si Git demande un nom d'utilisateur et mot de passe, utiliser votre email GitHub et un **token personnel** (pas votre mot de passe). Créer un token sur https://github.com/settings/tokens avec les droits `repo`.

---

## Étape 4 — Créer la release

Toujours dans le terminal, taper :

```bash
git tag v1.2.0
git push origin v1.2.0
```

**C'est tout !** Le reste est automatique.

GitHub va :
1. Compiler l'application (GPU et CPU)
2. Créer l'installateur
3. Publier la release sur https://github.com/Apocalis-31/APOStudio/releases

---

## Vérifier que tout s'est bien passé

Aller sur https://github.com/Apocalis-31/APOStudio/actions

- Si les 3 pastilles sont **vertes** : tout est bon
- Si une pastille est **rouge** : cliquer dessus pour voir l'erreur

Une fois terminé, la release est disponible sur :
https://github.com/Apocalis-31/APOStudio/releases

Elle contient deux installateurs :
- `APOStudio_Setup_x.x.x.exe` — version GPU (plus lourde, ~850 Mo)
- `APOStudio_Setup_CPU_x.x.x.exe` — version CPU (plus légère, ~200 Mo)

---

## En cas d'erreur

### "tag already exists"
Le tag existe déjà. Le supprimer d'abord :
```bash
gh release delete v1.2.0 --repo Apocalis-31/APOStudio --yes --cleanup-tag
git tag -d v1.2.0
```
Puis refaire l'étape 4.

### Le workflow a échoué
Aller sur https://github.com/Apocalis-31/APOStudio/actions, cliquer sur le run en erreur, puis sur le job en rouge pour voir le détail.

### Les fichiers .exe ne sont pas dans la release
Le workflow a peut-être mal matché les noms de fichiers. Vérifier que `installer/changelog.txt` est bien rempli et relancer :
```bash
gh release delete v1.2.0 --repo Apocalis-31/APOStudio --yes --cleanup-tag
git tag -d v1.2.0
git tag v1.2.0
git push origin v1.2.0 --force
```

---

## Résumé rapide (pour les habitués)

```bash
# 1. Changer VERSION dans src/app_info.py
# 2. Écrire installer/changelog.txt
git add -A && git commit -m "release: vX.X.X" && git push origin main
git tag vX.X.X && git push origin vX.X.X
```
