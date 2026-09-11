# RESULTADOS.md — Resultado de la Ejecución del PLAN

Ejecución completa del PLAN.md para la construcción del backend de **Scorely** (Django REST Framework + PostgreSQL + Docker).

**Fecha:** 09/09/2026
**Estado global:** ✅ Completo — 14/14 fases + iteración seed ampliado.

---

## Resumen Ejecutivo

El plan se ejecutó en su totalidad. La base del proyecto está operativa:

- **14 de 14 fases completadas + iteración seed.**
- **82/82 tests pasando** contra PostgreSQL 15 real (Docker).
- `manage.py check` y `manage.py spectacular --validate` sin errores ni warnings.
- Imagen Docker `scorely-web` construida correctamente.
- PostgreSQL 15 healthy en contenedor.
- `seed_data` ampliado con datos demo completos (ver abajo).

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
| Users | `User` (custom, email login), `Role`, `CompetitionEditionAdmin` |
| Competitions | `CompetitionType`, `Affiliation`, `Location`, `Competition`, `CompetitionEdition` |
| Participants | `Person`, `Team`, `TeamMember`, `Competitor` (individual/team) |
| Events | `CompetitionCategory`, `CompetitionEnabledCategory`, `CompetitionStage`, `Event`, `EventResultType`, `RankDirection`, `StatusEventCompetitor`, `EventCompetitor` |
| Scoring | `ScoringRule` (tabla de puntos por posición/edición) |

### Servicios de Negocio

| Servicio | Responsabilidad |
|----------|-----------------|
| `ResultParser` | Parsea resultados TIME / REPS / WEIGHT / DISTANCE / POINTS |
| `EventRankingService` | Ranking denso por evento según rank_direction |
| `ScoringService` | Puntos por posición según ScoringRule |
| `CompetitionRankingService` | Clasificación general por edición + desempates |
| `FinalQualificationService` | Selección de top-N para la fase final |

### API REST (JWT)

- Auth: `POST /api/v1/auth/token/`, `POST /api/v1/auth/token/refresh/`.
- CRUD completo por recurso bajo `/api/v1/`.
- Leaderboard público: `/api/v1/leaderboards/edition/<id>/qualifier/` y `/final/`.
- Docs: `/api/schema/`, `/api/docs/` (Swagger), `/api/redoc/`.

### Seguridad

- Autenticación JWT (Bearer) con `simplejwt`.
- Permisos por rol: `IsSuperAdmin`, `IsEditionAdmin`.
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
| Suite de tests (pytest) | ✅ 82/82 passed |
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
| `test_api.py` | Endpoints principales (auth, users, competitions, events, leaderboards) |
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