# Plan de Implementación — Abrir GET públicos de solo lectura (PROMPT.md, Parte II)

> Este plan reemplaza al plan anterior (Seed Update, ya completado y verificado). Documenta paso a paso cómo implementar la actualización definida en la **Parte II de `PROMPT.md`**: abrir la lectura pública (GET) de `competitions`, `competition-stages` y `events` para que el frontend consulta público funcione sin autenticación, manteniendo las escrituras protegidas por JWT.
>
> **Alcance ejecutado por este plan: SOLO los cambios indicados. No ejecutar nada fuera de lo listado.**
>
> **Este plan NO ejecuta los cambios**: es la guía de implementación. Cada archivo modificado debe verificar los snippets aquí propuestos contra el código real antes de aplicar.

---

## Restricciones Globales

- No crear ramas git / no push / no commit (el agente no toca git sin pedido explícito del usuario).
- **NO ejecutar** `makemigrations`, `migrate`, `seed_data` ni `createsuperuser`: esta actualización **no genera migraciones** (sin cambios de modelo), por lo que no hay pasos de migración manuales.
- No modificar modelos, serializers, services, urls ni la lógica de ranking/puntuación.
- No cambiar `LeaderboardViewSet` (ya público con `AllowAny`).
- No cambiar `config/settings/base.py` (se conserva `DEFAULT_PERMISSION_CLASSES = IsAuthenticated` como default global).
- Seguir el patrón existente de `permission_classes` por ViewSet (como ya hace `LeaderboardViewSet`).
- No añadir comentarios al código salvo que se pidan.
- Documentar avances en `Process.md` al iniciar y finalizar cada fase.

---

## Contexto / Estado actual

- `config/settings/base.py:86-87` define `DEFAULT_PERMISSION_CLASSES = ('rest_framework.permissions.IsAuthenticated',)`. Solo `LeaderboardViewSet` declara `permission_classes = [AllowAny]` (`apps/rankings/views.py:19`).
- Endpoints afectados hoy (exigen JWT por defecto):
  - `CompetitionViewSet` (`apps/competitions/views.py:33-42`) → `GET /api/v1/competitions/` y `GET /api/v1/competitions/{id}/`.
  - `CompetitionStageViewSet` (`apps/events/views.py:37-40`) → `GET /api/v1/competition-stages/?competition={id}`.
  - `EventViewSet` (`apps/events/views.py:53-57`) → `GET /api/v1/events/?competition_stage={id}`.
- `CompetitionSerializer` ya embebe `competition_type`, `status`, `affiliation` y `location` (solo lectura) →
  la página pública de detalle no requiere llamadas adicionales a catálogos.
- Los tres ViewSets mantienen filtros (django-filter) y búsquedas existentes: no se tocan.
- Fixtures disponibles en `tests/conftest.py`: `user`, `superadmin`, `competition_type`, `status_competition`, `affiliation`, `location`, `competition`, `stage_qualifier`, `stage_final`, `event`, etc.
- Patrón de tests API en `tests/test_api.py`: `rest_framework.test.APIClient`, `force_authenticate(user=...)`; anónimo = `APIClient()` sin autenticar.
- `apps/users/permissions.py` contiene `IsSuperAdmin` (permiso global) y `IsCompetitionAdmin` (a nivel objeto). No se modifica salvo que se opte por la alternativa del mixin (ver Fase 1).

---

## Pre-requisitos antes de implementar

1. `.env` listo y entorno levantado (o `pip install -r requirements.txt` en local).
2. Conocer el código real de los archivos objetivo (verificar líneas antes de cada edición).
3. Suite de tests actual en verde (81 tests) antes de empezar (Fase 0 lo confirma).
4. Confirmar con el usuario el **enfoque** (Fase 1): `IsAuthenticatedOrReadOnly` directo vs mixin.

---

## Fase 0 — Preparación y verificación inicial

### Paso 0.1: Verificaciones de línea base (solo lectura)

```bash
python manage.py check --settings=config.settings.development
python manage.py spectacular --validate --settings=config.settings.development
python manage.py makemigrations --check --settings=config.settings.development
python -m pytest tests --settings=config.settings.development
```

