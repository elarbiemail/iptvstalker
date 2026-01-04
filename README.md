# iptvstalker

Small PyQt6 utility to scaffold IPTV Stalker portal servers and generate MAC addresses starting with 00:1a:79:.

Usage:

- Install deps: `pip install -r requirements.txt`
- Run: `python main.py`

The app generates per-client JSON files and an `inventory.json` in the chosen output folder.

Nouvelle fonctionnalité:

- Vous pouvez fournir une liste d'adresses de sites (une par ligne) ; l'application peut tenter de chercher automatiquement des portals Stalker sur ces sites et utiliser le premier portal trouvé.
- Option pour exporter une playlist M3U (`playlist.m3u`) contenant les portals utilisés.

Conseils:

- Activez la recherche automatique si vous fournissez des sites.
- Le probe effectue des requêtes HTTP vers les sites fournis (timeout 5s).

Build Windows executable:

- Vous pouvez tenter de construire un exécutable Windows depuis Linux en utilisant l'image Docker `cdrx/pyinstaller-windows` (Wine + PyInstaller). Un script `build_windows.sh` est fourni.
- Exemple d'usage:

```bash
chmod +x build_windows.sh
./build_windows.sh
```

- Le binaire sera placé dans `dist/`. Testez toujours l'exécutable sur une machine Windows réelle ; le packaging Qt peut nécessiter des DLL/plugins additionnels et des ajustements de `--add-data` ou d'un fichier `.spec` PyInstaller.

- Si vous préférez, buildez directement sur une machine Windows (recommandé) : installez Python, créez un venv, `pip install -r requirements.txt` puis `pyinstaller --noconfirm --onefile --windowed main.py`.

Tests des portals et MACs:

- Utilisez le bouton "Tester portals & MACs" pour exécuter des requêtes vers les portals fournis/découverts et vers les adresses MAC générées.
- L'outil tentera plusieurs variantes d'URL (paramètre `mac`, chemin avec le MAC, etc.) et enregistrera les codes HTTP ou erreurs.
- Les résultats sont affichés dans l'interface et sauvegardés dans `test_results.json` dans le dossier de sortie.

À propos:

- Auteur: El Arbi El Adlouni

Aide dans l'application:

- Le bouton `Aide` dans l'interface explique les étapes d'utilisation (génération, export M3U, tests). Le bouton `À propos` affiche l'auteur.

Barre de progression:

- Une barre de progression dans l'interface indique l'avancement lors de la génération des clients et pendant les tests.
