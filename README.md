# DBS II – Aufgabenblatt 2

Implementiert Two-Phase Multiway Mergesort (TPMMS) für ein DBMS mit begrenztem
Hauptspeicher. Das Aufgabenblatt enthält die Anforderungen, Hinweise zum
Framework und die drei Quizfragen.

## Privates Repository für eure Zweiergruppe einrichten

1. Ein Gruppenmitglied erstellt auf GitHub ein leeres Repository für die Gruppe.
   Wählt die Sichtbarkeit **Private** und lasst README, Lizenz und `.gitignore`
   beim Erstellen abgewählt. Diese Dateien bringt der Programmrahmen bereits mit.
   Haltet eure Lösung privat.
2. Kopiert den Programmrahmen in das Gruppenrepository. Ersetzt
   `URL_DES_GRUPPENREPOS` im folgenden Befehl durch die Git-URL eures **privaten**
   Repositorys.

   ```bash
   git clone https://github.com/HPI-Information-Systems-Teaching/DBSII-WS2026-exercise2.git exercise-2
   cd exercise-2
   git remote set-url origin URL_DES_GRUPPENREPOS
   git push -u origin main
   ```

3. Ladet das zweite Gruppenmitglied mit Schreibzugriff ein. Es kann dann das
   private Repository klonen und mit derselben Codebasis arbeiten.

   ```bash
   git clone URL_DES_GRUPPENREPOS exercise-2
   cd exercise-2
   ```

   Arbeitet ihr beide auf `main`, holt zu Beginn jeder Arbeitssitzung mit
   `git pull --ff-only` die Änderungen des anderen Gruppenmitglieds.

4. Ladet den GitHub-Benutzer **`sedirmohammed`** zur Korrektur in euer privates
   Repository ein. Gewährt mindestens Leserechte und versendet die Einladung
   spätestens bis zum Abgabetermin.

## Python einrichten

Ihr benötigt **Python 3.11 oder neuer** und Git. Führt die Befehle im
Projektverzeichnis aus. Jedes Gruppenmitglied richtet seine eigene virtuelle
Umgebung ein.

### macOS und Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Falls PowerShell die Aktivierung blockiert, könnt ihr den Interpreter direkt
aufrufen.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest
```

Die Installation richtet pytest und das lokale Projekt im editierbaren Modus
ein. Änderungen am Quellcode sind sofort wirksam. Wählt in eurer IDE den
Python-Interpreter aus `.venv` und aktiviert die Umgebung in jedem neuen Terminal.

## Implementierung und Tests

Ergänzt `sort` und `estimated_io_cost` in
[`src/exercise2/tpmms.py`](src/exercise2/tpmms.py). Eure Implementierung muss
mit den übrigen vorgegebenen Dateien unverändert funktionieren.

```bash
python -m pytest tests/framework
python -m pytest tests/test_tpmms.py
```

Die Framework-Tests sollten nach der Einrichtung bestehen. Die TPMMS-Tests
melden zunächst `NotImplementedError`, bis ihr die Methoden implementiert habt.
Mit `python -m pytest` führt ihr alle Tests aus. Beispieldaten liegen in
[`tests/resources/exercise2/`](tests/resources/exercise2/). Ihr könnt eigene
Tests ergänzen. Für die Bewertung werden weitere Eingaben verwendet.

## Beispiel ausführen

Mit `python -m exercise2` seht ihr die Eingaberelation und die anfangs leere
Ausgaberelation. Nach der Implementierung könnt ihr die Sortierung mit den
Beispieldaten oder einer eigenen CSV-Datei ausprobieren.

```bash
python -m exercise2 --sort
python -m exercise2 --sort --sort-column 2
python -m exercise2 data/input.csv --sort
```

Für den letzten Befehl legt ihr eine CSV-Datei mit einer Ganzzahl-, einer
Text- und einer Gleitkommaspalte unter `data/input.csv` ab.

## Projektstruktur

| Pfad | Inhalt |
| --- | --- |
| `src/exercise2/` | TPMMS-Aufgabe, Sortierschnittstelle und Beispielprogramm |
| `src/dbs2/dbms/` | DBMS-Framework und Hilfsfunktionen |
| `tests/` | Framework-Tests, TPMMS-Tests und Beispieldaten |
| `data/` | Eigene lokale Datendateien, die Git ignoriert |

## Abgabe bis Mittwoch, 25.11.2026, 23:59 Uhr

1. Pusht die fertige Implementierung in euer **privates Gruppenrepository**.
   Wenn ihr eigene Tests geschrieben habt, nehmt sie ebenfalls in den Commit auf.

   ```bash
   git add src/exercise2/tpmms.py tests/
   git commit -m "Implement TPMMS"
   git push
   ```

2. Prüft, dass ihr die Einladung an **`sedirmohammed`** mit mindestens
   Leserechten fristgerecht versendet habt.
3. Gebt im [Moodle-Kurs](https://moodle.hpi.de/course/view.php?id=1214) ein
   **PDF** mit euren Antworten auf die Quizfragen und dem **Link zum privaten
   Gruppenrepository** ab. Für die Korrektur sind sowohl der Link im PDF als
   auch die Einladung auf GitHub erforderlich.