**Criterio:** 0 issues, schema OK, "No changes" en migraciones, suite completa en verde (81 passed).
Registrar en `Process.md` (nueva fila de iteración "Public GETs").

### Paso 0.2: Confirmar el estado del frontend

- `PROMPT-frontend.md` no está presente actualmente en el repo (verificado). Si reaparece antes de implementar, revisar su sección 12 y la tabla de endpoints (Fase 6 lo documentará si existe).

---

## Fase 1 — Decisión de enfoque de permisos

### Paso 1.1: Elegir opción

| Opción | Descripción | Juicio |
|--------|-------------|--------|
| **A (recomendado)** | Añadir `permission_classes = (IsAuthenticatedOrReadOnly,)` en cada uno de los 3 ViewSets objetivo. | Simple, explícito, consistente con `LeaderboardViewSet`. Sin archivos nuevos. |
| **B (alternativa)** | Crear mixin `PublicReadOnly(IsAuthenticatedOrReadOnly)` en `apps/users/permissions.py` y aplicarlo a los 3 ViewSets. | Centraliza la regla, pero añade abstracción innecesaria para solo 3 vistas. |

**Decisión propuesta:** Opción A (más simple y consistente con el patrón existente). Confirmar con el usuario antes de implementar; si elige B, adaptar los pasos 2.2 y 3.2 para importar el mixin en lugar de la clase base.

### Paso 1.2: Verificación

Registrar la decisión en `Process.md`.

---

## Fase 2 — Abrir lectura de `CompetitionViewSet`

### Paso 2.1: Importar la clase de permiso

En `apps/competitions/views.py`, añadir el import (junto a los existentes de `rest_framework`):

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly
```

### Paso 2.2: Declarar `permission_classes` en `CompetitionViewSet`

`apps/competitions/views.py` (clase actual en líneas 33-42). Añadir el atributo justo debajo del `queryset` (patrón de `LeaderboardViewSet`):

```python
class CompetitionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    ...
```

**No cambiar** `get_serializer_class()` ni filtros.

### Paso 2.3: Verificación estática

- `python manage.py check --settings=config.settings.development`.

---

## Fase 3 — Abrir lectura de `CompetitionStageViewSet` y `EventViewSet`

### Paso 3.1: Importar la clase de permiso

En `apps/events/views.py`, añadir:

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly
```

### Paso 3.2: `CompetitionStageViewSet`

`apps/events/views.py:37-40`. Añadir `permission_classes`:

```python
class CompetitionStageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = CompetitionStage.objects.all()
    serializer_class = CompetitionStageSerializer
    filterset_fields = ('competition', 'stage_type')
```

### Paso 3.3: `EventViewSet`

`apps/events/views.py:53-57`:

```python
class EventViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_fields = ('competition_stage',)
    search_fields = ('name',)
```

### Paso 3.4: Verificación estática

- `python manage.py check --settings=config.settings.development` (0 issues).

---

## Fase 4 — Tests de permisos públicos (nuevos)

> Ubicación: `tests/test_api.py`, siguiendo el patrón existente de `APIClient`. Reutilizar fixtures de `conftest.py` (`competition`, `stage_qualifier`, `event`, `superadmin`, etc.).
> Nota: las listas responden con paginación (`response.data['results']`).

### Paso 4.1: Añadir clase `TestAPIPublicReadOnly` al final de `tests/test_api.py`

