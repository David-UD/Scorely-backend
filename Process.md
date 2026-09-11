# Process.md — Registro de Progreso

Seguimiento en tiempo real de la ejecución del PLAN.md.

---

## Estado General

| Iteración | Fase | Estado | Inicio | Fin |
|-----------|------|--------|--------|-----|
| Build | 0–14 | ✅ COMPLETADA | 09/09/2026 | 09/09/2026 |
| Seed Update | 0–14 | ✅ COMPLETADA | 09/09/2026 | 09/09/2026 |
| Public GETs | 0–7 | ✅ COMPLETADA | 11/09/2026 | 11/09/2026 |

---

## Iteración Build (Fases 0–14) — Completa

Ver ediciones anteriores. Resultado: 78/78 tests, 14/14 fases completadas.

---

## Iteración Seed Update (09/09/2026) — Completa

Ampliación del comando `seed_data` para incluir competiciones, ediciones, etapas, eventos, participantes y resultados de demostración.

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `apps/users/management/commands/seed_data.py` | Reescritura completa: `seed_data()` ahora crea datos de demo (afiliaciones, ubicaciones, competiciones, ediciones, categorías habilitadas, etapas, eventos, reglas de scoring, participantes, competidores, resultados y ranking por evento). 15 métodos auxiliares, 307 líneas. |
| `tests/test_seed.py` | **Nuevo.** 4 tests: conteo de datos demo, idempotencia (2 ejecuciones consecutivas), ranking calculado y categorías globales. |
| `PLAN.md` | **Nuevo.** Plan de 14 fases para la ampliación del seed (valores demo, especificación, verificación). |
| `PROMPT.md` | Reestructurado como plantilla reutilizable (Parte I: contexto fijo, Parte II: especificación con [COMPLETAR], Parte III: reglas de agente). Parte II completada con "Seed de datos de prueba". |
| `RESULTADOS.md` | Actualizado con 82 tests, detalle de seed y problemas encontrados. |

### Qué crea `seed_data` (valores demo)

| Tipo | Cantidad | Detalle |
|------|----------|---------|
| Afiliaciones | 6 | 4 CrossFit + 2 HYROX |
| Ubicaciones | 4 | Box Centro, Box Norte, Box Sur, Box Este |
| Competiciones | 4 | 2 CF (Open 2026, Showdown) + 2 HYROX (Madrid, Barcelona) |
| Ediciones | 4 | 2026 para cada competición |
| Categorías habilitadas | 6 | Principiantes/Intermedios/RX Individual, Principiantes Mixto, Intermedios Duo, Relevos 4 |
| Etapas | 6 | 1 Qualifier + 1 Final por edición × 4 ediciones (2 finales solo CF) |
| Eventos | 11 | 5×CF-A (Fran, AMRAP, Snatch, Run 5K, WOD Final) + 5×CF-B (idénticos) + 1×HYROX-A (1500m Row) + 1×HYROX-B (1500m Row) |
| Scoring Rules | 40 | Tabla completa por edición (1→100, 2→94, … 10→46) |
| Personas | 19 | 7 CF-A + 8 CF-B + 2 HY-A + 2 HY-B |
| Equipos | 4 | 2 DUO (CF-A) + 2 RELAY (CF-B) |
| Miembros de equipo | 12 | 2×2 DUO + 2×4 RELAY |
| Competidores | 11 | 3 individual + 2 team (CF-A) + 2 team (CF-B) + 2 individual (HY-A) + 2 individual (HY-B) |
| EventCompetitors | 34 | 5×4 (CF-A) + 2×5 (CF-B) + 2×1 (HY-A) + 2×1 (HY-B) |

### Idempotencia

`get_or_create` / `update_or_create` con filtros únicos. Ejecutar `seed_data` 2 veces produce exactamente los mismos conteos. Test verificado: `test_seed_data_is_idempotent`.

### Problemática

| # | Problema | Solución |
|---|----------|----------|
| 1 | Resultado "21:15" para evento tipo DISTANCE en `Run 5K` | Cambiado a "5000" y "4850" (metros) con `rank_direction=desc` |
| 2 | Test `test_seed.py` esperaba 16 personas | Corregido a 19 (7+8+2+2) |
| 3 | `ScoringRule` importado desde `apps.events.models` | Corregido a `apps.scoring.models` |

