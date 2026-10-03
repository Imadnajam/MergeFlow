# Fusionner des PDF

Petite application Windows avec interface graphique Tkinter pour sélectionner, réorganiser et fusionner plusieurs PDF avec `pypdf`.

## Fonctionnalités

- Sélection de plusieurs PDF en une seule fois
- Réorganisation avec **Monter** et **Descendre**
- Suppression d’un fichier ou vidage complet de la liste
- Fusion dans l’ordre affiché, avec compteur de pages créé
- Protection contre l’écrasement accidentel d’un fichier source
- Écriture temporaire de la sortie pour éviter un fichier final incomplet
- Ouverture directe du dossier contenant le PDF généré

Les erreurs de fichier corrompu, de destination inaccessible et d’enregistrement annulé sont signalées dans l’interface.

## Installation et lancement

1. Installer Python 3.10 ou une version plus récente depuis [python.org](https://www.python.org/downloads/). Pendant l’installation, cocher **Add Python to PATH**.
2. Ouvrir un terminal dans ce dossier et installer la dépendance :

   ```powershell
   py -m pip install -r requirements.txt
   ```

3. Lancer l’application :

   ```powershell
   py merge_pdfs.py
   ```

L’application permet ensuite d’ajouter les PDF, de les monter ou descendre, puis de choisir l’emplacement du fichier final avec **Fusionner les PDF**. Le dernier fichier ajouté est automatiquement sélectionné.

### Raccourcis clavier

- `Ctrl+O` : ajouter des PDF
- `Suppr` : supprimer le fichier sélectionné
- `Ctrl+Up` / `Ctrl+Down` : déplacer le fichier sélectionné

## Créer un fichier `.exe` avec PyInstaller

Installer PyInstaller :

```powershell
py -m pip install pyinstaller
```

Créer l’exécutable Windows :

```powershell
py -m PyInstaller --onefile --windowed --name FusionnerPDF merge_pdfs.py
```

Le fichier `FusionnerPDF.exe` sera créé dans le dossier `dist`. Il peut être lancé par double-clic, sans ouvrir de terminal. Le dossier `dist` peut être copié sur un autre ordinateur Windows ; Python n’y sera pas nécessaire.

Pour une version distribuable, conserver uniquement `dist\FusionnerPDF.exe`. Les dossiers `build` et le fichier `.spec` sont des artefacts temporaires de PyInstaller.

## Structure du projet

```text
merge_pdfs.py      # application Tkinter et logique de fusion
requirements.txt   # dépendance Python
pdfs/              # exemples de fichiers PDF locaux
```