```python
@pytest.mark.django_db
class TestAPIPublicReadOnly:
    # --- competitions: lectura pública, escritura protegida ---
    def test_competition_list_public(self, competition):
        client = APIClient()
        response = client.get('/api/v1/competitions/')
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    def test_competition_detail_public(self, competition):
        client = APIClient()
        response = client.get(f'/api/v1/competitions/{competition.id}/')
        assert response.status_code == 200
        assert response.data['competition_type']['code'] == 'CROSSFIT'
        assert 'status' in response.data
        assert 'affiliation' in response.data
        assert 'location' in response.data

    def test_competition_create_requires_auth(self, competition_type, status_competition, affiliation, location):
        client = APIClient()
        data = {  # mismo payload que TestAPICompetitions.test_create_competition
            'name': 'Público Intruso',
            'competition_type': competition_type.id,
            'status': status_competition.id,
            'affiliation': affiliation.id,
            'location': location.id,
            'description': '',
            'start_date': '2027-07-01',
            'end_date': '2027-07-03',
            'slug': 'publico-intruso',
        }
        response = client.post('/api/v1/competitions/', data, format='json')
        assert response.status_code == 401

    def test_competition_destroy_requires_auth(self, competition):
        client = APIClient()
        response = client.delete(f'/api/v1/competitions/{competition.id}/')
        assert response.status_code == 401

    def test_competition_filter_public(self, competition):
        client = APIClient()
        response = client.get(f'/api/v1/competitions/?status={competition.status.id}')
        assert response.status_code == 200

    # --- competition-stages ---
    def test_stage_list_public(self, stage_qualifier):
        client = APIClient()
        response = client.get(
            f'/api/v1/competition-stages/?competition={stage_qualifier.competition.id}'
        )
        assert response.status_code == 200
        assert len(response.data['results']) >= 1

    def test_stage_create_requires_auth(self, competition):
        client = APIClient()
        data = {
            'competition': competition.id,
            'stage_type': 'QUALIFIER',
            'qualification_count': 5,
            'order': 1,
        }
        response = client.post('/api/v1/competition-stages/', data, format='json')
        assert response.status_code == 401

    # --- events ---
    def test_event_list_public(self, event):
        client = APIClient()
        response = client.get(
            f'/api/v1/events/?competition_stage={event.competition_stage.id}'
        )
        assert response.status_code == 200
        assert len(response.data['results']) == 1

    def test_event_create_requires_auth(self, event):
        client = APIClient()
        data = {
            'competition_stage': event.competition_stage.id,
            'event_number': 99,
            'name': 'WOD Intruso',
            'event_result_type': event.event_result_type_id,
            'rank_direction': event.rank_direction_id,
        }
        response = client.post('/api/v1/events/', data, format='json')
        assert response.status_code == 401

    # --- regresión con autenticación ---
    def test_public_reads_work_with_superadmin(self, superadmin, competition,
                                               stage_qualifier, event):
        client = APIClient()
        client.force_authenticate(user=superadmin)
        assert client.get('/api/v1/competitions/').status_code == 200
        assert client.get(
            f'/api/v1/competition-stages/?competition={competition.id}').status_code == 200
        assert client.get(
            f'/api/v1/events/?competition_stage={stage_qualifier.id}').status_code == 200

    # --- leaderboards siguen públicos ---
    def test_leaderboard_still_public(self, competition):
        client = APIClient()
        response = client.get(
            f'/api/v1/leaderboards/competition/{competition.id}/qualifier/'
        )
        assert response.status_code in (200, 404)
```

### Paso 4.2: Verificar campos del serializer antes de escribir el test de detalle

- Confirmar en `apps/competitions/serializers.py` (`CompetitionSerializer`) que los campos anidados se llaman `competition_type`, `status`, `affiliation`, `location` (verificado: sí). Ajustar el test si cambia algo.

### Paso 4.3: Ejecutar los tests nuevos

```bash
python -m pytest tests/test_api.py --settings=config.settings.development -v
```

**Criterio:** todos los casos nuevos en verde y sin cambios en los existentes (uno a uno de los asserts:
el POST/DELETE anónimo devuelve **401**; el GET anónimo devuelve **200**).

---

## Fase 5 — Verificación completa

### Paso 5.1: Suite completa

```bash
python -m pytest tests --settings=config.settings.development
```

**Criterio:** verde, con los tests nuevos añadidos (81 existentes + ~11 nuevos ≈ 92).

### Paso 5.2: Checks estáticos

```bash
python manage.py check --settings=config.settings.development
python manage.py spectacular --validate --settings=config.settings.development
```

**Criterio:** 0 issues, schema OpenAPI válido.

### Paso 5.3: Confirmar que NO hay migraciones

```bash
python manage.py makemigrations --check --settings=config.settings.development
```

**Criterio:** "No changes detected" (no se generan migraciones; no hay tareas manuales de migración).

### Paso 5.4: Smoke test manual (opcional, con server corriendo)

