# RESULTADOS.md — Resultado de la Ejecución del PLAN

Ejecución completa del PLAN.md para la construcción del backend de **Scorely** (Django REST Framework + PostgreSQL + Docker).

**Fecha:** 09/09/2026 (última actualización: 15/09/2026 — iteración "Refactor CompetitionStage → Event + phase", "Exponer `event_results`" y "Final global leaderboard")
**Estado global:** ✅ Completo — 14/14 fases + iteración seed + iteración "Public GETs" + iteración "Refactor modelo events" + iteración "CompetitionStage→Event.phase + event_results" + iteración "Final global leaderboard".

---

## Resumen Ejecutivo

El plan se ejecutó en su totalidad. La base del proyecto está operativa:

- **14 de 14 fases completadas + iteración seed + iteración "Public GETs" + iteración "Refactor modelo events" + iteración "CompetitionStage→Event.phase + `event_results`" + iteración "Final global leaderboard".**
- **119/119 tests pasando** (113 previos + 6 de la iteración "Final global leaderboard"). Tras añadir el no clasificado al seed demo: **120/120**.
- `manage.py check` y `manage.py spectacular --validate` sin errores ni warnings.
- Imagen Docker `scorely-web` construida correctamente.
- PostgreSQL 15 healthy en contenedor.
- `seed_data` ampliado con datos demo completos (ver abajo).
- Endpoints de lectura de competiciones/etapas/eventos abiertos al público (sin JWT).
- Leaderboard enriquecido con `event_results` (desglose por evento) y evento/con fase en el modelo (sin `CompetitionStage`).
- `/final/` es el leaderboard **global** (qualifier+final combinados): no clasificados con `null` en WODs finales (`score` suma global). `seed_data` crea registros en eventos FINAL solo para clasificados (top `finalist_slots` por categoría).

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
| Events | `CompetitionCategory`, `EnabledCompetitionCategory`, `Event` (FK `competition` + `phase` QUALIFIER/FINAL + `event_number` único por competición), `EventCompetitor` |
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
- Leaderboard público: `/api/v1/leaderboards/competition/<id>/qualifier/` (solo QUALIFIER) y `/final/` (global, qualifier+final) (`AllowAny`).
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
| Etapas | 0 — se eliminó `CompetitionStage`; `Event.phase` (QUALIFIER/FINAL) lo sustituye; `Competition.finalist_slots` (cf_a=2, cf_b=2, hy_a=0, hy_b=0) |
| Eventos | 11 | 5×CF-A + 5×CF-B + 1×HY-A + 1×HY-B (FINAL renumerados: cf_a→4, cf_b→5)
| Scoring Rules | 40 | Tabla 10 posiciones × 4 ediciones (1→100, 2→94, ... 10→46) |
| Personas | 20 | Participantes variados (incluye Daniel, 3º de "Principiantes Individual" de CF-A) |
| Equipos | 4 | 2 DUO (CF-A) + 2 RELAY (CF-B, 4 integrantes) |
| Competidores | 12 | 6 CF-A + 2 CF-B + 2 HY-A + 2 HY-B |
| EventCompetitors | 37 | Todos con resultado, event_rank (dense) y score calculado; DEMO-CFA-006 no clasifica y no tiene registro en el WOD Final |

Idempotente: ejecutar 2 veces produce exactamente los mismos conteos.

---

## Resultados de Verificación

| Verificación | Resultado |
|--------------|-----------|
| `manage.py check` | ✅ 0 issues |
| `manage.py spectacular --validate` | ✅ Limpio (schema incluye `EventResult` y `event_results`) |
| Suite de tests (pytest) | ✅ 120/120 passed |
| `docker compose config` | ✅ Válido |
| `docker build -t scorely-web .` | ✅ OK |

### Detalle de Tests

