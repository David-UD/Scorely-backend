# RESULTADOS.md — Resultado de la Ejecución del PLAN

Ejecución completa del PLAN.md para la construcción del backend de **Scorely** (Django REST Framework + PostgreSQL + Docker).

**Fecha:** 09/09/2026 (última actualización: 11/09/2026 — iteraciones "Public GETs" y "Refactor modelo events")
**Estado global:** ✅ Completo — 14/14 fases + iteración seed + iteración "Public GETs" + iteración "Refactor modelo events".

---

## Resumen Ejecutivo

El plan se ejecutó en su totalidad. La base del proyecto está operativa:

- **14 de 14 fases completadas + iteración seed + iteración "Public GETs" + iteración "Refactor modelo events".**
- **90/90 tests pasando** contra PostgreSQL 15 real (Docker).
- `manage.py check` y `manage.py spectacular --validate` sin errores ni warnings.
- Imagen Docker `scorely-web` construida correctamente.
- PostgreSQL 15 healthy en contenedor.
- `seed_data` ampliado con datos demo completos (ver abajo).
- Endpoints de lectura de competiciones/etapas/eventos abiertos al público (sin JWT).

Pendiente por parte del usuario (por su solicitud): **ejecutar las migraciones y seed de forma manual**.

---

## Qué se Construyó

### Arquitectura

- Django 4.2 + DRF + PostgreSQL 15 + Docker Compose.
- Configuración por entorno: `config/settings/{base,development,production}.py` con python-decouple.
- Apps por dominio: `users`, `competitions`, `participants`, `events`, `scoring`, `rankings`.
- Servicios de negocio separados en `apps/*/services/`.

### Dominios y Modelos Principales

| Dominio | Modelos |
|---------|---------|
| Users | `User` (custom, email login), `CompetitionAdmin` |
| Competitions | `CompetitionType`, `Affiliation`, `Location`, `Competition`, `StatusCompetition` |
| Participants | `Athlete`, `Team`, `TeamMember`, `Competitor` (individual/team) |
| Events | `CompetitionCategory`, `EnabledCompetitionCategory`, `CompetitionStage`, `Event`, `EventCompetitor` |
| Scoring | `ScoringRule` (tabla de puntos por posición y competición) |

### Servicios de Negocio

| Servicio | Responsabilidad |
|----------|-----------------|
| `ResultParser` | Parsea resultados TIME / REPS / WEIGHT / DISTANCE / POINTS |
| `EventRankingService` | Ranking denso por evento según `Event.is_ascending` |
| `ScoringService` | Puntos por posición según ScoringRule |
| `CompetitionRankingService` | Clasificación general por edición + desempates |
| `FinalQualificationService` | Selección de top-N para la fase final |

### API REST (JWT)

- Auth: `POST /api/v1/auth/token/`, `POST /api/v1/auth/token/refresh/`.
- CRUD completo por recurso bajo `/api/v1/`.
- Lectura pública de competiciones, etapas y eventos (`IsAuthenticatedOrReadOnly`).
- Leaderboard público: `/api/v1/leaderboards/competition/<id>/qualifier/` y `/final/` (`AllowAny`).
- Docs: `/api/schema/`, `/api/docs/` (Swagger), `/api/redoc/`.

### Seguridad

- Autenticación JWT (Bearer) con `simplejwt`.
- Permisos por rol: `IsSuperAdmin`, `IsEditionAdmin`.
- Endpoints de lectura públicos: `CompetitionViewSet`, `CompetitionStageViewSet`, `EventViewSet` (`IsAuthenticatedOrReadOnly`), `LeaderboardViewSet` (`AllowAny`).
- Escrituras protegidas por JWT (mismo comportamiento anterior).
- CORS configurado para `http://localhost:3000`.

### Datos Demo (`seed_data`)

El comando `manage.py seed_data` genera datos completos de demostración:

| Tipo | Cantidad | Detalle |
|------|----------|---------|
| Afiliaciones | 6 | 4 CrossFit + 2 HYROX |
| Ubicaciones | 4 | Box Centro, Norte, Sur, Este |
| Competiciones | 4 | 2 CrossFit (Open 2026, Showdown) + 2 HYROX (Madrid, Barcelona) |
| Ediciones | 4 | 2026, todas PUBLISHED |
| Categorías habilitadas | 6 | Principiantes/Intermedios/RX Individual, Principiantes Mixto, Intermedios Duo, Relevos 4 |
| Etapas | 6 | Qualifier + Final por edición |
| Eventos | 11 | 5×CF-A + 5×CF-B + 1×HY-A + 1×HY-B |
| Scoring Rules | 40 | Tabla 10 posiciones × 4 ediciones (1→100, 2→94, ... 10→46) |
| Personas | 19 | Participantes variados |
| Equipos | 4 | 2 DUO (CF-A) + 2 RELAY (CF-B, 4 integrantes) |
| Competidores | 11 | 5 CF-A + 2 CF-B + 2 HY-A + 2 HY-B |
| EventCompetitors | 34 | Todos con resultado, event_rank (dense) y score calculado |

