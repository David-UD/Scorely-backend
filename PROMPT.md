# Scorely — PROMPT para implementación de actualizaciones


# Parte I — Contexto del proyecto

## Rol

Eres **Scorely**, un backend developer especializado que implementa actualizaciones sobre la plataforma Scorely: sistema de gestión y publicación de resultados de competiciones deportivas (CrossFit y HYROX).

## Alcance del sistema

El backend comienza en el registro de participantes y termina en la publicación pública de leaderboards. **NO** gestiona horarios, heats, jueces ni logística de competición.

## Tech Stack (fijo)

| Componente | Tecnología |
|-----------|-----------|
| Lenguaje | Python 3.8+ (3.11 en Docker) |
| Framework | Django 4.2 LTS |
| API | Django REST Framework |
| Base de datos | PostgreSQL |
| Auth | djangorestframework-simplejwt |
| Filtering | django-filter |
| Docs | drf-spectacular |
| Testing | pytest + pytest-django |
| Contenedores | Docker + Docker Compose |

**Prohibido:** Supabase, otro ORM que no sea el de Django, otra BD que no sea PostgreSQL.

## Arquitectura

```
Scorely/
├── config/                 # settings (base/development/production), urls, wsgi, asgi
├── apps/
│   ├── users/              # User, Role, CompetitionEditionAdmin, permisos, seed_data
│   ├── competitions/       # CompetitionType, Affiliation, Location, Competition, CompetitionEdition
│   ├── participants/       # Person, Team, TeamMember, Competitor
│   ├── events/             # CompetitionCategory, EnabledCategory, Stage, Event, ResultType, RankDirection, EventCompetitor, StatusEventCompetitor
│   ├── scoring/            # ScoringRule, ScoringService
│   └── rankings/           # Leaderboard, ranking services
├── tests/                  # Suite de pytest
├── manage.py
├── Dockerfile
├── docker-compose.yml
├── pytest.ini
├── requirements.txt
├── Process.md              # Bitácora de fases (estado actual del proyecto)
└── RESULTADOS.md           # Resumen de resultados y problemas resueltos
```

**Regla:** toda la lógica de negocio vive en `services/`, nunca en `views/`.

## Variables de entorno

| Variable | Descripción |
|----------|-------------|
| `SECRET_KEY` | Clave secreta de Django (nunca versionar) |
| `DEBUG` | Modo debug |
| `ALLOWED_HOSTS` | Hosts permitidos |
| `DATABASE_URL` | URL de conexión PostgreSQL |
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | Credenciales BD |
| `DB_HOST` | `localhost` en local; `db` forzado en Docker |
| `DB_PORT` | Puerto de BD |
| `CORS_ALLOWED_ORIGINS` | Orígenes CORS permitidos |

**Regla:** nunca guardar credenciales en código. Nunca commitear `.env`.

## Comandos de verificación

```bash
python manage.py check --settings=config.settings.development
python manage.py spectacular --validate --settings=config.settings.development
python -m pytest tests --settings=config.settings.development
docker compose up --build
```

## Modelo de datos (resumen)

```
Competition
  └─▶ CompetitionEdition          UNIQUE(competition, year)
        └─▶ CompetitionStage      una QUALIFIER y una FINAL por edición
              └─▶ Event           UNIQUE(competition_stage, event_number)
                    └─▶ EventCompetitor   UNIQUE(competitor, event) / result + event_rank + score
                          └─▶ Final Score
                                └─▶ Leaderboard

Participantes:
Person ─┐
        ▼
  Competitor  (INDIVIDUAL usa person | TEAM usa team, nunca ambos)
        ▲
Team ── TeamMember (UNIQUE(team, person))
```

El motor de puntuación **siempre** trabaja con `Competitor`, sea individual o equipo.

## Sistema de puntuación (reglas intocables)

> **El resultado NO es la puntuación.**

```
Resultado → Posición (rank) → Puntos WOD (ScoringRule) → Puntaje Final → Leaderboard
```

- `Final Score = SUM(puntos de todos los eventos válidos)`.
- Empates con ranking deportivo denso: `1, 2, 2, 4` (nunca `1, 2, 3, 4`).
- Cada edición define su propia tabla `ScoringRule` (nunca asumir fórmula fija).
- La fase Final tiene ranking **independiente**; nunca sumar Qualifier + Final.
- Desempates permitidos: mayor puntaje → más 1ºs → más 2ºs → más 3ºs → mejor resultado último evento común → mantener empate. **Prohibidos:** ID, nombre, fecha de registro.

## Seguridad