| Archivo | Cobertura |
|---------|-----------|
| `test_users.py` | Modelo User, roles, CompetitionEditionAdmin, serializer |
| `test_competitions.py` | Tipos, afiliaciones, locations, competición, edición, estados |
| `test_participants.py` | Personas, equipos, miembros, validación de Competitor |
| `test_events.py` | Categorías, eventos por competición/fase, unicidad de `event_number`, resultados |
| `test_scoring.py` | ScoringRule y ScoringService |
| `test_rankings.py` | ResultParser, EventRankingService, CompetitionRankingService (`event_results` + `calculate_overall_ranking`), FinalQualificationService |
| `test_api.py` | Endpoints principales (auth, users, competitions, events, leaderboards) + permisos de lectura pública + `event_results` en API + `/final/` global |
| `test_security.py` | JWT (obtain/refresh/expired/invalid), permisos por rol, CORS |
| `test_seed.py` | Conteo datos demo, idempotencia (2 ejecuciones), ranking calculado, categorías globales, FINAL solo para clasificados |

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
| 17 | Refactor `CompetitionStage` → `Event.competition + phase` (opción 1, sin migraciones): el código quedó roto (`ImportError`) a mitad del refactor del usuario | Completado el refactor: `Event.competition` FK + `Event.phase` + `UniqueConstraint(competition, event_number)`; eliminada ruta `competition-stages`; `seed_data` usa `finalist_slots` (cf_a=2, cf_b=2) y renumeró los eventos FINAL (cf_a→4, cf_b→5) para respetar la unicidad de `event_number` por competición; sin generar migraciones (pendiente del usuario) |
| 18 | `calculate_overall_ranking` usaba `order_by('event__event_number')` sobre `Event` (ruta de relación inválida, habría lanzado FieldError) | Corregido a `order_by('event_number')` (consistente con `Event.Meta.ordering`) |
| 19 | `spectacular --validate` reportaba 4 errores (1 único) por `CurrentUserView` (APIView sin `serializer_class`, preexistente) | Añadido `serializer_class = UserSerializer` a `CurrentUserView`; `spectacular --validate` → exit 0 |

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

## Iteración "CompetitionStage → Event.phase + Exponer `event_results`" (15/09/2026)

Se completó el refactor de modelos iniciado por el usuario (opción 1, **sin generar migraciones**) y se implementó la Parte II-bis de `PROMPT.md`: el leaderboard expone `event_results`.

### Cambio de modelo (opción 1)

- Eliminado `CompetitionStage`. `Event` pasa a tener FK directo `competition` + campo `phase` (`QUALIFIER`/`FINAL`) + `UniqueConstraint(competition, event_number)`.
- `Competition.finalist_slots` sustituye a `qualification_count` del stage.
- Ruta `/competition-stages/` eliminada; `events` filtra por `competition` y `phase`.

### Lógica de negocio

- `CompetitionRankingService.calculate_competition_ranking(competition, phase)` filtra `event__competition` + `event__phase`, ordena por `event__event_number` y construye `event_results` desde el mismo queryset (sin N+1).
- `_rank_competitors()` propaga `event_results` en el dict final.
- `FinalQualificationService.get_qualifiers()` usa `competition.finalist_slots` + `Event.Phase.QUALIFIER`.
- `EventRankingService` y permisos usan `event.competition` directamente.

### API / Serializers

- `LeaderboardEntrySerializer` agrega `event_results` (lista de `EventResultSerializer`: `event_id`, `event_number`, `event_name`, `phase`, `result`, `event_rank`, `score`).
- Se conservan `event_ranks`/`event_scores` (backward-compatible).
- `finalist_slots` expuesto en `CompetitionSerializer` y `CompetitionWriteSerializer`.

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `apps/events/models.py` | (usuario) eliminado `CompetitionStage`; `Event.competition`/`Event.phase` + constraint |
| `apps/events/serializers.py`, `views.py`, `urls.py`, `admin.py` | Sin `CompetitionStage`; `EventViewSet` por `competition`/`phase`; ruta `competition-stages` eliminada |
| `apps/rankings/services/competition_ranking_service.py` | Firma `(competition, phase)`; construye/propaga `event_results` |
| `apps/rankings/serializers.py` | `EventResultSerializer` + campo `event_results` |
| `apps/rankings/views.py` | Acciones `qualifier`/`final` con `Event.Phase.*` |
| `apps/rankings/services/final_qualification_service.py` | `finalist_slots` + `Event.Phase.QUALIFIER` |
| `apps/events/services/event_ranking_service.py` | `competition = event.competition` |
| `apps/competitions/serializers.py` | `finalist_slots` expuesto |
| `apps/users/permissions.py` | `resolve_competition` sin fallback a `competition_stage` |
| `apps/users/management/commands/seed_data.py` | Eventos por `competition`/`phase`; FINAL renumerados; `finalist_slots` |
| `tests/*` | Adaptados al nuevo modelo + tests de `event_results` (servicio y API) |
| `PROMPT.md` | Nueva Parte II-bis "Exponer `event_results` en el leaderboard de rankings" |
| `Process.md` | Registro de la iteración |

### Verificaciones

| Verificación | Resultado |
|--------------|-----------|
| `manage.py check` | ✅ 0 issues |
| `manage.py spectacular --validate` | ✅ Limpio (schema `EventResult`, `event_results`) |
| `manage.py makemigrations --check` | ⚠️ Detecta migración pendiente del refactor (NO creada; la genera el usuario) |
| `pytest tests/` | ✅ **113/113 passed** |

### Ejemplo de respuesta del leaderboard

```json
{
  "category": "Individual Male",
  "entries": [
    {
      "rank": 1,
      "competitor_id": 5,
      "display_name": "John Doe",
      "final_score": 100,
      "event_ranks": [1],
      "event_scores": [100],
      "event_results": [
        {
          "event_id": 3,
          "event_number": 1,
          "event_name": "Fran",
          "phase": "QUALIFIER",
          "result": "04:36",
          "event_rank": 1,
          "score": 100
        }
      ]
    }
  ]
}
```

