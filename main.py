#!/usr/bin/env python3
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QSpinBox, QFileDialog, QMessageBox, QHBoxLayout,
    QTextEdit, QCheckBox, QProgressBar, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
import sys
import secrets
import requests
import re
from urllib.parse import urljoin
from PyQt6.QtGui import QColor
from pathlib import Path
import json

PREFIX = "00:1a:79"

def generate_mac(prefix=PREFIX):
    parts = prefix.split(':')
    r = [f"{secrets.randbelow(256):02x}" for _ in range(3)]
    return ':'.join(parts + r)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IPTV Stalker Scaffolder")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Nom du serveur:"))
        self.name = QLineEdit("iptv-server")
        layout.addWidget(self.name)

        layout.addWidget(QLabel("Portal URL:"))
        self.portal = QLineEdit("http://example.com/c/MTIzNDU6")
        layout.addWidget(self.portal)

        layout.addWidget(QLabel("Adresses de sites (une par ligne) :"))
        self.sites = QTextEdit()
        self.sites.setPlaceholderText("https://example.org\nhttps://autre-site.com")
        layout.addWidget(self.sites)

        self.probe_cb = QCheckBox("Chercher automatiquement les portals dans les sites fournis")
        self.probe_cb.setChecked(True)
        layout.addWidget(self.probe_cb)

        self.m3u_cb = QCheckBox("Exporter une playlist M3U")
        self.m3u_cb.setChecked(False)
        layout.addWidget(self.m3u_cb)

        # Tester panels
        test_h = QHBoxLayout()
        self.btn_test = QPushButton("Tester portals & MACs")
        self.btn_test.clicked.connect(self.run_tests)
        test_h.addWidget(self.btn_test)

        btn_help = QPushButton("Aide")
        btn_help.clicked.connect(self.show_help)
        test_h.addWidget(btn_help)

        btn_about = QPushButton("À propos")
        btn_about.clicked.connect(self.show_about)
        test_h.addWidget(btn_about)
        layout.addLayout(test_h)

        layout.addWidget(QLabel("Liste des portals trouvés:"))
        self.portal_list = QListWidget()
        layout.addWidget(self.portal_list)

        layout.addWidget(QLabel("Résultats des tests:"))
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        layout.addWidget(self.results)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        hl = QHBoxLayout()
        hl.addWidget(QLabel("Nombre de clients:"))
        self.count = QSpinBox()
        self.count.setRange(1, 1000)
        self.count.setValue(10)
        hl.addWidget(self.count)
        layout.addLayout(hl)

        out_h = QHBoxLayout()
        out_h.addWidget(QLabel("Répertoire de sortie:"))
        self.out = QLineEdit(str(Path.cwd() / "output"))
        out_h.addWidget(self.out)
        btn_browse = QPushButton("Parcourir")
        btn_browse.clicked.connect(self.browse)
        out_h.addWidget(btn_browse)
        layout.addLayout(out_h)

        self.btn = QPushButton("Générer")
        self.btn.clicked.connect(self.generate)
        layout.addWidget(self.btn)

        self.setLayout(layout)

    def browse(self):
        d = QFileDialog.getExistingDirectory(self, "Choisir dossier de sortie", str(Path.cwd()))
        if d:
            self.out.setText(d)

    def generate(self):
        name = self.name.text().strip() or "iptv-server"
        portal = self.portal.text().strip()
        sites_text = self.sites.toPlainText().strip()
        probe = self.probe_cb.isChecked()
        export_m3u = self.m3u_cb.isChecked()
        n = self.count.value()
        outdir = Path(self.out.text()).expanduser()
        outdir.mkdir(parents=True, exist_ok=True)

        macs = set()
        records = []

        discovered_portals = []
        if probe and sites_text:
            sites = [s.strip() for s in sites_text.splitlines() if s.strip()]
            discovered_portals = probe_sites(sites)
            if discovered_portals:
            portal = discovered_portals[0]
        # save discovered portals to the instance for later testing
        self.discovered_portals = discovered_portals
        # populate portal list UI
        self.populate_portal_list()
        self.progress.setRange(0, n)
        self.progress.setValue(0)
        for i in range(n):
            mac = generate_mac()
            while mac in macs:
                mac = generate_mac()
            macs.add(mac)
            record = {
                "server_name": f"{name}-{i+1}",
                "portal": portal,
                "mac": mac
            }
            records.append(record)
            p = outdir / f"{name}-{i+1}.json"
            p.write_text(json.dumps(record, indent=2))
            self.progress.setValue(i+1)
            QApplication.processEvents()

        (outdir / "inventory.json").write_text(json.dumps(records, indent=2))

        if export_m3u:
            playlist = ["#EXTM3U"]
            for r in records:
                playlist.append(f"#EXTINF:-1,{r['server_name']}")
                playlist.append(r['portal'])
            (outdir / "playlist.m3u").write_text("\n".join(playlist))

        # If we discovered additional portals, save them for reference
        if discovered_portals:
            (outdir / "discovered_portals.json").write_text(json.dumps(discovered_portals, indent=2))
        QMessageBox.information(self, "Terminé", f"Généré {n} clients dans:\n{outdir}")

    def show_help(self):
        text = (
            "Utilisation:\n"
            "1) Remplissez 'Nom du serveur' et 'Portal URL' ou fournissez des sites pour discovery.\n"
            "2) Choisissez le nombre de clients et le répertoire de sortie.\n"
            "3) Cliquez sur 'Générer' pour créer des fichiers JSON par client et 'inventory.json'.\n"
            "4) (Optionnel) Activez 'Exporter une playlist M3U' pour produire 'playlist.m3u'.\n"
            "5) Utilisez 'Tester portals & MACs' pour vérifier les portals et les adresses MAC; les résultats seront enregistrés dans 'test_results.json'.\n"
        )
        QMessageBox.information(self, "Aide - Utilisation", text)

    def show_about(self):
        QMessageBox.information(self, "À propos", "El Arbi El Adlouni\nIPTV Stalker Scaffolder - utilitaire PyQt6")

    def run_tests(self):
        # Collect portals: explicit portal + discovered ones
        portal_text = self.portal.text().strip()
        portals = []
        if portal_text:
            portals.append(portal_text)
        portals += getattr(self, 'discovered_portals', []) or []
        portals = [p for i, p in enumerate(portals) if p and p not in portals[:i]]

        # populate portal list UI before testing
        self.populate_portal_list(portals)

        outdir = Path(self.out.text()).expanduser()
        outdir.mkdir(parents=True, exist_ok=True)

        # Collect MACs: try to load inventory.json, else generate sample
        macs = []
        inv = outdir / 'inventory.json'
        if inv.exists():
            try:
                data = json.loads(inv.read_text())
                macs = [d.get('mac') for d in data if d.get('mac')]
            except Exception:
                macs = []
        if not macs:
            # generate a few sample macs based on count
            for _ in range(min(10, self.count.value())):
                macs.append(generate_mac())

        if not portals:
            QMessageBox.warning(self, "Aucun portal", "Aucun portal fourni ou découvert pour tester.")
            return

        results = {}
        headers = {"User-Agent": "iptvstalker-scaffolder/1.0"}
        self.results.clear()
        total = len(portals) if portals else 1
        self.progress.setRange(0, total)
        self.progress.setValue(0)
        for idx, p in enumerate(portals):
            results[p] = {}
            ok_any = False
            for m in macs:
                self.results.append(f"Testing portal={p} mac={m}...")
                QApplication.processEvents()
                attempts = test_portal_mac(p, m, headers)
                results[p][m] = attempts
                # summarize
                ok = any(a.get('status') == 200 for a in attempts)
                if ok:
                    ok_any = True
                self.results.append(f" -> {'OK' if ok else 'FAIL'} ({len(attempts)} attempts)")
            # color the portal list item green if any mac succeeded, red otherwise
            self.color_portal_item(p, ok_any)
            self.progress.setValue(idx + 1)
            QApplication.processEvents()
        # save results
        (outdir / 'test_results.json').write_text(json.dumps(results, indent=2))
        QMessageBox.information(self, "Tests terminés", f"Tests terminés. Résultats sauvegardés dans:\n{outdir / 'test_results.json'}")


