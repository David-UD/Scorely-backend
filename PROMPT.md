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
│   ├── users/              # User, CompetitionAdmin, permisos, seed_data
│   ├── competitions/       # CompetitionType, Affiliation, Location, StatusCompetition, Competition
│   ├── participants/       # Athlete, Team, TeamMember, Competitor
│   ├── events/             # CompetitionCategory, EnabledCompetitionCategory, Event (competition FK + phase + workout/is_ascending/is_active), EventCompetitor
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
Competition (slug único, año derivado de start_date, status DRAFT/ACTIVE/FINISHED, finalist_slots)
  └─▶ Event                una QUALIFIER y una FINAL por competición (phase) / UNIQUE(competition, event_number)
        └─▶ EventCompetitor   UNIQUE(competitor, event) / result + event_rank + score
              └─▶ Final Score
                    └─▶ Leaderboard

Participantes:
Athlete ─┐
         ▼
   Competitor  (INDIVIDUAL usa athlete | TEAM usa team, nunca ambos)
         ▲
Team ── TeamMember (UNIQUE(team, athlete))
```

El motor de puntuación **siempre** trabaja con `Competitor`, sea individual o equipo.

## Sistema de puntuación (reglas intocables)

> **El resultado NO es la puntuación.**

```
Resultado → Posición (rank) → Puntos WOD (ScoringRule) → Puntaje Final → Leaderboard
```

- `Final Score = SUM(puntos de todos los eventos válidos)`.
- Empates con ranking deportivo denso: `1, 2, 2, 4` (nunca `1, 2, 3, 4`).
- Cada competición define su propia tabla `ScoringRule` (nunca asumir fórmula fija).
- La fase Final tiene ranking **independiente**; nunca sumar Qualifier + Final.
- Desempates permitidos: mayor puntaje → más 1ºs → más 2ºs → más 3ºs → mejor resultado último evento común → mantener empate. **Prohibidos:** ID, nombre, fecha de registro.

## Seguridad

| Requisito | Implementación |
|-----------|---------------|
| Autenticación | JWT via simplejwt (`/api/v1/auth/token/`, `/api/v1/auth/token/refresh/`) |
| Autorización | Permisos por competición (`apps/users/permissions.py`) |
| Secretos | Solo variables de entorno |
| CORS | Configurable |
| Leaderboards | Públicos (`AllowAny`) |
| Lectura pública (competencias/etapas/eventos) | Públicos de solo lectura — ver Parte II |

## Restricciones del proyecto

- No crear ramas.
- No realizar push ni subir a git (el agente no hace nada de git sin pedido explícito del usuario).
- **AVISAR al usuario para ejecutar las migraciones manualmente** (`makemigrations` / `migrate` / `seed_data` / `createsuperuser`). El agente no las ejecuta.
- Documentar avances en `Process.md` al iniciar y finalizar cada paso.
- No añadir comentarios al código salvo que se soliciten.

---

# Parte II — Plantilla de especificación de la actualización

## 1. Título

Abrir endpoints de lectura al público (GET de solo lectura) para el frontend público

## 2. Objetivo

Permitir que las vistas públicas del frontend (SPA, `PROMPT-frontend.md`) consulten competiciones, etapas y eventos **sin autenticarse**, manteniendo las escrituras protegidas por JWT.

Hoy el backend solo expone `leaderboards` con `AllowAny`; `competitions`, `competition-stages` y `events` exigen JWT por defecto (`DEFAULT_PERMISSION_CLASSES = IsAuthenticated` en `config/settings/base.py:86`). Esto bloquea el inicio público `/` y el detalle de competición (decisión aplazada en `PROMPT-frontend.md`, sección 12, que esta actualización resuelve).

## 3. Alcance

**Incluye (se debe implementar):**
- Abrir lectura pública (GET) de:
  - `GET /api/v1/competitions/` y `GET /api/v1/competitions/{id}/`
  - `GET /api/v1/competition-stages/?competition={id}`
  - `GET /api/v1/events/?competition_stage={id}`
- Las escrituras de esos mismos endpoints (`POST`/`PUT`/`PATCH`/`DELETE`) **permanecen autenticadas** (401 sin JWT).
- Añadir tests de permiso que aseguren el comportamiento público + protegido.

**Excluye (NO tocar):**
- No modificar modelos, serializers, services ni la lógica de ranking/puntuación.
- No abrir la lectura de catálogos que la UI pública no consume: `users`, `auth`, `competition-admins`, `affiliations`, `locations`, `competition-types`, `competition-categories`, `enabled-competition-categories`, `athletes`, `teams`, `team-members`, `competitors`, `event-competitors`, `scoring-rules`.
- No ejecutar `makemigrations`/`migrate` (no hay cambios de modelo).
- No cambiar `LeaderboardViewSet` (ya público).

## 4. Cambios en el modelo de datos

- Ninguno. No se generan migraciones.

## 5. Cambios en la API

Enfoque recomendado: usar la clase **`IsAuthenticatedOrReadOnly`** de DRF por ViewSet (permite `GET`/`HEAD`/`OPTIONS` a cualquiera; exige autenticación para el resto de métodos).

| ViewSet | App | Cambio |
|---------|-----|--------|
| `CompetitionViewSet` | `apps/competitions/views.py` | `permission_classes = (IsAuthenticatedOrReadOnly,)` |
| `CompetitionStageViewSet` | `apps/events/views.py` | ídem |
| `EventViewSet` | `apps/events/views.py` | ídem |

Alternativa (si se quiere centralizar la regla): crear un mixin `PublicReadOnly(IsAuthenticatedOrReadOnly)` en `apps/users/permissions.py` y aplicarlo a los tres ViewSets. Elegir la opción más simple y consistente con el código existente.

Consideraciones:
- El detalle de `Competition` ya embebe `competition_type`, `status`, `affiliation`, `location` vía `CompetitionSerializer` (solo lectura), así que la página pública de detalle no necesita llamadas adicionales a esos catálogos.
- Se mantienen intactos los filtros y búsquedas actuales (django-filter): `competitions` filtra por `competition_type`/`status`; `competition-stages` por `competition`/`stage_type`; `events` por `competition_stage`.
- `CompetitionViewSet` conserva su `get_serializer_class()` (read vs write) sin cambios.

## 6. Cambios en lógica de negocio / servicios

- Ninguno.

## 7. Cambios en Django Admin

- Ninguno.

## 8. Cambios en documentación

- `Process.md`: registrar avances y resultado de la fase.
- `RESULTADOS.md`: registrar el resultado y las verificaciones.
- `README.md`: actualizar la sección API/seguridad — indicar que los GET de `competitions`, `competition-stages` y `events` son públicos (solo lectura) además de los leaderboards.
- `PROMPT-frontend.md`: actualizar la sección 12 (la decisión ya no está pendiente → opción (a) implementada) y la tabla de endpoints marcados como "Pública pendiente (hoy JWT)" → "Pública (AllowAny)".

## 9. Detalle de implementación

Para cada ViewSet objetivo:

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class CompetitionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    ...
```

