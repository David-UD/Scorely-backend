# Plan de Implementación — Seed de datos de prueba (PROMPT.md, Parte II)

> Este plan reemplaza el plan original de construcción (proyecto ya implementado y verificado: 78 tests en verde). Documenta paso a paso cómo implementar la actualización definida en la **Parte II de `PROMPT.md`**: ampliar el seed con datos de ejemplo para visualizar el API y los leaderboards.
>
> **Alcance ejecutado por este plan: SOLO los cambios indicados. No ejecutar nada más.**

---

## Restricciones Globales

- No crear ramas git / no push.
- **NO ejecutar** `makemigrations`, `migrate`, `seed_data` ni `createsuperuser`. Avisar al usuario para que los ejecute manualmente.
- No modificar modelos, serializers, views, services ni la API existentes.
- La lógica nueva vive en el management command `seed_data` (dato, no en `services/` — es símplemente data seeding).
- Nunca guardar credenciales en código.
- Documentar avances en `Process.md` al iniciar y finalizar cada fase.

---

## Contexto / Estado actual

- Backend completo: apps `users`, `competitions`, `participants`, `events`, `scoring`, `rankings` en `apps/`.
- `seed_data` actual (`apps/users/management/commands/seed_data.py`) solo crea **catálogos**: Roles, CompetitionTypes, StatusEventCompetitor, EventResultType, RankDirection y categorías globales (Individual/Team/Master). No crea competencias, ediciones, eventos, competidores ni resultados.
- `EventCompetitor` guarda `result`, `event_rank` y `score`. **El rank y el score NO se calculan al guardar por API o por seed**: se calculan invocando `EventRankingService.calculate_event_ranking(event)` (apps/events/services/event_ranking_service.py), que asigna `event_rank` y `score` según `ScoringRule` de la edición, usando ranking denso (`1, 2, 2, 4`). **El leaderboard suma `score` de los `EventCompetitor` con `status='VALID'`** (apps/rankings/services/competition_ranking_service.py) → **sin ese paso el leaderboard mostraría scores con `None`/0**.
- El seed debe ser **idempotente** (ejecutable N veces sin duplicar): usar `get_or_create` con claves estables.

---

## Pre-requisitos antes de implementar

1. `.env` configurado, PostgreSQL arriba (`docker compose up`) y **migraciones ya aplicadas** (las ejecuta el usuario).
2. El usuario completa los `[COMPLETAR]` restantes en `PROMPT.md` (Parte II, sección 9):
   - Nombres y años de las 4 competencias (2 CROSSFIT + 2 HYROX).
   - Nombres/ciudades de las 6 affiliations ("box") y 4 locations.
   - Nombres de los WODs (los tipos y direcciones ya están definidos en el plan).
   - `qualification_count` deseado por fase QUALIFIER (sugerencia: 2 para demostración).
3. Confirmar que no existen datos previos de prueba colisionando (el seed usa claves estables).

---

## Fase 0 — Preparación y verificación inicial

### Paso 0.1: Ejecutar verificaciones de línea base (solo lectura)

```bash
python manage.py check --settings=config.settings.development
python manage.py spectacular --validate --settings=config.settings.development
python -m pytest tests --settings=config.settings.development
```

**Criterio:** 0 issues, schema OK, suite completa en verde (78 passed). Registrar en `Process.md`.

### Paso 0.2: Anotar datos definidos por el usuario

Volcar en `Process.md` los valores definitivos de las secciones `[COMPLETAR]` de `PROMPT.md` para usar como claves estables del seed.

---

## Fase 1 — Estructurar el command `seed_data` (refactor sin cambio de comportamiento)

### Paso 1.1: Organizar por métodos

Reestructurar `apps/users/management/commands/seed_data.py` manteniendo los métodos existentes y agregando (al estyy) los helpers de esta actualización:

```
handle()
├── _seed_roles()                       # existente
├── _seed_competition_types()           # existente
├── _seed_statuses()                    # existente
├── _seed_event_result_types()          # existente
├── _seed_rank_directions()             # existente
├── _seed_categories()                  # EXISTENTE + extensiones (Fase 2)
├── _seed_affiliations()                # NUEVO (Fase 3)
├── _seed_locations()                   # NUEVO (Fase 3)
├── _seed_competitions_and_editions()   # NUEVO (Fase 4)
├── _seed_enabled_categories()          # NUEVO (Fase 5)
├── _seed_stages_and_events()           # NUEVO (Fase 6)
├── _seed_scoring_rules()               # NUEVO (Fase 7)
├── _seed_participants()                # NUEVO (Fase 8)
├── _seed_results()                     # NUEVO (Fase 9)
└── _compute_event_rankings()           # NUEVO (Fase 10)
```

