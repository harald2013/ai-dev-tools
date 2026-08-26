# AGENTS.md — OpenHands Setup Governance

Diese Datei ist die verbindliche Richtlinie für alles unterhalb von `./openhands/`.
Sie beschreibt Architektur, IaC-Dateistruktur und Verhaltensregeln für jeden
Agenten (Mensch oder KI), der dieses Setup aufbaut, betreibt oder ändert.

> **Geltungsbereich:** Ausschließlich `./openhands/`. Nichts außerhalb dieses
> Verzeichnisses darf durch dieses Setup verändert werden (keine globalen
> Docker-Netzwerke, keine Host-weiten Volumes, keine Systemd-Units).

---

## 0. Zuerst lesen: Wissensstand vs. Realität (kritisch!)

Das trainierte Wissen über "OpenHands" bezieht sich mit hoher Wahrscheinlichkeit
auf die **klassische V0-Architektur** (`config.toml`, `SANDBOX_BASE_CONTAINER_IMAGE`,
Docker-Socket-Mount für Runtime-Sandboxen pro Konversation). Das Projekt hat sich
seither zu **Agent Canvas** weiterentwickelt, und dieses Repository deployt
bewusst die einfache Single-Container-Variante davon. Wesentliche Unterschiede,
Stand der Recherche (Primärquelle `https://docs.openhands.dev/`, Sekundärquelle
`https://github.com/OpenHands/OpenHands`, Architektur-Issue
[OpenHands/OpenHands#15630](https://github.com/OpenHands/OpenHands/issues/15630)):

| Klassisches Wissen (potenziell veraltet)                     | Aktueller Stand in diesem Setup |
|----------------------------------------------------------------|----------------------------------|
| Konfiguration über `config.toml`, Sektion `[mcp]` in TOML      | Konfiguration über `~/.openhands/settings.json` + `~/.openhands/agent-profiles/*.json` (JSON, Schema-versioniert). `config.toml` existiert nur noch in der Legacy-/OSS-App, **nicht** in Agent Canvas. |
| Runtime-Sandbox pro Konversation via Docker-Socket-Mount (`SANDBOX_BASE_CONTAINER_IMAGE`) | Der Self-Hosted-Single-Container (`ghcr.io/openhands/agent-canvas:latest`) bündelt Canvas-UI, Agent Server und Automation Server **in einem Prozess**. **Keine Per-Konversation-Isolation** — alle Konversationen teilen sich Prozess, Dateisystem und `/workspace`. Das ist laut Issue #15630 ein bekanntes, noch offenes Limit, kein Bug in unserer Config. |
| Custom-Sandbox über `Dockerfile` + `docker.sock`-Mount          | Custom-Tools im Ausführungs-Image sind nur relevant, wenn man vom Single-Container-Modus auf ein Remote-/Cloud-Backend mit `AGENT_SERVER_IMAGE_REPOSITORY` / `AGENT_SERVER_IMAGE_TAG` umsteigt (siehe [§6](#6-optionale-erweiterung-custom-agent-server-image)). Im Default-Setup dieses Repos gibt es **keinen** separaten Sandbox-Container. |
| MCP-Server in `[mcp].stdio_servers` / `.sse_servers` (TOML)     | MCP-Server werden im Feld `agent_settings.mcp_config` des jeweiligen Agent-Profils (JSON) bzw. über die UI unter `Settings → MCP` gepflegt. |

**Konsequenz:** Wo diese Datei von einer "sauberen" Control-Plane/Runtime-Trennung
mit eigenem Sandbox-Dockerfile spricht, ist das ein **optionaler Erweiterungspfad**,
kein Ist-Zustand. Der Ist-Zustand ist ein bewusst einfacher, nicht isolierter
Single-Container-Betrieb für Trusted-Environment-Nutzung (lokale Entwicklungs-
maschine, ein Nutzer). Jeder Agent, der das ändern will, muss zuerst gegen
`docs.openhands.dev` verifizieren, dass sich daran nichts geändert hat (siehe
[§7](#7-regeln-für-künftige-ki-agenten)).

---

## 1. Mission & Architekturprinzip

**Ziel:** Ein reproduzierbares, versioniertes, headless-fähiges OpenHands-
Agent-Canvas-Setup, das mit einem einzigen Befehl — `docker compose -f
openhands/compose.yml up -d` — auf jedem Zielsystem hochfährt, ohne manuelle
UI-Klicks, ohne Host-seitige Einmal-Konfiguration und ohne Wrapper-Skripte.
Plain Compose-Befehle *sind* hier bereits das Ein-Befehl-Interface; ein
zusätzliches `up.sh`/`down.sh` würde nur eine zweite, redundante Quelle der
Wahrheit neben `compose.yml` schaffen.

**Komponentenmodell** (gemäß aktueller Doku):

- **Agent Canvas (Client/UI):** Browser-App. Rendert Zustand, sendet Requests
  an Backend-Services. Stellt selbst **keine** Isolation/Runtime bereit.
- **Agent Server:** Führt die eigentliche Konversation/den Agenten-Loop aus
  (Tools, LLM-Calls, Dateisystemzugriff auf `/workspace` bzw. `/projects`).
- **Automation Server:** Besitzt den Lifecycle von geplanten/Event-getriggerten
  Läufen (Cron-artige Agentenläufe, Headless-Automationen).
- In diesem Repo laufen alle drei Rollen **in einem Container**
  (`agent-canvas`-Image, "all-in-one local stack"). Das ist die bewusste
  Trennung von *Zuständigkeit* (Control-Plane-Konzept bleibt in der Doku
  bestehen), nicht von *Prozessen* — für echte Prozess-/Container-Isolation
  siehe [§6](#6-optionale-erweiterung-custom-agent-server-image).

**Sicherheitsmodell:** Der Container läuft mit `OPENHANDS_UID`/`OPENHANDS_GID`
(Default `1000:1000`), damit unter `.openhands/` erzeugte Dateien vom Host-User
lesbar/committable bleiben. Das ist **kein** Sandboxing der Agentenaktionen
selbst — der Agent hat innerhalb des Containers vollen Zugriff auf die
gemounteten Verzeichnisse (`/projects`, `/workspace`). Secrets, an die der
Agent nicht herandarf, gehören **nicht** in gemountete Pfade.

**Deklaratives Secrets-Management:** Alle Umgebungsvariablen, die host-
spezifisch sind (UID/GID, API-Keys, Ports), werden über `./openhands/.env`
(lokal, gitignored) auf Basis von `./openhands/.env.example` (versioniert,
committed, ohne echte Werte) bereitgestellt. Runtime-Secrets, die die
Anwendung selbst erzeugt (`api-key.txt`, `secret-key.txt`, `auth/`), werden
ausschließlich unter `.openhands/` abgelegt und sind über `.gitignore`
ausgeschlossen — niemals hart in `compose.yml` kodieren.

---

## 2. IaC-Dateistruktur unter `./openhands/`

```
openhands/
├── AGENTS.md              # diese Datei
├── compose.yml            # Service-Definition (Single Source of Truth)
├── .env.example            # versioniertes Template für Host-Overrides
├── .env                     # NICHT committed — echte UID/GID/Secrets
├── .gitignore
├── .openhands/              # Bind-Mount-Ziel: Konfiguration & Runtime-State
│   ├── settings.json         # aktives Profil, LLM-/Conversation-Settings
│   ├── agent-profiles/       # ein JSON pro Agent-Profil (siehe §4)
│   │   └── *.json
│   ├── microagents/          # optional: globale Skills (nicht repo-gebunden)
│   ├── auth/                  # gitignored — Session-/OAuth-State
│   ├── cache/                  # gitignored — Runtime-Cache
│   └── secrets.json            # gitignored — niemals committen
└── sandbox/                 # OPTIONAL, nur bei Umstieg auf Remote-Backend
    └── Dockerfile            # Custom Agent-Server-Image, siehe §6
```

Regeln zu dieser Struktur:

- `compose.yml` (nicht `docker-compose.yml`) ist der kanonische Dateiname in
  diesem Repo — moderner Compose-Spec-Standardname. Keine zweite Compose-Datei
  parallel pflegen.
- **Kein `scripts/`-Verzeichnis.** Start/Stop/Health-Check laufen ausschließlich
  über plain `docker compose`-Befehle (siehe §3) — sie duplizieren nichts, was
  `compose.yml` nicht schon deklariert. Ein Skript braucht einen konkreten,
  benannten Bedarf (z. B. WSL-IP-Ausgabe, CI-Health-Gate), sonst bleibt es bei
  den Compose-Befehlen.
- **Kein `config.toml`.** Falls eine zukünftige Doku-Version wieder TOML-Config
  für Agent Canvas einführt, muss das hier zuerst gegen `docs.openhands.dev`
  verifiziert und diese Sektion aktualisiert werden, bevor eine solche Datei
  angelegt wird.
- `sandbox/Dockerfile` existiert nur, sobald tatsächlich ein Custom-Execution-
  Image gebraucht wird (siehe §6). Ein leeres `sandbox/`-Verzeichnis "auf
  Vorrat" wird nicht angelegt (YAGNI) — bis dahin ist dieser Abschnitt reine
  Spezifikation für den Tag, an dem es gebraucht wird.

---

## 3. Betrieb: nur `docker compose`, keine Wrapper

Standard-Befehle, direkt vom Repo-Root oder aus `./openhands/` — das ist die
vollständige Betriebsschnittstelle, es gibt keine weiteren Skripte:

```bash
# Start (idempotent, wartet bis Health-Check grün ist)
docker compose -f openhands/compose.yml up -d --wait

# Status / Logs
docker compose -f openhands/compose.yml ps
docker compose -f openhands/compose.yml logs -f

# Stop
docker compose -f openhands/compose.yml down
```

Host-UID/GID abweichend von `1000:1000`: `openhands/.env` aus
`openhands/.env.example` anlegen (siehe dortiger `sed`-Einzeiler) — danach
liest `docker compose` sie automatisch, kein zusätzlicher Export nötig.

---

## 4. `compose.yml` — Referenz (Ist-Zustand)

```yaml
name: openhands

x-openhands-image: &openhands-image ghcr.io/openhands/agent-canvas:latest

x-openhands-bind-mounts: &openhands-bind-mounts
  - ./.openhands:/home/openhands/.openhands
  - ../openhandswork/projects:/projects
  - ../openhandswork/workspace:/workspace

services:
  agent-canvas:
    image: *openhands-image
    user: "0"
    ports:
      - "${OPENHANDS_PORT:-18040}:8000"
    volumes: *openhands-bind-mounts
    environment:
      PORT: "8000"
      HOME: /home/openhands
      OPENHANDS_UID: "${OPENHANDS_UID:-1000}"
      OPENHANDS_GID: "${OPENHANDS_GID:-1000}"
    entrypoint: ["tini", "--", "sh", "-c"]
    command:
      - |
        chmod 755 /home/openhands
        chown -R "$$OPENHANDS_UID:$$OPENHANDS_GID" /home/openhands/.openhands /projects /workspace
        exec setpriv --reuid="$$OPENHANDS_UID" --regid="$$OPENHANDS_GID" --clear-groups -- /opt/agent-canvas/entrypoint.sh
    restart: unless-stopped
```

Anmerkungen:

- Der Container startet initial als `root` (`user: "0"`), um `chown` auf die
  Bind-Mounts anzuwenden, und wechselt danach per `setpriv` auf
  `OPENHANDS_UID:OPENHANDS_GID`. Das ist der offizielle empfohlene Weg, damit
  Bind-Mount-Inhalte vom Host-User schreib-/lesbar bleiben, **kein**
  Privilege-Escalation-Risiko, solange der Container selbst vertrauenswürdig
  bleibt.
- Zusätzliche relevante Env-Vars (bei Bedarf ergänzen, nicht hart einbrennen):
  `LOCAL_BACKEND_API_KEY` (Pflicht nur im `--public`-Modus, sonst Auto-Generierung),
  `OH_SECRET_KEY` (schützt gespeicherte Settings/Secrets),
  `OH_AGENT_SERVER_VERSION` (pinnt eine bestimmte Agent-Server-Version).
- `latest` als Image-Tag ist für ein reproduzierbares Setup grundsätzlich ein
  Zielkonflikt (IaC-Prinzip "versioniert"). Vor einem Pin auf eine konkrete
  Version die aktuell unterstützten Tags auf `ghcr.io/openhands/agent-canvas`
  bzw. in den Release-Notes von `docs.openhands.dev` prüfen — nicht blind
  einen alten Tag aus Trainingsdaten eintragen.

---

## 5. Konfiguration: `settings.json` & `agent-profiles/*.json`

Agent Canvas verwendet **kein** `config.toml`. Konfiguration ist JSON,
Schema-versioniert (`schema_version`-Felder), und liegt unter
`.openhands/settings.json` (aktives Profil + globale Conversation-Settings)
sowie `.openhands/agent-profiles/<name>.json` (ein Profil = LLM, Agent-Kind,
Condenser, Verification, MCP).

Minimal-Template für ein neues Agent-Profil:

```json
{
  "schema_version": 2,
  "name": "example-profile",
  "agent_kind": "openhands",
  "agent": "CodeActAgent",
  "llm": {
    "model": "<provider>/<model-id>",
    "api_key": null,
    "timeout": 300,
    "caching_prompt": true
  },
  "mcp_config": {},
  "condenser": {
    "enabled": true,
    "condenser_kind": "llm_summarizing"
  }
}
```

### MCP-Server konfigurieren

MCP wird **nicht** über TOML gepflegt, sondern entweder über die UI
(`Settings → MCP`) oder deklarativ im Feld `mcp_config` eines Agent-Profils.
Das dokumentierte JSON-Schema dafür (SDK-Format, `mcpServers`-Map):

```json
{
  "mcp_config": {
    "mcpServers": {
      "fetch": {
        "command": "uvx",
        "args": ["mcp-server-fetch"]
      },
      "remote-example": {
        "url": "https://api.example.com/mcp",
        "transport": "http",
        "auth": "oauth"
      }
    }
  }
}
```

> Dieses Feld ist im Ist-Zustand des Repos leer (`"mcp_config": {}`). Vor dem
> ersten produktiven Einsatz eines MCP-Servers das exakte Schema gegen
> `https://docs.openhands.dev/openhands/usage/settings/mcp-settings`
> gegenprüfen — es kann sich zwischen Agent-Canvas-Versionen ändern.

### Secrets in Profilen

`api_key`/`aws_secret_access_key`/etc. **niemals** als Klartext in ein
committed `agent-profiles/*.json` schreiben. Diese Dateien liegen unter
`.openhands/`, das per `.gitignore` teilweise ausgeschlossen ist — Profile
mit echten Keys gehören zu den lokalen, nicht committeten Artefakten, oder
die Keys werden über Env-Var-Referenzen/Secret-Store bezogen, sobald die
Doku dafür einen deklarativen Mechanismus vorsieht (bei nächster Recherche
prüfen, ob es einen `${ENV_VAR}`-Interpolationsmechanismus in `settings.json`
gibt).

---

## 6. Projekt-/Repo-Integration

### Skills / Microagents (repo-spezifische Regeln)

Für **einzelne Projekte**, die der Agent unter `/projects` bearbeitet, gilt
die OpenHands-eigene Konvention (unabhängig von diesem `openhands/`-Verzeichnis,
lebt im jeweiligen Zielrepo):

```
<ziel-repo>/
└── .openhands/
    ├── skills/          # V1, bevorzugt
    │   └── repo.md
    └── microagents/     # V0/Legacy — weiterhin unterstützt, nicht neu anlegen
        └── repo.md
```

- `AGENTS.md` im Zielrepo-Root: kurze, repo-weite Konventionen (wie diese
  Datei hier — als Vorbild für Struktur, nicht als Kopiervorlage für Inhalt).
- `SKILL.md`: fokussiertes Wissen, das nur für bestimmte Aufgaben geladen wird.
- OpenHands erkennt zusätzlich `CLAUDE.md`/`GEMINI.md` als modellspezifischen
  Repo-Kontext.
- Neue Skills bevorzugt unter `.agents/skills/` anlegen (aktuellste Konvention,
  vor Verwendung gegen die Skills-Übersicht in der Doku gegenprüfen — dieser
  Pfad war zum Zeitpunkt der Recherche im Wandel).

### Volume-/Workspace-Strategie

- `../openhandswork/projects` → `/projects`: Container für alle Git-Checkouts,
  die der Agent bearbeiten soll. Liegt bewusst **außerhalb** des versionierten
  `openhands/`-Verzeichnisses (Arbeitsdaten, kein IaC-Artefakt) — relativ zu
  `compose.yml`, damit jeder Checkout-Pfad funktioniert.
- `../openhandswork/workspace` → `/workspace`: Scratch-/Ausführungsverzeichnis
  des Agenten selbst.
- Beide Verzeichnisse werden von Docker automatisch angelegt und beim Start
  auf `OPENHANDS_UID:OPENHANDS_GID` gechownt — nichts manuell auf dem Host
  vorbereiten.
- Git-Worktrees für parallele Agentenläufe: als Unterverzeichnisse innerhalb
  von `../openhandswork/projects/<repo>/` anlegen, nicht als eigene Top-Level-
  Mounts — sonst muss `compose.yml` bei jedem neuen Worktree angefasst werden,
  was dem "ein Befehl reicht"-Prinzip widerspricht.

---

## 7. Optionale Erweiterung: Custom Agent-Server-Image

Nur relevant, wenn (a) der Agent Build-Tools/SDKs braucht, die im Default-
Image (`ghcr.io/openhands/agent-server:<release>-python`, enthält Python +
Node.js) fehlen, **und** (b) auf ein Setup mit echter Per-Konversation-
Isolation umgestiegen wird (Remote-/Cloud-Backend statt Single-Container-
Agent-Canvas — siehe [§0](#0-zuerst-lesen-wissensstand-vs-realität-kritisch)).
Im aktuellen Single-Container-Betrieb dieses Repos greift das **nicht**.

Vorgehen laut `docs.openhands.dev/openhands/usage/advanced/custom-sandbox-guide`:

`openhands/sandbox/Dockerfile.base` (eigene Zusatz-Tools):

```dockerfile
FROM nikolaik/python-nodejs:python3.12-nodejs22
RUN apt-get update && apt-get install -y ruby
```

Build der Basis:

```bash
docker build -t my-org/openhands-sandbox-base:latest -f openhands/sandbox/Dockerfile.base openhands/sandbox
```

Agent-Server-Image darauf aufbauen (aus einem separaten Checkout des
OpenHands-SDK-Repos, `--target binary` entspricht dem Standard-Image mit
VSCode/VNC; `binary-minimal` für ein schlankeres Image ohne beides):

```bash
docker buildx build \
  --build-arg BASE_IMAGE=my-org/openhands-sandbox-base:latest \
  --target binary \
  -f openhands-agent-server/openhands/agent_server/docker/Dockerfile \
  -t ghcr.io/my-org/openhands-sandbox:custom \
  --load .
```

Anbindung (beide Variablen sind zusammen erforderlich):

```yaml
environment:
  - AGENT_SERVER_IMAGE_REPOSITORY=ghcr.io/my-org/openhands-sandbox
  - AGENT_SERVER_IMAGE_TAG=custom
```

Vor jeder Umsetzung dieses Pfads: gegen die aktuelle Doku-Seite prüfen, ob
sich Build-Target-Namen, Dockerfile-Pfad im SDK-Repo oder die Env-Var-Namen
geändert haben.

---

## 8. Headless-/CLI-Agentenläufe

Für CI/CD- oder Batch-Nutzung ohne UI stehen laut
`docs.openhands.dev/openhands/usage/cli/headless` und dem Agent-Canvas-Repo
grundsätzlich zwei Wege offen — **beide vor Nutzung verbindlich gegen die
aktuelle Doku verifizieren**, da hier zum Zeitpunkt der Recherche zwei
unterschiedliche Tools kursieren, die leicht verwechselt werden. Ein eigenes
Skript dafür wird bewusst nicht vorab angelegt (§2/§3) — erst bei konkretem
Bedarf, und dann direkt als plain Befehl in der jeweiligen CI-Pipeline bzw.
als einzelner dokumentierter `curl`/API-Aufruf hier ergänzen:

1. **Backend-only Agent Canvas:** `agent-canvas --backend-only` startet Agent
   Server + Automation Server ohne Frontend. Für unseren Docker-Betrieb
   bedeutet das: Der laufende `agent-canvas`-Container exponiert eine REST-API
   (Port 8000/`OPENHANDS_PORT`), gegen die Konversationen per HTTP angestoßen
   werden können (`LOCAL_BACKEND_API_KEY` als Auth). Das ist der Weg, der zu
   diesem Setup passt, da der Container ohnehin läuft.
2. **Separates `openhands`/`OpenHands-CLI`-Paket** (`pip install openhands`,
   Aufruf `openhands --headless -t "<task>"`): ein eigenständiges CLI-Tool,
   **nicht** identisch mit dem Agent-Canvas-Container dieses Setups. Nur
   relevant, falls bewusst zusätzlich zum Container ein separates, lokal
   installiertes CLI genutzt werden soll — dann als eigener, klar benannter
   Schritt dokumentieren, nicht mit Weg (1) vermischen.

---

## 9. Regeln für künftige KI-Agenten

1. **Doku-Abgleich vor jeder Änderung.** Vor jeder Modifikation an Architektur,
   Image-Tags, CLI-Flags, Env-Vars oder Config-Schema: live gegen
   `https://docs.openhands.dev/` (primär) und
   `https://github.com/OpenHands/OpenHands` (sekundär) verifizieren. Internes
   Trainingswissen zu OpenHands gilt als potenziell veraltet — siehe die
   Diskrepanzen in [§0](#0-zuerst-lesen-wissensstand-vs-realität-kritisch), die
   bei der Erstellung dieser Datei entdeckt wurden. Wurde etwas neu verifiziert
   und weicht von dieser Datei ab: diese Datei im selben Commit korrigieren.
2. **Kein Verlassen von `./openhands/`.** Alle Artefakte (Compose, Configs,
   Dockerfiles) bleiben strikt innerhalb dieses Verzeichnisses. Keine globalen
   Docker-Objekte (Netzwerke, Volumes) ohne Namensraum-Präfix `openhands`.
3. **Kein manuelles Host-Workaround.** Kein manuelles `docker exec` zum
   Nachinstallieren von Tools im laufenden Container, kein manuelles Editieren
   von generiertem State unter `.openhands/cache`, `.openhands/storage` o.ä.
   Jede dauerhafte Änderung muss als Diff in `compose.yml`, `.env.example`,
   einem `agent-profiles/*.json`-Template oder `sandbox/Dockerfile` landen und
   committed werden. Wurde ein Workaround zur Diagnose genutzt: danach in IaC
   zurücküberführen, nicht stehen lassen.
4. **Secrets bleiben deklarativ.** Neue host-spezifische Werte immer zuerst in
   `.env.example` als Platzhalter dokumentieren, dann erst in der lokalen
   `.env` (nicht committed) mit echtem Wert befüllen. Niemals echte Secrets in
   `compose.yml` oder committeten `agent-profiles/*.json` hart kodieren.
5. **Kein Wrapper-Skript ohne Not.** Start/Stop/Status laufen über plain
   `docker compose`-Befehle (§3). Ein neues Skript unter `openhands/` braucht
   eine explizite Begründung (z. B. CI-Health-Gate, WSL-IP-Ausgabe) — sonst
   bleibt es bei den dokumentierten Compose-Befehlen. `docker compose -f
   openhands/compose.yml up -d --wait` muss nach jeder strukturellen Änderung
   weiterhin von einem sauberen Checkout aus ohne weitere manuelle Schritte
   zum laufenden System führen. Wird das gebrochen, ist die Änderung
   unvollständig.
6. **Diese Datei aktuell halten.** Strukturelle Änderungen (neue Services,
   geänderte Mounts, neues Config-Schema) erfordern ein Update dieser
   `AGENTS.md` im selben Commit — sie ist die einzige Quelle der Wahrheit für
   nachfolgende Agenten, nicht Commit-Historie oder Slack-Threads.
7. **Kein historischer Kontext in dieser Datei.** Siehe das repo-weite
   Dokumentationsprinzip in der [Root-`AGENTS.md`](../AGENTS.md) — gilt
   unverändert auch hier: nur Soll-/Ist-Zustand, keine Rückblicke auf
   entfernte/ersetzte Skripte, Configs etc.