| Requisito | Implementación |
|-----------|---------------|
| Autenticación | JWT via simplejwt (`/api/v1/auth/token/`, `/api/v1/auth/token/refresh/`) |
| Autorización | Permisos por edición (`apps/users/permissions.py`) |
| Secretos | Solo variables de entorno |
| CORS | Configurable |
| Leaderboards | Públicos (`AllowAny`) |

## Restricciones del proyecto

- No crear ramas.
- No realizar push ni subir a git (el agente no hace nada de git sin pedido explícito del usuario).
- **AVISAR al usuario para ejecutar las migraciones manualmente** (`makemigrations` / `migrate` / `seed_data` / `createsuperuser`). El agente no las ejecuta.
- Documentar avances en `Process.md` al iniciar y finalizar cada paso.
- No añadir comentarios al código salvo que se soliciten.

---

# Parte II — Plantilla de especificación de la actualización

## 1. Título

Seed de datos de prueba para visualización del API

## 2. Objetivo

Poblar la base de datos con datos de ejemplo (competencias, ediciones, categorías, eventos, competidores, resultados y puntuaciones) para visualizar el comportamiento del API y los leaderboards públicos.

## 3. Alcance

**Incluye (se debe implementar):**
- Ampliar el comando `seed_data` (`apps/users/management/commands/seed_data.py`) para crear todos los datos listados en la sección 9.
- Dejar el seed idempotente (re-ejecutable sin duplicar datos): usar `get_or_create` y valores conocidos.

**Excluye (NO tocar):**
- No modificar modelos, serializers, views ni services existentes.
- No cambiar la API ni la lógica de ranking/puntuación.
- No ejecutar `makemigrations`/`migrate`/`createsuperuser` (los corre el usuario).

## 4. Cambios en el modelo de datos

- NO hay cambios en el modelo.

## 5. Cambios en la API

- NO hay cambios en el API; solo se usa para visualizar los datos sembrados.

## 6. Cambios en lógica de negocio / servicios

- No cambia la lógica de negocio. Única modificación de código: nuevos datos en `seed_data`.

## 7. Cambios en Django Admin

- Sin cambios: todos los modelos ya están registrados. Se usa `createsuperuser` para acceder.

## 8. Cambios en documentación

- `Process.md`: registrar avances.
- `RESULTADOS.md`: registrar el resultado del seed y las verificaciones.
- `README.md`: opcional, mencionar los datos de ejemplo creados por `seed_data`.

## 9. Datos / seeds

Catalogos ya cubiertos por `seed_data` (roles, types, estados, result types, rank directions, categorías globales) — no repetir. Extender con:

**Affiliaciones ("box") — 6** (el modelo `Affiliation` no distingue tipo; los nombres indican el origen):

| Nombre | Ciudad |
|--------|--------|
| `[COMPLETAR nombre box crossfit]`… | `[COMPLETAR]` |
| Total: 4 relacionados a competencias CrossFit y 2 a HYROX | |

**Locations — 4** (obligatoria 1 por competencia): `[COMPLETAR nombre/sede dirección ciudad]`.

**Competencias — 4 (2 CROSSFIT + 2 HYROX)**, cada una con `affiliation` + `location`:

| Nº | Nombre | Type | Edición | Eventos QUALIFIER | Evento FINAL | Categorías habilitadas |
|----|--------|------|---------|-------------------|--------------|------------------------|
| 1 | `[COMPLETAR CrossFit A]` | CROSSFIT | año `[COMPLETAR]` | 3 | 1 | Principiantes (Ind), Intermedios (Ind), Principiantes Mixto (Eq 2) |
| 2 | `[COMPLETAR CrossFit B]` | CROSSFIT | año `[COMPLETAR]` | 4 | 1 | Relevos 4 (Eq 4) |
| 3 | `[COMPLETAR HYROX A]` | HYROX | año `[COMPLETAR]` | 1 | — | RX (Ind) |
| 4 | `[COMPLETAR HYROX B]` | HYROX | año `[COMPLETAR]` | 1 | — | RX (Ind) |

> Definido en esta revisión: cada edición tiene stage QUALIFIER (order 1, `qualification_count` según avance a final) y, para crossfit, stage FINAL (order 2) con 1 "WOD Final". Las 2 HYROX llevan 1 evento (en QUALIFIER) cada una. Los años y nombres quedan a elección del usuario → `[COMPLETAR]`.

**Categorías globales nuevas (CompetitionCategory)** — las de la plantilla actual (Individual Male/Female, Team Mixto 2-2, Master) se conservan; **agregar**:

| Nombre | min_members | max_members |
|--------|-------------|-------------|
| Principiantes Individual | 1 | 1 |
| Intermedios Individual | 1 | 1 |
| RX Individual | 1 | 1 |
| Principiantes Mixto | 2 | 2 |
| Intermedios Duo | 2 | 2 |
| Relevos 4 | 4 | 4 |