```bash
python manage.py runserver --settings=config.settings.development
```

| Endpoint | Anónimo (sin header) | Esperado |
|----------|----------------------|----------|
| `GET /api/v1/competitions/` | sin token | 200 + listado |
| `GET /api/v1/competitions/{id}/` | sin token | 200 + detalle con type/status/affiliation/location |
| `GET /api/v1/competition-stages/?competition={id}` | sin token | 200 |
| `GET /api/v1/events/?competition_stage={id}` | sin token | 200 |
| `POST /api/v1/events/` | sin token | 401 |
| `GET /api/v1/leaderboards/competition/{id}/qualifier/` | sin token | 200 (sin cambios) |

---

## Fase 6 — Documentación

### Paso 6.1: `Process.md`

- Agregar fila de iteración "Public GETs" en la tabla de estado.
- Registrar por fase: decisión de enfoque (Fase 1), ediciones hechas (Fases 2-3), tests añadidos (Fase 4), resultados de verificación (Fase 5).

### Paso 6.2: `RESULTADOS.md`

- Resumen final: archivos modificados, tests añadidos (conteo final), verificaciones OK, problema/solución si lo hubo (p. ej. si `IsAuthenticatedOrReadOnly` afectara algún detalle del schema o si la paginación interfiere en un assert).

### Paso 6.3: `README.md` — secciones API y seguridad

- En la nota tras la tabla de la API (línea ~177): indicar que además de los leaderboards, los GET de `competitions`, `competition-stages` y `events` son **públicos de solo lectura**; las escrituras siguen requiriendo JWT.
- Si existe sección de seguridad que liste "Leaderboards públicos", ampliarla con "Lectura pública de competencias/etapas/eventos".

### Paso 6.4: `PROMPT-frontend.md` (si el archivo existe/regresa)

- Sección 12: marcar la decisión como **resuelta** (opción "abrir GET públicos" implementada).
- Tabla de endpoints: las filas marcadas como "Pública pendiente (hoy JWT)" → "Pública (AllowAny)".
- Estado actual verificable: el archivo no está en el repo en este momento → si al implementar no existe, omitirlo y anotarlo en `Process.md`.

---

## Fase 7 — Cierre

### Paso 7.1: Reporte final al usuario

Resumen de: qué se cambió (3 archivos de código si se elige Opción A), tests añadidos, verificaciones, y **pasos manuales del usuario** (ninguno de migración; opcional smoke test del punto 5.4).

### Paso 7.2: No ejecutar nada pendiente

Sin migraciones/seed/createsuperuser pendientes. Única acción opcional del usuario: recrear/inspeccionar `PROMPT-frontend.md` para que refleje el estado público del backend.

---

## Resumen de archivos a modificar

| # | Archivo | Tipo | Fase |
|---|---------|------|------|
| 1 | `apps/competitions/views.py` | modificar (`CompetitionViewSet` + import) | 2 |
| 2 | `apps/events/views.py` | modificar (`CompetitionStageViewSet`, `EventViewSet` + import) | 3 |
| 3 | `tests/test_api.py` | modificar (nueva clase `TestAPIPublicReadOnly`) | 4 |
| 4 | `Process.md` | modificar (registro de iteración) | 0,1,6 |
| 5 | `RESULTADOS.md` | modificar | 6 |
| 6 | `README.md` | modificar (sección API/seguridad) | 6 |
| 7 | `PROMPT-frontend.md` | modificar **si existe** (sección 12 + tabla) | 6 |

**No se modifican:** modelos, migraciones, serializers, services, urls, `config/settings/base.py`,
`LeaderboardViewSet`, `apps/users/permissions.py` (salvo Opción B en Fase 1).

---

## Orden de ejecución recomendado

```
Fase 0 (línea base) → Fase 1 (decisión de enfoque) → Fase 2 (CompetitionViewSet)
→ Fase 3 (Stage + Event ViewSets) → Fase 4 (tests de permisos) → Fase 5 (verificación completa)
→ Fase 6 (documentación) → Fase 7 (cierre y reporte)
```

**Total estimado:** 2 archivos de código + 1 archivo de tests + 3-4 docs. Sin cambios en el modelo de datos.