Verificar al final:
- Que usuarios anónimos y autenticados pueden leer (`GET`).
- Que `POST`/`PATCH`/`PUT`/`DELETE` siguen devolviendo `401` sin credenciales válidas y funcionan con superadmin/`CompetitionAdmin` según las reglas actuales de `apps/users/permissions.py`.

## 10. Pruebas requeridas

| Test | Escenario | Resultado esperado |
|------|-----------|--------------------|
| GET `/api/v1/competitions/` sin token | Anónimo | 200 con listado |
| GET `/api/v1/competitions/{id}/` sin token | Anónimo | 200 con detalle (type/status/affiliation/location embebidos) |
| POST `/api/v1/competitions/` sin token | Anónimo | 401 |
| DELETE `/api/v1/competitions/{id}/` sin token | Anónimo | 401 |
| GET `/api/v1/competition-stages/?competition={id}` sin token | Anónimo | 200 |
| POST `/api/v1/competition-stages/` sin token | Anónimo | 401 |
| GET `/api/v1/events/?competition_stage={id}` sin token | Anónimo | 200 |
| POST `/api/v1/events/` sin token | Anónimo | 401 |
| GET públicas con JWT válido | Autenticado | 200 (regresión) |
| Leaderboards público | Anónimo | 200 (sin cambios) |

Añadir los casos nuevos en `tests/test_api.py` (reutilizando fixtures existentes). Mantener la suite completa en verde.

## 11. Criterios de aceptación

Checklist verificable al terminar:

- `python manage.py check --settings=config.settings.development` sin errores.
- `python manage.py spectacular --validate --settings=config.settings.development` limpio.
- `python manage.py makemigrations --check --settings=config.settings.development` → "No changes" (sin migraciones).
- Suite pytest completa en verde (incluidos los nuevos tests de permisos).
- GET públicos responden 200 sin token; escrituras responden 401 sin token.

## 12. Observaciones / riesgos

- **Backward-compatible:** el cambio solo relaja lectura; no rompe contratos existentes.
- Origen de la necesidad: `PROMPT-frontend.md` — vistas públicas `/` (recientes + todas) y detalle (info general, mapa, afiliación, fechas, WODs y leaderboards) sin login.
- No abrir de más: si una vista pública futura necesitara otros catálogos (p. ej. `competition-categories` o `enabled-competition-categories` para filtros de leaderboard), abrirlos en una iteración aparte con su test.
- El modelo de eventos ya no tiene `EventResultType`/`RankDirection`/`StatusEventCompetitor` (refactor del usuario): `Event` usa `workout`, `is_ascending` (True → menor es mejor / tiempo; False → mayor es mejor / numérico) e `is_active`; `EventCompetitor` no tiene `status`. Si una vista futura necesitara catálogos de resultado/dirección/estado, reintroducir el modelo o el campo en una iteración aparte.
- Cuidado con la doble fuente de permisos: si se añade `DEFAULT_PERMISSION_CLASSES` global distinta, revisar que no contradiga los `permission_classes` por ViewSet.