Idempotente: ejecutar 2 veces produce exactamente los mismos conteos.

---

## Resultados de Verificación

| Verificación | Resultado |
|--------------|-----------|
| `manage.py check` | ✅ 0 issues |
| `manage.py spectacular --validate` | ✅ Limpio |
| Suite de tests (pytest) | ✅ 90/90 passed |
| `docker compose config` | ✅ Válido |
| `docker build -t scorely-web .` | ✅ OK |

### Detalle de Tests

| Archivo | Cobertura |
|---------|-----------|
| `test_users.py` | Modelo User, roles, CompetitionEditionAdmin, serializer |
| `test_competitions.py` | Tipos, afiliaciones, locations, competición, edición, estados |
| `test_participants.py` | Personas, equipos, miembros, validación de Competitor |
| `test_events.py` | Categorías, stages (único qualifier), eventos, resultados |
| `test_scoring.py` | ScoringRule y ScoringService |
| `test_rankings.py` | ResultParser, EventRankingService, CompetitionRankingService, FinalQualificationService |
| `test_api.py` | Endpoints principales (auth, users, competitions, events, leaderboards) + permisos de lectura pública (11 tests) |
| `test_security.py` | JWT (obtain/refresh/expired/invalid), permisos por rol, CORS |
| `test_seed.py` | Conteo datos demo, idempotencia (2 ejecuciones), ranking calculado, categorías globales |

---

## Problemas Encontrados y Soluciones

| # | Problema | Solución |
|---|----------|----------|
| 1 | `No module named 'config'` (layout anidado `scorely/`) | Se movieron `config/`, `apps/`, `tests/` a la raíz del proyecto |
| 2 | `rest_framework_simplejwt.urls` no existe en simplejwt moderno | Rutas JWT definidas manualmente con `TokenObtainPairView`/`TokenRefreshView` |
| 3 | Admin errors E040 (autocomplete sin search_fields) | Se añadieron `search_fields` a CompetitionEnabledCategory, CompetitionStage, EventResultType, RankDirection, StatusEventCompetitor |
| 4 | NOT NULL al crear Competition/CompetitionEdition vía API | Serializers write con `PrimaryKeyRelatedField` + `get_serializer_class()` en viewsets |
| 5 | `EventRankingService` usaba atributo inexistente | Corregido a `event.competition_stage.competition_edition` |
| 6 | pytest: error `auth_group` no existe (sin migraciones locales) | `--nomigrations` en pytest.ini |
| 7 | Token expirado: `set_exp(lifetime=-1)` requería timedelta; se expiraba el refresh en vez del access | `timedelta(seconds=-1)` sobre el access token |
| 8 | Permisos con `request=None` en tests | `SimpleNamespace(user=...)` |
| 9 | `python:3.8.10-slim` (Debian buster EOL) fallaba en build | `python:3.11-slim` |
| 10 | `.env` con `DB_HOST=localhost` rompía el service web en Docker | `environment: {DB_HOST: db}` en docker-compose |
| 11 | drf-spectacular no derivaba schema de `LeaderboardViewSet` | `serializer_class`, `@extend_schema` + `OpenApiParameter`, `@extend_schema_field` |
| 12 | Test de "único qualifier por edición" fallaba | Se añadió la fixture `stage_qualifier` que crea el stage previo |
| 13 | Resultado "21:15" para evento tipo DISTANCE en seed_data | Cambiado a "5000"/"4850" (metros) — `RankDirection.DESC` |
| 14 | Test `test_seed.py` esperaba 16 personas | Corregido a 19 (7 CF-A + 8 CF-B + 4 HY) |
| 15 | `ScoringRule` importado desde módulo incorrecto en test_seed | Corregido a `apps.scoring.models` |
| 16 | Refactor modelo events del usuario (elimina `EventResultType`, `RankDirection`, `StatusEventCompetitor`) | Propagado a serializers, views, urls, admin, services, seed, fixtures y tests: `Event` con `workout`/`is_ascending`/`is_active`; `ResultParser` autodetecta tiempo vs numérico; ranking usa `Event.is_ascending`; `EventCompetitor` sin `status`; `EnabledCompetitionCategory.ordering` devuelto a `Meta` |

---

## Iteración "Refactor modelo events" (11/09/2026)