**Eventos por competencia** (indicar `event_result_type` + `rank_direction`):

| Competencia | Evento | Type | Direction |
|-------------|--------|------|-----------|
| CrossFit A QUALIFIER | `[COMPLETAR]` (WOD 1) | TIME | ASC |
| CrossFit A QUALIFIER | `[COMPLETAR]` (WOD 2) | REPS | DESC |
| CrossFit A QUALIFIER | `[COMPLETAR]` (WOD 3) | WEIGHT | DESC |
| CrossFit A FINAL | `[COMPLETAR]` WOD Final | TIME | ASC |
| CrossFit B QUALIFIER | 4 eventos (mismos tipos que A, 4.º DISTANCE/REPS `[COMPLETAR]`) | — | — |
| CrossFit B FINAL | WOD Final | TIME | ASC |
| HYROX A / B | HYROX Race | TIME | ASC |

**ScoringRule por edición** (puntuación por posición, misma en las 4 ediciones):

| Posición | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|----------|---|---|---|---|---|---|---|---|---|---|
| Puntos | 100 | 94 | 88 | 82 | 76 | 70 | 64 | 58 | 52 | 46 |

**Competidores + resultados** (necesarios para visualizar leaderboards):
- CrossFit A: 2 personas (Principiantes Ind), 1 persona (Intermedios Ind), 2 equipos de 2 (Principiantes Mixto).
- CrossFit B: 2 equipos de 4 integrantes (Relevos 4) con sus `TeamMember`.
- HYROX A/B: 2 personas (RX Ind) por competencia.
- `EventCompetitor` con `result` (string) y `status=VALID` por evento, para que el leaderboard muestre posiciones/scores. Las posiciones y scores se calculan (no se fijan).

## 10. Pruebas requeridas

| Test | Escenario | Resultado esperado |
|------|-----------|--------------------|
| Seed idempotente | Ejecutar `seed_data` dos veces | Sin duplicados (mismos conteos) |
| GET `/api/v1/competitions/` | Consultar lista | 4 competencias con sus tipos |
| GET `/api/v1/leaderboards/edition/{id}/qualifier/` | Edición CrossFit A | Leaderboard con scores y posiciones |
| GET `/api/v1/leaderboards/edition/{id}/final/` | Edición CrossFit A | Ranking independiente del qualifier |
| GET `/api/v1/leaderboards/edition/{id}/qualifier/` | Edición CrossFit B (Relevos 4) | Leading con equipos de 4 |

## 11. Criterios de aceptación

Checklist verificable al terminar:

- `python manage.py check` sin errores
- `python manage.py spectacular --validate` limpio
- Suite de pytest completa en verde
- `seed_data` ejecutado dos veces no duplica datos
- Existen 4 competencias (2 CROSSFIT, 2 HYROX), 6 affiliations, 4 locations
- Leaderboards (qualifier/final) responden HTTP 200 con datos

## 12. Observaciones / riesgos

- `Affiliation` no tiene campo de tipo: los "6 box (4 crossfit, 2 hyrox)" se modelan solo con el nombre; ajustar nombres con `[COMPLETAR]`.
- `Competition` exige `affiliation` y `location` obligatorios (`PROTECT`): crear SIEMPRE ambas por competencia.
- CRUD de eventos: `UNIQUE(stage, event_number)` — numerar secuencial.
- Sin `Competitor` + `EventCompetitor` no hay leaderboard visible; por eso se incluyen personas/equipos/resultados.
- Los equipos de 4 necesitan la categoría `Relevos 4` (4-4) habilitada en la edición correspondiente.

---

# Parte III — Flujo de trabajo del agente

1. **Leer antes de tocar:** revisar `Process.md`, `RESULTADOS.md` y los modelos, serializers, views y services existentes de las apps involucradas. No asumir convenciones: verificarlas en el código.
2. **Confirmar la especificación:** si la Parte II tiene ambigüedades, hacer preguntas al usuario antes de implementar.
3. **Implementar** siguiendo el estilo y patrones del código existente (ViewSets + Routers, lógica en `services/`, serializers read/write según el patrón actual).
4. **Actualizar/crear pruebas** en `tests/` y ejecutar la suite completa.
5. **Verificar** con los comandos de la Parte I (check, spectacular --validate, pytest).
6. **NO ejecutar** `makemigrations`, `migrate`, `seed_data` ni `createsuperuser`. Informar al usuario los comandos que debe correr manualmente.
7. **Documentar:** registrar avances y fases en `Process.md` y, si corresponde, actualizar `RESULTADOS.md` y demás piezas de la Parte II (sección 8).
8. **Reportar** un resumen final: qué se cambió, cómo se verificó y los pasos manuales pendientes del usuario.