---

## Fase 0 — Infraestructura y Andamiaje

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos Creados

- `.env.example`
- `.gitignore`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `manage.py`
- `pytest.ini`
- `config/settings/base.py`
- `config/settings/development.py`
- `config/settings/production.py`
- `config/urls.py`
- `config/asgi.py`
- `config/wsgi.py`
- `apps/__init__.py`
- `tests/__init__.py`

### Notas

- Estructura de directorios creada completamente.
- Settings configurados con python-decouple.
- DRF, Spectacular, JWT, CORS configurados en base.py.
- URLs incluyen todas las apps y endpoints de documentación.
- **Ajuste de layout:** `config/`, `apps/` y `tests/` se movieron a la raíz del proyecto (junto a `manage.py`), depurando la estructura `scorely/` anidada inicial.

---

## Fase 1 — App users (Sistema de Usuarios)

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos Cre _files

- `apps/users/models.py` — User (email como username, AbstractBaseUser + PermissionsMixin), Role, CompetitionEditionAdmin
- `apps/users/admin.py`
- `apps/users/serializers.py`
- `apps/users/views.py`
- `apps/users/urls.py`
- `apps/users/permissions.py`
- `apps/users/__init__.py`

### Notas

- Custom User con `USERNAME_FIELD = 'email'`.
- Roles: SUPERADMIN y ADMIN con relación FK en User.
- CompetitionEditionAdmin (M2M intermedia) para asignar admins a ediciones.
- Permissions: `IsSuperAdmin` e `IsEditionAdmin`.

---

## Fase 2 — App competitions (Competiciones)

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos

- `apps/competitions/models.py` — CompetitionType, Affiliation, Location, Competition, CompetitionEdition
- `apps/competitions/admin.py`
- `apps/competitions/serializers.py`
- `apps/competitions/views.py`
- `apps/competitions/urls.py`
- `apps/competitions/__init__.py`

### Notas

- CompetitionEdition con `unique_together (competition, year)` y estados DRAFT/PUBLISHED.
- **Fix:** los serializers de Competition/CompetitionEdition tenían los FK como nested read-only, lo que provocaba NOT NULL al crear. Se añadieron los serializers `CompetitionWriteSerializer` y `CompetitionEditionWriteSerializer` (con PrimaryKeyRelatedField) y `get_serializer_class()` en los viewsets.

---

## Fase 3 — App participants (Participantes)

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos

- `apps/participants/models.py` — Person, Team, TeamMember, Competitor (Individual/Team)
- `apps/participants/admin.py`
- `apps/participants/serializers.py`
- `apps/participants/views.py`
- `apps/participants/urls.py`
- `apps/participants/__init__.py`

### Notas

- Competitor con validación `clean()`: INDIVIDUAL exige person sin team; TEAM exige team sin person.
- Categorías habilitadas por edición (`CompetitionEnabledCategory`).

---

## Fase 4 — App events (Eventos)

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos

- `apps/events/models.py` — CompetitionCategory, CompetitionEnabledCategory, CompetitionStage, EventResultType, RankDirection, Event, StatusEventCompetitor, EventCompetitor
- `apps/events/admin.py`
- `apps/events/serializers.py`
- `apps/events/views.py`
- `apps/events/urls.py`
- `apps/events/__init__.py`

### Notas

- CompetitionStage valida un solo Qualifier/Final por edición en `clean()`.
- EventCompetitor guarda `result` (string) + `event_rank` + `score`.

---

## Fase 5 — App scoring (Tabulación)

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos

- `apps/scoring/models.py` — ScoringRule (tabla de puntos por posición y edición)
- `apps/scoring/admin.py`
- `apps/scoring/serializers.py`
- `apps/scoring/views.py`
- `apps/scoring/urls.py`
- `apps/scoring/__init__.py`

### Notas

- `unique_together (competition_edition, position)`.
- Tabla configurable por edición (ej. 1→100, 2→94, ...).

---

## Fase 6 — Services (Lógica de Negocio)

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos

