# Fusionner des PDF

Petite application Windows avec interface graphique Tkinter pour sélectionner, réorganiser et fusionner plusieurs PDF avec `pypdf`.

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

L’application permet ensuite d’ajouter les PDF, de les monter ou descendre, puis de choisir l’emplacement du fichier final avec **Fusionner les PDF**.

## Créer un fichier `.exe` avec PyInstaller

Installer PyInstaller :

```powershell
py -m pip install pyinstaller
```

Créer l’exécutable Windows :

```powershell
py -m PyInstaller --onefile --windowed --name FusionnerPDF merge_pdfs.py
```

Le fichier `FusionnerPDF.exe` sera créé dans le dossier `dist`. Il peut être lancé par double-clic, sans ouvrir de terminal.