Importaciones nuevas necesarias:

```python
from apps.competitions.models import Affiliation, Competition, CompetitionEdition, Location
from apps.events.models import (
    CompetitionCategory, CompetitionEnabledCategory, CompetitionStage,
    Event, EventCompetitor, EventResultType, RankDirection, StatusEventCompetitor,
)
from apps.participants.models import Competitor, Person, Team, TeamMember
from apps.scoring.models import ScoringRule
from apps.events.services.event_ranking_service import EventRankingService
```

---

## Fase 2 — Categorías globales nuevas

### Paso 2.1: Agregar al catálogo de `CompetitionCategory` (name es UNIQUE)

Extensiones a `_seed_categories()` (conservando las 7 actuales):

| Nombre | min_members | max_members |
|--------|-------------|-------------|
| Principiantes Individual | 1 | 1 |
| Intermedios Individual | 1 | 1 |
| RX Individual | 1 | 1 |
| Principiantes Mixto | 2 | 2 |
| Intermedios Duo | 2 | 2 |
| Relevos 4 | 4 | 4 |

**Implementación:** `get_or_create(name=..., defaults={'min_members': ..., 'max_members': ...})`.

### Paso 2.2: Verificación

Ejecutar el command → en consola "created". Ejecutar de nuevo → "exists" (sin duplicados).

---

## Fase 3 — Affiliations y Locations

### Paso 3.1: `_seed_affiliations()` — 6 registros

| # | Nombre (clave estable, del usuario) | city | state | country |
|---|--------------------------------------|------|-------|---------|
| 1-4 | 4 "box" CrossFit (`[COMPLETAR]`) | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` |
| 5-6 | 2 "box" HYROX (`[COMPLETAR]`) | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` |

> Nota: `Affiliation` no tiene campo de tipo; la distinción crossfit/hyrox queda implícita en el nombre.

### Paso 3.2: `_seed_locations()` — 4 registros

| # | Uso | Nombre/sede (`[COMPLETAR]`) | address | city | country |
|---|-----|------------------------------|---------|------|---------|
| 1 | Comp CrossFit A | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` |
| 2 | Comp CrossFit B | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` |
| 3 | Comp HYROX A | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` |
| 4 | Comp HYROX B | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` |

**Regla de negocio:** `Competition` exige `affiliation` y `location` NO NULL (`PROTECT`) → cada competencia usa una affiliation + su location.

### Paso 3.3: Verificación

`Competition` aún no se crea en esta fase; verificar conteos tras la Fase 4.

---

## Fase 4 — Competencias y ediciones

### Paso 4.1: `_seed_competitions_and_editions()` — 4 competencias + 4 ediciones