---

# Parte II-bis — Especificación de la actualización actual

## 1. Título

Exponer `event_results` en el leaderboard de rankings

## 2. Objetivo

El frontend necesita saber **qué evento corresponde a cada valor** de `event_ranks`/`event_scores` del leaderboard (listas planas de enteros). Se agrega `event_results`, un desglose por evento dentro de cada `LeaderboardEntry`, con `event_id`, `event_number`, `event_name`, `phase`, `result` (string crudo), `event_rank` y `score`.

## 3. Alcance

**Incluye (se debe implementar):**
- `apps/rankings/serializers.py`: nuevo `EventResultSerializer` + campo `event_results` en `LeaderboardEntrySerializer`.
- `apps/rankings/services/competition_ranking_service.py`: construir y propagar `event_results` en cada entrada del ranking.
- Tests: `tests/test_rankings.py` y `tests/test_api.py` (casos de `event_results`).

**Excluye (NO tocar):**
- Modelos (`Event`, `EventCompetitor`, `Competition`) ni migraciones.
- `EventRankingService`, `ScoringService`, `LeaderboardViewSet`, rutas y permisos.
- Eliminar `event_ranks`/`event_scores` (se conservan: backward-compatible).

## 4. Cambios en el modelo de datos

- Ninguno. No se generan migraciones.

## 5. Cambios en la API

- Solo se enriquece la respuesta de `GET /api/v1/leaderboards/competition/{id}/qualifier/` y `/final/`: cada `entry` incluye `event_results` (lista de objetos, ordenada por `event_number`). Sin cambios de rutas ni permisos.

## 6. Cambios en lógica de negocio / servicios

- `CompetitionRankingService.calculate_competition_ranking()` filtra por `competition` + `phase` (modelo vigente, opción 1 del refactor) y construye `event_results` desde el mismo queryset de `EventCompetitor` (evita N+1, orden consistente por `event__event_number`).
- `_rank_competitors()` propaga `event_results` en el dict rankeado final.

## 7. Cambios en Django Admin

- Ninguno.

## 8. Cambios en documentación

- `Process.md`: registrar avances y fases de la iteración.
- `RESULTADOS.md`: registrar el resultado y las verificaciones.
- `README.md`: indicar que la respuesta del leaderboard incluye `event_results` con un ejemplo de estructura.

## 9. Detalle de implementación

Nuevo serializer en `apps/rankings/serializers.py`:

```python
class EventResultSerializer(serializers.Serializer):
    event_id = serializers.IntegerField()
    event_number = serializers.IntegerField()
    event_name = serializers.CharField()
    phase = serializers.CharField()
    result = serializers.CharField()
    event_rank = serializers.IntegerField(allow_null=True)
    score = serializers.IntegerField(allow_null=True)
```

Campo nuevo en `LeaderboardEntrySerializer`:

```python
event_results = EventResultSerializer(many=True, read_only=True)
```

En el servicio, construir `event_results` desde el queryset ordenado de `EventCompetitor` y agregarlo al dict de `competitor_scores`; `_rank_competitors()` debe conservarlo al reconstruir el dict final.

## 10. Pruebas requeridas

| Test | Escenario | Resultado esperado |
|------|-----------|--------------------|
| Presencia | Capa de servicio: cada entry tiene `event_results` | `len == número de eventos` de la fase |
| Estructura | Cada elemento expone los 7 campos | `event_id`, `event_number`, `event_name`, `phase`, `result`, `event_rank`, `score` |
| Suma | `sum(score)` de `event_results` vs `final_score` | Iguales |
| Orden | Múltiples eventos en una fase | Orden por `event_number` |
| Vacío | Competitor sin resultados (o fase sin eventos) | `event_results == []` (o categoría con lista vacía) |
| API | `GET qualifier` con datos rankeados | 200; `entries[0].event_results` presente y coherente |

## 11. Criterios de aceptación

- `python manage.py check --settings=config.settings.development` sin errores.
- `python manage.py spectacular --validate --settings=config.settings.development` limpio (schema con `EventResult` y `event_results`).
- Suite pytest completa en verde (incluidos los casos nuevos).
- `event_ranks`/`event_scores` intactos (backward-compatible).

## 12. Observaciones / riesgos

- Backward-compatible: se agrega un campo, no se elimina ninguno.
- `result` es el string crudo del resultado (p. ej. `"04:36"`), igual que `EventCompetitor.result`; no se parsea.
- El orden interno es `event_number` (coherente con `Event.Meta.ordering`).
- Impacto en tamaño de respuesta: una entrada mide ~7 campos × nº de eventos de la fase. Considerar paginación/serialización selectiva en el futuro si crece.

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