- `apps/events/services/__init__.py`
- `apps/events/services/result_parser.py` — ResultParser
- `apps/events/services/event_ranking_service.py` — EventRankingService (ranking denso por evento)
- `apps/scoring/services/__init__.py`
- `apps/scoring/services/scoring_service.py` — ScoringService
- `apps/rankings/services/__init__.py`
- `apps/rankings/services/competition_ranking_service.py` — CompetitionRankingService
- `apps/rankings/services/final_qualification_service.py` — FinalQualificationService

### Notas

- **Fix:** `EventRankingService` referenciaba `event.competition_edition.competition_edition`; corregido a `event.competition_stage.competition_edition`.

---

## Fase 7 — App rankings (Clasificaciones)

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos

- `apps/rankings/__init__.py`
- `apps/rankings/serializers.py` — LeaderboardEntrySerializer, LeaderboardSerializer
- `apps/rankings/views.py` — LeaderboardViewSet con acciones qualifier/final
- `apps/rankings/urls.py`
- `apps/rankings/services/...`

### Notas

- Endpoints públicos (AllowAny):
  - `GET /api/v1/leaderboards/edition/<id>/qualifier/`
  - `GET /api/v1/leaderboards/edition/<id>/final/`
- Leaderboard agrupado por categoría con ranking y puntuación final.

---

## Fase 8 — API REST

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Endpoints

| Recurso | Ruta |
|---------|------|
| Users | `/api/v1/users/` |
| Roles | `/api/v1/roles/` |
| Competition Types | `/api/v1/competition-types/` |
| Affiliations | `/api/v1/affiliations/` |
| Locations | `/api/v1/locations/` |
| Competitions | `/api/v1/competitions/` |
| Competition Editions | `/api/v1/competition-editions/` |
| Persons | `/api/v1/persons/` |
| Teams | `/api/v1/teams/` |
| Competitors | `/api/v1/competitors/` |
| Categories | `/api/v1/categories/` |
| Enabled Categories | `/api/v1/enabled-categories/` |
| Stages | `/api/v1/stages/` |
| Events | `/api/v1/events/` |
| Event Result Types | `/api/v1/event-result-types/` |
| Rank Directions | `/api/v1/rank-directions/` |
| Event Competitors | `/api/v1/event-competitors/` |
| Scoring Rules | `/api/v1/scoring-rules/` |
| Leaderboards | `/api/v1/leaderboards/` |

### Notas

- **Fix:** los routers JWT se definieron con vistas explícitas `TokenObtainPairView`/`TokenRefreshView` porque versiones nuevas de simplejwt no incluyen `rest_framework_simplejwt.urls`. Rutas finales: `/api/v1/auth/token/` y `/api/v1/auth/token/refresh/`.

---

## Fase 9 — Security

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos

- `apps/users/permissions.py` — IsSuperAdmin, IsEditionAdmin
- `config/settings/base.py` — JWT (SIMPLE_JWT), CORS (CORS_ALLOWED_ORIGINS)
- Tests de seguridad en `tests/test_security.py`

### Notas

- `AUTH_HEADER_TYPES = ('Bearer',)`.
- Tokens: access 30 min, refresh 7 días, con rotación y blacklist configurados (requiere `rest_framework_simplejwt.token_blacklist` si se activa).
- CORS permite `http://localhost:3000` por defecto.

---

## Fase 10 — Django Admin

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos

- `apps/users/admin.py`
- `apps/competitions/admin.py`
- `apps/participants/admin.py`
- `apps/events/admin.py`
- `apps/scoring/admin.py`

### Notas

- **Fix:** registros con `autocomplete_fields` requerían `search_fields` en los admins referenciados (agent CodE040); se añadieron `search_fields` faltantes (CompetitionEnabledCategory, CompetitionStage, EventResultType, RankDirection, StatusEventCompetitor, CompetitionEnabledCategory en participants).

---

## Fase 11 — Seed Data

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos

- `apps/users/management/__init__.py`
- `apps/users/management/commands/__init__.py`
- `apps/users/management/commands/seed_data.py`

### Notas

- Comando `manage.py seed_data` que crea tipos de competición, roles, usuarios demo y datos de ejemplo.

---

## Fase 12 — Documentación

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Notas

