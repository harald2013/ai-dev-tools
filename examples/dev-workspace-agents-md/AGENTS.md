# AGENTS.md

Dieses Verzeichnis enthält normale Git-Checkouts (plain clones), in denen AI
Coding Agents arbeiten:

- `brain/`
- `nrg/`
- `agent-tools/`
- `ai-dev-tools/`

Jedes Repo hat einen eigenen Top-Level-Ordner. Darin liegt pro Auftrag
(Ticket) ein eigener, vollständiger Checkout, isoliert von anderen laufenden
Aufträgen — kein bare Repo, keine Worktrees, kein geteilter Object-Store.

## Referenz-Checkout

Pro Repo existiert zusätzlich ein dauerhafter Checkout des Default-Branch
(`<repo>/development` bzw. `<repo>/main` für `agent-tools`), benannt nach dem
Branch. Er dient zum schnellen Nachschauen ohne Ticket-Bezug und wird bei
Bedarf gepullt (`git pull`), aber nicht für eigene Entwicklung verwendet.

Ausnahme `ai-dev-tools`: siehe unten, hier gibt es nur den einen
`main/`-Checkout, der zugleich Referenz- und Arbeitscheckout ist.

## Workflow

1. **Checkout anlegen**

   Für Ticket `NRG-123` (Timeout-Fix) im Repo `nrg`:

   ```bash
   cd ~/dev
   git clone git@github.com:harald2013/nrg.git nrg/NRG-123-fix-timeout
   cd nrg/NRG-123-fix-timeout
   git checkout -b NRG-123-fix-timeout origin/development
   ```

   - `<kurzname>` ist ein kurzer, sprechender Bezeichner (2-4 Wörter,
     kebab-case) für den Auftrag, z. B. `fix-timeout`, `add-login-flow`.
   - Branch-Name = Ordnername (`<ticket>-<kurzname>`), damit Checkout, Branch
     und PR eindeutig zuordenbar bleiben.
   - Basis ist `development`, falls nicht anders angegeben. Ausnahme:
     `agent-tools` verwendet direkt `main`.
   - Existiert der Branch bereits (z. B. Fortsetzung eines Auftrags), direkt
     auschecken statt neu anzulegen:

     ```bash
     git clone git@github.com:harald2013/nrg.git nrg/NRG-123-fix-timeout
     cd nrg/NRG-123-fix-timeout
     git checkout NRG-123-fix-timeout
     ```

2. **Arbeiten & Testen**

   Im Checkout implementieren, committen und testen:

   ```bash
   cd ~/dev/nrg/NRG-123-fix-timeout
   # ... Änderungen, Tests ...
   git add -A
   git commit -m "..."
   ```

3. **Push**

   ```bash
   git push -u origin NRG-123-fix-timeout
   ```

4. **Pull Request**

   Falls die Aufgabe einen Review/Merge über GitHub erfordert:

   ```bash
   gh pr create --fill
   ```

5. **Aufräumen**

   Nach Merge/Abschluss den Ordner einfach löschen — kein bare Repo, also
   auch kein `worktree remove`/`prune` nötig:

   ```bash
   rm -rf ~/dev/nrg/NRG-123-fix-timeout
   ```

## Ausnahme: ai-dev-tools

`ai-dev-tools` hat nur einen `main`-Branch und praktisch nie Ticket-Nummern.
Hier entfällt der Workflow oben komplett:

- **Kein Checkout pro Auftrag.** Es gibt nur `ai-dev-tools/main/`, ein
  einziger dauerhafter Checkout, in dem direkt gearbeitet wird.
- **Kein Feature-Branch, kein PR.** Änderungen werden direkt auf `main`
  committet und gepusht:

  ```bash
  cd ~/dev/ai-dev-tools/main
  # ... Änderungen, Tests ...
  git add -A
  git commit -m "..."
  git push
  ```

- Vor dem Start einer neuen Aufgabe `git pull`, um sicherzustellen, dass der
  Checkout aktuell ist (kein Nebeneinander mehrerer Checkouts, das das sonst
  automatisch abfängt).
- Commit-Messages sind sprechend statt ticket-referenziert (kein `NRG-123:`-
  Präfix o. ä.).
- Ticket-Status-Pflege (siehe unten) entfällt in der Regel, da es meist kein
  Ticket gibt. Existiert ausnahmsweise doch eines, gilt der Abschnitt normal.

## Ticket-Status

Der Agent soll den Status des Tickets (z. B. in Linear) im Rahmen der
Bearbeitung pflegen:

- **In Progress** (und vergleichbare Start-Status wie "In Review" bei PR):
  darf der Agent selbst setzen, sobald die Arbeit bzw. der Review beginnt.
- **Done** (oder anderer Abschluss-Status): nur nach Rückfrage beim User.

## Konventionen

### GitHub CLI

`gh` ist verfügbar und authentifiziert. Nutze es für GitHub-Operationen, die
nicht über einen MCP/Connector abgedeckt sind, z. B. Default-Branch prüfen oder
setzen, Branch Protection prüfen, PRs anlegen und GitHub-Actions-Checks/Logs
untersuchen.

Wichtig: GitHub-Operationen benötigen in der Agent-Sandbox Netzwerkzugriff.
Wenn `gh auth status`, `git push`, `git ls-remote`, `gh pr create` oder ähnliche
GitHub-Befehle mit DNS-/Netzwerkfehlern oder scheinbar ungültiger Authentifizierung
scheitern, den gleichen Befehl mit Netzwerk-Eskalation erneut ausführen, bevor
der User zur Re-Authentifizierung aufgefordert wird.

- **Name = Ticketnummer + kurzer sprechender Name** (z. B. `NRG-123-fix-timeout`,
  `BRAIN-45-add-login-flow`), einheitlich für Ordner und Branch, damit
  Checkout, Branch und PR eindeutig einem Auftrag zuordenbar sind.
- **Ein Checkout pro Ticket**, mehrere Agents/Aufträge können so parallel an
  verschiedenen Tickets arbeiten, ohne sich im Arbeitsverzeichnis zu stören.
- Basis-Branch ist `development`, sofern der Auftrag nichts anderes vorgibt.
  Ausnahme: `agent-tools` verwendet direkt `main`.
- `~/dev` selbst ist kein Git-Repo, sondern nur der Container für die
  Repo-Ordner und deren Ticket-Checkouts.
- `ai-dev-tools` folgt keiner der obigen Konventionen — siehe
  [Ausnahme: ai-dev-tools](#ausnahme-ai-dev-tools).

## Repository-Struktur

```
~/dev/
├── agent-tools/
│   ├── main/                        # Referenz-Checkout, Default-Branch
│   └── <ticket>-<kurzname>/         # aktive Ticket-Checkouts
├── ai-dev-tools/
│   └── main/                        # einziger Checkout, direkt bearbeitet
├── brain/
│   ├── development/                 # Referenz-Checkout, Default-Branch
│   └── <ticket>-<kurzname>/
└── nrg/
    ├── development/                 # Referenz-Checkout, Default-Branch
    └── <ticket>-<kurzname>/
```