def probe_sites(sites):
    found = []
    headers = {"User-Agent": "iptvstalker-scaffolder/1.0"}
    patterns = [
        re.compile(r'(https?://[^\s"']+/c/[^\s"']+)'),
        re.compile(r'href=["\']([^"\']*/c/[^"\']+)["\']'),
        re.compile(r'(https?://[^\s"']+/stalker_portal[^\s"']*)'),
    ]
    for site in sites:
        try:
            r = requests.get(site, headers=headers, timeout=5)
            if not r.ok:
                continue
            text = r.text
            for pat in patterns:
                for m in pat.findall(text):
                    url = m
                    # If match is relative path, join with base
                    if url.startswith('/'):
                        url = urljoin(site, url)
                    if url not in found:
                        found.append(url)
        except Exception:
            continue
    return found


def test_portal_mac(portal, mac, headers=None):
    if headers is None:
        headers = {"User-Agent": "iptvstalker-scaffolder/1.0"}
    variants = []
    portal = portal.strip()
    variants.append(portal)
    # common query variants
    variants.append(f"{portal.rstrip('/')}/?mac={mac}")
    variants.append(f"{portal.rstrip('/')}/mac:{mac}")
    variants.append(f"{portal.rstrip('/')}/{mac}")
    variants.append(f"{portal.rstrip('/')}/c/{mac}")

    attempts = []
    for url in variants:
        try:
            r = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
            attempts.append({"url": url, "status": r.status_code, "ok": r.ok})
            if r.ok:
                # stop on first OK
                break
        except Exception as e:
            attempts.append({"url": url, "error": str(e)})
    return attempts


    def populate_portal_list(self, portals=None):
        # If portals is None, use current discovered + explicit portal
        if portals is None:
            portals = []
            p_text = self.portal.text().strip()
            if p_text:
                portals.append(p_text)
            portals += getattr(self, 'discovered_portals', []) or []
            portals = [p for i, p in enumerate(portals) if p and p not in portals[:i]]
        self.portal_list.clear()
        for p in portals:
            item = QListWidgetItem(p)
            item.setData(1, p)
            self.portal_list.addItem(item)

    def color_portal_item(self, portal, ok):
        # find item with matching text and color it
        for i in range(self.portal_list.count()):
            item = self.portal_list.item(i)
            if item.text() == portal:
                color = QColor(200, 255, 200) if ok else QColor(255, 200, 200)
                item.setBackground(color)
                return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(600, 200)
    w.show()
    sys.exit(app.exec())