---

## Iteración "Final global leaderboard" (15/09/2026)

El usuario definió el comportamiento esperado: obtienes todos los `Event` de la competición con `phase = QUALIFIER`, sumas los scores de cada `Competitor` en esos WODs, ordenas de mayor a menor, los primeros `finalist_slots` son los clasificados y **solo ellos** tienen registros en `EventCompetitor` para los WOD finales. Además, `/final/` muestra el leaderboard **global** (qualifier+final combinados) y los no clasificados aparecen con `null` ("—") en los WODs finales.

### Cambios

- `CompetitionRankingService.calculate_overall_ranking(competition)`: recorre todos los eventos de la competición (cualquier phase) ordenados por `event_number`; si un competidor no tiene registro en un evento emite `result`/`event_rank`/`score` = `null`; `final_score = sum(score or 0)`; propaga `event_results`.
- `LeaderboardViewSet.final()` usa `calculate_overall_ranking` (ya no requiere eventos FINAL); `qualifier()` valida que existan eventos QUALIFIER (404 si no).
- `EventResultSerializer` y las listas `event_ranks`/`event_scores` aceptan `null`.
- `seed_data`: `_seed_results()` siembra solo qualifier; `_seed_final_results()` calcula el ranking qualifier por categoría y crea `EventCompetitor` en eventos FINAL **solo** para los top `finalist_slots`; el ránking por evento se computa por fase (`_compute_event_rankings(phase=...)`).
- Fix: `order_by('event_number')` en `calculate_overall_ranking` (bug: `event__event_number` sobre `Event`).
- Fix schema: `CurrentUserView.serializer_class = UserSerializer`.

### Ejemplo (tabla del usuario verificada)

| # | Competidor | WOD 1 | WOD 2 | WOD 3 | WOD 4 (Final) | Total |
| - | - | - | - | - | - | - |
| 1 | David | 100 | 98 | 99 | 100 | 495 |
| 2 | Juan | 98 | 100 | 97 | 99 | 490 |
| 3 | Pedro | 95 | 96 | 98 | — | 289 |

Pedro (no clasificado) no tiene registro en WOD 4 → `null` y el Total solo suma sus 3 WODs qualifier.

### Demo del "—" en el seed

Para que el caso se vea en los datos demo (antes nadie dejaba de clasificar porque todas las categorías tenían ≤ 2 competidores y `finalist_slots=2`), se añadió **Daniel** (`DEMO-CFA-006`) como 3º de "Principiantes Individual" en CF-A con los peores resultados del qualifier (Fran 05:20, AMRAP 250, Snatch 70.0 → 3º en sus 3 WODs, 264 pts). Al ser 3º no entra en los top `finalist_slots` → **no** tiene registro en WOD 4 y aparecerá con "—" en `/final/`:

| # | Competidor | WOD 1 | WOD 2 | WOD 3 | WOD 4 (Final) | Total |
| - | - | - | - | - | - | - |
| 1 | Carlos | 100 | 100 | 100 | 100 | 400 |
| 2 | Luis | 94 | 94 | 94 | 94 | 376 |
| 3 | Daniel | 88 | 88 | 88 | — | 264 |

Nuevos conteos demo: **20** personas, **12** competidores, **37** `EventCompetitor` (Daniel solo aporta 3 registros de qualifier).

### Verificaciones

| Verificación | Resultado |
|--------------|-----------|
| `manage.py check` | ✅ 0 issues |
| `manage.py spectacular --validate` | ✅ exit 0 (0 errors) |
| `manage.py makemigrations --check` | ⚠️ Detecta migración pendiente (NO creada; la genera el usuario) |
| `pytest tests/` | ✅ **120/120 passed** |

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

5. **Migración pendiente del refactor CompetitionStage → Event.phase (15/09/2026):**

   ```bash
   .venv\Scripts\python.exe manage.py makemigrations events competitions
   .venv\Scripts\python.exe manage.py migrate
   ```

   Cambios detectados: elimina `CompetitionStage`, elimina `competition_stage`/`stage_type`/`qualification_count`/`order` de Event y las relaciones; añade `Event.competition` (FK) y `Event.phase`; crea `UniqueConstraint(competition, event_number)` en Event; añade `Competition.finalist_slots`.

6. **Seed tras la migración (si se ejecuta el seed):**

   ```bash
   .venv\Scripts\python.exe manage.py seed_data
   ```

   El seed crea 4 competiciones con `finalist_slots` (cf_a=2, cf_b=2, hy_a=0, hy_b=0) y 11 eventos (finales renumerados para respetar la unicidad de `event_number` por competición).

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