Cambio estructural en `apps/events/models.py` (hecho por el usuario): se eliminan `EventResultType`, `RankDirection` y `StatusEventCompetitor`; `Event` pasa a `workout` (TextField), `is_ascending`, `is_active`; `EventCompetitor` pierde `status`.

### Semántica de ranking adoptada

- `ResultParser.parse(result)`: si el resultado contiene `:` → se parsea como tiempo (`MM:SS`/`HH:MM:SS` → segundos); si no → numérico.
- `EventRankingService`: `reverse_sort = not event.is_ascending` (True → menor es mejor; False → mayor es mejor). Ya no filtra `status__code='VALID'`.
- `CompetitionRankingService`: ya no filtra `status__code='VALID'`.

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `apps/events/models.py` | (usuario) 3 modelos borrados; `Event` y `EventCompetitor` redefinidos; `ordering` de `EnabledCompetitionCategory` corregido a `Meta` |
| `apps/events/serializers.py` | Borrados 3 serializers; `EventSerializer` con `workout`/`is_ascending`/`is_active`; `EventCompetitorSerializer` sin `status` |
| `apps/events/views.py` | Borrados 3 viewsets read-only; `EventCompetitorViewSet.filterset_fields` sin `status` |
| `apps/events/urls.py` | Borradas rutas `event-result-types`, `rank-directions`, `status-event-competitors` |
| `apps/events/admin.py` | Borrados 3 admins; `EventAdmin`/`EventCompetitorAdmin` con campos nuevos |
| `apps/events/services/result_parser.py` | `parse(result)` con autodetección tiempo vs numérico |
| `apps/events/services/event_ranking_service.py` | Sin filtro de status; `reverse_sort = not event.is_ascending` |
| `apps/rankings/services/competition_ranking_service.py` | Sin filtro de status |
| `apps/users/management/commands/seed_data.py` | Sin catálogos de los 3 modelos; eventos con `workout`/`is_ascending`; `EventCompetitor` sin `status` |
| `tests/conftest.py` | Fixture `event` con `workout`/`is_ascending`; `event_desc` nuevo; borrados fixtures/imports de los 3 modelos |
| `tests/test_events.py` | `TestEventResultTypes` eliminado; tests adaptados |
| `tests/test_api.py` | Payload de `test_event_create_requires_auth` con `workout`/`is_ascending` |
| `tests/test_rankings.py` | `ResultParser.parse` sin tipo; sin `status`; `test_disqualified_not_ranked` eliminado; eventos con `workout`/`is_ascending` |
| `README.md`, `PROMPT.md` | Modelos, endpoints, sección de escore actualizados |
| `docs/db_modelo.svg` | Diagrama actualizado al modelo nuevo |

**Nota (usuario):** se generó la **migración pendiente** (ver "Despliegue / Pasos Siguientes").

---

## Despliegue / Pasos Siguientes (usuario)

1. **Migraciones manuales** (como se acordó):

   ```bash
   docker compose up -d db
   docker compose run --rm web python manage.py makemigrations
   docker compose run --rm web python manage.py migrate
   ```

   O desde el host:

   ```bash
   .venv\Scripts\python.exe manage.py makemigrations
   .venv\Scripts\python.exe manage.py migrate
   ```

2. **Seed opcional y superusuario:**

   ```bash
   docker compose run --rm web python manage.py seed_data
   docker compose run --rm web python manage.py createsuperuser
   ```

3. **Levantar la API:**

   ```bash
   docker compose up --build
   # Docs: http://localhost:8000/api/docs/
   ```

> Nota: si se ejecutan las migraciones desde el host, `.env` debe mantener `DB_HOST=localhost`. En Docker, `DB_HOST=db` se fuerza vía `environment`.

4. **Migración pendiente del refactor de events (11/09/2026)** — ejecutarla manualmente:

   ```bash
   .venv\Scripts\python.exe manage.py makemigrations events
   .venv\Scripts\python.exe manage.py migrate
   ```

   Cambios detectados: añade `workout`/`is_ascending`/`is_active` a `Event`, elimina `event_result_type`/`rank_direction`, elimina `status` de `EventCompetitor`, borra los modelos `EventResultType`, `RankDirection` y `StatusEventCompetitor`, y migra los `unique_together` a `UniqueConstraint`.

---

## Versiones

| Componente | Versión |
|------------|---------|
| Python (local) | 3.8.10 |
| Python (Docker) | 3.11 |
| Django | 4.2.30 |
| djangorestframework | 4.2.x |
| psycopg2-binary | 2.9.9 (por compatibilidad de wheels con Python 3.8 local) |
| PostgreSQL | 15 |
| pytest / pytest-django | 7.4.4 / 4.11.1 |