| # | Nombre (`[COMPLETAR]`) | Type | affiliation | location | Año (`[COMPLETAR]`) | start_date | end_date | status |
|---|------------------------|------|-------------|----------|---------------------|------------|----------|--------|
| 1 | CrossFit A | CROSSFIT | aff 1 | loc 1 | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` | PUBLISHED |
| 2 | CrossFit B | CROSSFIT | aff 2 | loc 2 | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` | PUBLISHED |
| 3 | HYROX A | HYROX | aff 5 | loc 3 | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` | PUBLISHED |
| 4 | HYROX B | HYROX | aff 6 | loc 4 | `[COMPLETAR]` | `[COMPLETAR]` | `[COMPLETAR]` | PUBLISHED |

**Implementación:** guardar instancias en atributos del comando (`self.cf_a`, `self.cf_b`, `self.hy_a`, `self.hy_b` para reusar en fases siguientes). Usar `get_or_create(name=..., defaults={...})` y luego edición con `get_or_create(competition=..., year=..., defaults={...})`. Aviso: `UNIQUE(competition, year)`.

### Paso 4.2: Verificación

- `python manage.py shell -c "from apps.competitions.models import Competition, CompetitionEdition; print(Competition.objects.count(), CompetitionEdition.objects.count())"` → `4 4`.
- Re-ejecutar seed → sigue `4 4`.

---

## Fase 5 — Categorías habilitadas por edición

### Paso 5.1: `_seed_enabled_categories()`

| Edición | Categorías habilitadas |
|---------|------------------------|
| CrossFit A | Principiantes Individual, Intermedios Individual, Principiantes Mixto |
| CrossFit B | Relevos 4 |
| HYROX A | RX Individual |
| HYROX B | RX Individual |

**Implementación:** `CompetitionEnabledCategory.objects.get_or_create(competition_edition=self.cf_a, competition_category=<cat>, defaults={})` (unique_together edition+category). Guardar instancias por edición (p. ej. `self.cf_a_cats`) para Fase 8.

### Paso 5.2: Verificación

Conteo de enabled categories = `3 + 1 + 1 + 1 = 6`.

---

## Fase 6 — Stages y eventos

### Paso 6.1: `_seed_stages_and_events()` — stages

| Edición | QUALIFIER (order 1) | FINAL (order 2) | qualification_count |
|---------|--------------------|-----------------|---------------------|
| CrossFit A | ✓ | ✓ | `[COMPLETAR]` (sug: 2) |
| CrossFit B | ✓ | ✓ | `[COMPLETAR]` (sug: 2) |
| HYROX A | ✓ | — | `[COMPLETAR]` (sug: 0) |
| HYROX B | ✓ | — | `[COMPLETAR]` (sug: 0) |

> Regla: un solo QUALIFIER y un solo FINAL por edición (validación a nivel modelo). Guardar instancias (`self.cf_a_qual`, `self.cf_a_fin`, etc.) para crear eventos.

### Paso 6.2: Eventos por stage

Usar `get_or_create(competition_stage=..., event_number=..., defaults={...})` (unique_together stage+event_number). Tipos/direcciones:

| Competencia | Stage | Evento | event_number | ResultType | RankDirection |
|-------------|-------|--------|--------------|------------|---------------|
| CrossFit A | QUALIFIER | `[COMPLETAR]` WOD 1 | 1 | TIME | ASC |
| CrossFit A | QUALIFIER | `[COMPLETAR]` WOD 2 | 2 | REPS | DESC |
| CrossFit A | QUALIFIER | `[COMPLETAR]` WOD 3 | 3 | WEIGHT | DESC |
| CrossFit A | FINAL | `[COMPLETAR]` WOD Final | 1 | TIME | ASC |
| CrossFit B | QUALIFIER | `[COMPLETAR]` WOD 1 | 1 | TIME | ASC |
| CrossFit B | QUALIFIER | `[COMPLETAR]` WOD 2 | 2 | REPS | DESC |
| CrossFit B | QUALIFIER | `[COMPLETAR]` WOD 3 | 3 | WEIGHT | DESC |
| CrossFit B | QUALIFIER | `[COMPLETAR]` WOD 4 | 4 | REPS o DISTANCE | DESC |
| CrossFit B | FINAL | `[COMPLETAR]` WOD Final | 1 | TIME | ASC |
| HYROX A | QUALIFIER | HYROX Race | 1 | TIME | ASC |
| HYROX B | QUALIFIER | HYROX Race | 1 | TIME | ASC |

Guardar las instancias de `Event` de cada stage (listas `self.cf_a_qual_events`, etc.) para la Fase 9.

### Paso 6.3: Verificación

Conteo eventos = `(3+1) + (4+1) + 1 + 1 = 11`. Sin violar `UNIQUE(stage, event_number)`.

---

## Fase 7 — ScoringRules por edición

### Paso 7.1: `_seed_scoring_rules()` — misma tabla en las 4 ediciones

| Posición | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|----------|---|---|---|---|---|---|---|---|---|---|
| Puntos | 100 | 94 | 88 | 82 | 76 | 70 | 64 | 58 | 52 | 46 |

**Implementación:** para cada edición y posición: `get_or_create(competition_edition=edition, position=p, defaults={'points': pts})` (unique_together edition+position).

### Paso 7.2: Verificación

Conteo ScoringRule = `10 x 4 = 40`.

---

## Fase 8 — Personas, equipos, competidores

### Paso 8.1: `_seed_participants()`

**Personas** (`get_or_create(first_name, last_name, defaults={...})`, names estables del usuario):

- CrossFit A: 2 personas (Principiantes Ind), 1 persona (Intermedios Ind), 4 personas (2 equipos × 2 de Principiantes Mixto).
- CrossFit B: 8 personas (2 equipos × 4 de Relevos 4).
- HYROX A: 2 personas (RX Ind).
- HYROX B: 2 personas (RX Ind).

**Teams** (solo equipos): cada `Team` requiere `competition_edition` + `competition_enabled_category` (de la Fase 5) + `name`. Nombre estable por equipo.

**TeamMembers:** linkean `team` + `person` (unique_together team+person).

**Competitores** (regla en `clean()`: INDIVIDUAL → person requerida/team NULL; TEAM → team requerido/person NULL):

| Edición | Competitor | tipo | vía |
|---------|------------|------|-----|
| CrossFit A | 2 categoría Principiantes Ind | INDIVIDUAL | person |
| CrossFit A | 1 categoría Intermedios Ind | INDIVIDUAL | person |
| CrossFit A | 2 categoría Principiantes Mixto | TEAM | team (2 TeamMembers c/u) |
| CrossFit B | 2 categoría Relevos 4 | TEAM | team (4 TeamMembers c/u) |
| HYROX A | 2 categoría RX Ind | INDIVIDUAL | person |
| HYROX B | 2 categoría RX Ind | INDIVIDUAL | person |

**Implementation note:** `competition_enabled_category` del competitor debe ser la habilitada en su edición. `registration_number` puede quedar vacío (`blank=True`) o asignarse secuencial estable (ej. `CFA-001`, ...) para repetibilidad.

### Paso 8.2: Verificación

Conteos: Personas = `4 + 8 + 2 + 2 = 16`; Teams = 4; TeamMembers = `(2×2) + (2×4) = 12`; Competitores = `3 + 2 + 2 + 2 = 9`.

---

## Fase 9 — Resultados por evento

### Paso 9.1: `_seed_results()`

Para cada `Event` de cada edición y para cada `Competitor` de esa edición, crear:

```python
EventCompetitor.objects.get_or_create(
    competitor=competitor,
    event=event,
    defaults={
        'result': "<valor>",  # string; formato según result_type
        'status': status_valid,
    },
)
```

- `result` con formato correcto por tipo (TIME "HH:MM:SS"/"MM:SS"; REPS/POINTS int; WEIGHT/DISTANCE decimal).
- `event_rank`/`score` se dejan `None` aquí (se calculan en Fase 10).
- `status` = catálogo `VALID` (de la Fase existente 0).
- unique_together competitor+event evita duplicados.

**Resultados sintáticos sugeridos (valores concretos de prueba con direcciones ASC/DESC que produzcan ordenes distintos):** definirlos en `Process.md` al momento de implementar (TABLAS_REV: p. ej. CrossFit A WOD1 (TIME): podio "04:36", "04:52", "05:10" para los 3 individuales, etc.).

### Paso 9.2: Verificación

Conteo EventCompetitor = nº de (Competitor × Event) por edición donde corresponde:
- CrossFit A: 3 individuales × 3 qualifier + 3 × 1 final + 2 equipos × 4 eventos = 21.
- CrossFit B: 2 equipos × 5 eventos = 10.
- HYROX A/B: 2 × 1 = 2 c/u.
Total = 35.

---

## Fase 10 — Calcular rankings (`event_rank` + `score`)

### Paso 10.1: `_compute_event_rankings()`

Para cada `Event` del sistema creado:

```python
EventRankingService.calculate_event_ranking(event)
```

Esto parsea resultados (`ResultParser`), ordena por dirección, aplica ranking denso y asigna `event_rank` + `score` por `ScoringRule` de la edición. **Es requisito para que el leaderboard muestre sitios puntuados.**

### Paso 10.2: Verificación

- `EventCompetitor` sin `event_rank` ni `score` = 0.
- Empates resultantes siguen patrón `1, 2, 2, 4`.

---

## Fase 11 — Idempotencia final del command

### Paso 11.1: Revisar `get_or_create` en cada helper

Claves estables: `Affiliation.name`, `Location.name`, `Competition.name`, `CompetitionEdition(competition, year)`, `CompetitionEnabledCategory`, `CompetitionStage`, `Event(stage, event_number)`, `ScoringRule(edition, position)`, `Person(first_name, last_name)`, `Team.name`, `TeamMember(team, person)`, `Competitor(person/team + edition + enabled_category)`, `EventCompetitor(competitor, event)`.

### Paso 11.2: Decisión de actualización

- Si un `EventCompetitor` ya existe con `result` distinto (cambio del usuario), actualizar `result` y eliminar `event_rank`/`score` para recalcular (`update_or_create`). **Documentar esta decisión en Process.md.**

### Paso 11.3: Verificación

Ejecutar `seed_data` dos veces → conteos de la Fase 8/9 no varían.

---

## Fase 12 — Verificación final

### Paso 12.1: Checks estáticos

```bash
python manage.py check --settings=config.settings.development
python manage.py spectacular --validate --settings=config.settings.development
```

### Paso 12.2: Suite de tests

```bash
python -m pytest tests --settings=config.settings.development
```

Debe seguir en verde (el seed no altera testgear). **Opcional:** agregar `tests/test_seed.py` que ejecute `call_command('seed_data')` dos veces y verifique idempotencia + conteos.

### Paso 12.3: Verificación API (con servidor corriendo)

```bash
python manage.py runserver --settings=config.settings.development
```

| Endpoint | Esperado |
|----------|----------|
| `GET /api/v1/competition-types/` | CROSSFIT + HYROX |
| `GET /api/v1/competitions/` | 4 competencias |
| `GET /api/v1/competition-categories/` | 7 + 6 = 13 categorías |
| `GET /api/v1/leaderboards/edition/{cf_a_id}/qualifier/` | Leaderboard con scores y posiciones (HTTP 200) |
| `GET /api/v1/leaderboards/edition/{cf_a_id}/final/` | Ranking independiente del qualifier (HTTP 200) |
| `GET /api/v1/leaderboards/edition/{cf_b_id}/qualifier/` | Equipos de 4 con scores |
| `GET /api/v1/leaderboards/edition/{hy_a_id}/qualifier/` | RX individual (HTTP 200) |

### Paso 12.4: Django Admin

Login como admin → revisar CompetitionEdition, Events, EventCompetitor (list_display muestra rank/score calculados).

---

## Fase 13 — Documentación

### Paso 13.1: `Process.md`

Registrar por fases: qué se hizo, datos definidos (tablas de cada sección), verificaciones y resultados.

### Paso 13.2: `RESULTADOS.md`

Resumen final: comandos, conteos confirmados, endpoints verificados, problemas encontrados y soluciones (p. ej. rank/score calculados tras seed).

### Paso 13.3: `README.md`

`[Según PROMPT sección 8]` — mención de `seed_data` ampliado con datos de ejemplo (opcional).

---

## Fase 14 — Cierre manual del usuario

El usuario debe ejecutar (fuera del agente):

```bash
docker compose up --build
docker compose exec web python manage.py seed_data
docker compose exec web python manage.py createsuperuser   # solo si falta
```

---

## Resumen de archivos a modificar

| # | Archivo | Tipo | Fase |
|---|---------|------|------|
| 1 | `apps/users/management/commands/seed_data.py` | modificar (ampliar) | 1-11 |
| 2 | `tests/test_seed.py` | crear (opcional) | 12 |
| 3 | `Process.md` | modificar | todas |
| 4 | `RESULTADOS.md` | modificar | 13 |
| 5 | `README.md` | modificar (opcional) | 13 |

**No se modifican:** modelos, migraciones, serializers, views, urls, services, API.

---

## Orden de ejecución recomendado

```
Fase 0 (línea base) → Fase 1 (estructura seed) → Fase 2 (categorías) → Fase 3 (aff/loc)
→ Fase 4 (competencias+ediciones) → Fase 5 (categorías habilitadas) → Fase 6 (stages+eventos)
→ Fase 7 (scoring rules) → Fase 8 (personas/equipos/competidores) → Fase 9 (resultados)
→ Fase 10 (cálculo de rankings) → Fase 11 (idempotencia) → Fase 12 (verificación)
→ Fase 13 (documentación) → Fase 14 (pasos manuales del usuario)
```

**Total estimado:** ~1 comando modificado + 1 test opcional + 3 docs. Sin cambios estructurales.