- drf-spectacular configurado (`SPECTACULAR_SETTINGS`).
- Endpoints: `/api/schema/`, `/api/docs/` (Swagger), `/api/redoc/`.
- **Fix:** `LeaderboardViewSet` necesitaba `serializer_class`, `@extend_schema` con `OpenApiParameter` y `@extend_schema_field` en los SerializerMethodFields para generar el schema sin warnings/errores. `manage.py spectacular --validate` pasa limpio.

---

## Fase 13 — Testing

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Archivos

- `tests/conftest.py`
- `tests/test_users.py`
- `tests/test_competitions.py`
- `tests/test_participants.py`
- `tests/test_events.py`
- `tests/test_scoring.py`
- `tests/test_rankings.py`
- `tests/test_api.py`
- `tests/test_security.py`

### Resultado: 78 passed

### Notas

- pytest-django con `nomigrations` (opción `--nomigrations` en pytest.ini) para evitar el esquema mixto de apps migradas vs no migradas; las migraciones de BD las ejecutará el usuario manualmente.
- **Fixes aplicados:**
  - Tests de eventos: faltaba fixture `stage_qualifier` en `test_only_one_qualifier_per_edition` (existía el stage previo que dispara la ValidationError).
  - Tests de seguridad: `set_exp(lifetime=timedelta(seconds=-1))` (exigía timedelta); se expira el access token; `request` para permisos como `SimpleNamespace(user=...)`.

---

## Fase 14 — Verificación Final

**Inicio:** 09/09/2026
**Fin:** 09/09/2026
**Estado:** ✅ COMPLETADA

### Notas

- `manage.py check` → 0 issues.
- `manage.py spectacular --file schema.yml --validate` → limpio.
- Tests: 78/78 passed contra PostgreSQL 15 en Docker.
- **Fix Dockerfile:** `python:3.8.10-slim` usaba Debian buster (EOL, repos sin `Release`). Cambiado a `python:3.11-slim`. Imagen `scorely-web` build OK.
- **Fix docker-compose:** service web necesita `DB_HOST: db` (env override) porque `.env` apunta a `localhost` (para tests desde el host).
- PostgreSQL 15 en contenedor: healthy.

---

## Iteración "Public GETs" (Fases 0–7) — 11/09/2026 — Completa

Apertura de endpoints de lectura (GET) al público sin autenticación, según Parte II de `PROMPT.md`.

### Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `apps/competitions/views.py` | `CompetitionViewSet`: añadido `permission_classes = (IsAuthenticatedOrReadOnly,)` |
| `apps/events/views.py` | `CompetitionStageViewSet` y `EventViewSet`: añadido `permission_classes = (IsAuthenticatedOrReadOnly,)` |
| `tests/test_api.py` | Nueva clase `TestAPIPublicReadOnly` (11 tests: lecturas públicas, escrituras 401, regresión JWT, leaderboard intacto) |

### Enfoque elegido

**Opción A** del PLAN.md: `IsAuthenticatedOrReadOnly` de DRF declarado directamente en los 3 ViewSets objetivo (más simple y consistente con el patrón de `LeaderboardViewSet`). No se creó mixin ni se cambió el `DEFAULT_PERMISSION_CLASSES` global.

### Qué se abrió al público

| Endpoint | Antes | Después |
|----------|-------|---------|
| `GET /api/v1/competitions/` | 401 | 200 (listado) |
| `GET /api/v1/competitions/<id>/` | 401 | 200 (detalle con type/status/affiliation/location) |
| `GET /api/v1/competition-stages/?competition=<id>` | 401 | 200 |
| `GET /api/v1/events/?competition_stage=<id>` | 401 | 200 |
| `POST/DELETE` de los mismos | 401 | 401 (sin cambios) |
| `GET /api/v1/leaderboards/competition/<id>/*` | 200 | 200 (sin cambios) |

### Verificaciones

| Verificación | Resultado |
|--------------|-----------|
| `manage.py check` | ✅ 0 issues |
| `manage.py spectacular --validate` | ✅ OK |
| `manage.py makemigrations --check` | ✅ No changes detected |
| `pytest tests/` | ✅ **92/92 passed** (81 previos + 11 nuevos) |

### Migraciones

Ninguna (no hubo cambios de modelo). No hay pasos manuales de migración para esta iteración.