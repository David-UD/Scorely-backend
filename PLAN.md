# Plan de Implementación — Exponer `event_results` en el leaderboard (PROMPT.md, Parte II)

> Este plan reemplaza al plan anterior (Public GETs, ya completado y verificado). Documenta paso a paso cómo implementar la actualización pedida por el usuario y definida en la **Parte II de `PROMPT.md`** (sección nueva "Exponer `event_results` en el leaderboard de rankings"): enriquecer `LeaderboardEntrySerializer` y `CompetitionRankingService` para que el leaderboard devuelva el desglose de cada evento por competitor (`event_id`, `event_number`, `event_name`, `phase`, `result`, `event_rank`, `score`).
>
> **Alcance ejecutado por este plan: SOLO los cambios indicados. No ejecutar nada fuera de lo listado.**
>
> **Este plan NO ejecuta los cambios**: es la guía de implementación. Cada snippet debe verificarse contra el código real antes de aplicar.
>
> **Precondición (modelo):** este plan asume aplicada la **opción 1** acordada (refactor de modelos, sin migraciones): `Event` con FK directo `competition` y campo `phase` (`QUALIFIER`/`FINAL`), y **sin** `CompetitionStage`. Si el refactor aún no está aplicado, filtrar por el modelo vigente (`event__competition_stage__competition` / `event__competition_stage__stage_type`) hasta que se complete.

---

## Restricciones Globales

- No crear ramas git / no push / no commit (el agente no toca git sin pedido explícito del usuario).
- **NO ejecutar** `makemigrations`, `migrate`, `seed_data` ni `createsuperuser`: esta actualización **no genera migraciones** (sin cambios de modelo). No hay pasos de migración manuales.
- No modificar modelos (`Event`, `EventCompetitor`, `Competition`), ni `EventRankingService`, ni `ScoringService`.
- No cambiar rutas, permisos, filtros ni la estructura de `LeaderboardViewSet`.
- **Backward-compatible:** se conservan `event_ranks` y `event_scores` (listas planas). Solo se agrega `event_results`.
- No añadir comentarios al código salvo que se pidan.
- Documentar avances en `Process.md` al iniciar y finalizar cada fase.

---

## Contexto / Estado actual

- `apps/rankings/serializers.py:7-23` → `LeaderboardEntrySerializer` expone `rank`, `competitor_id`, `display_name`, `final_score`, `event_ranks` (lista de int) y `event_scores` (lista de int nullable). Las listas planas no permiten saber a qué evento pertenece cada valor.
- `apps/rankings/serializers.py:26-32` → `LeaderboardSerializer` (agrupa por categoría) — no se toca su estructura.
- `apps/rankings/services/competition_ranking_service.py`:
  - `calculate_competition_ranking(competition, stage)` (líneas 10-59) arma `competitor_scores` con `final_score`, `event_ranks`, `event_scores`.
  - `_rank_competitors()` (líneas 61-108) construye el dict rankeado final (pierde cualquier campo extra no listado).
- `apps/rankings/views.py:27-66` → `LeaderboardViewSet` (qualifier/final) obtiene competición + stage y llama al servicio; `serializer_class = LeaderboardSerializer`.
- `apps/rankings/services/final_qualification_service.py` → NO se toca en esta iteración (solo depende indirectamente del ranking).
- Tests actuales que llaman al servicio: `tests/test_rankings.py:167` y `:220` (`calculate_competition_ranking(competition, event.competition_stage)`).
- No existe aún en `PROMPT.md` la Parte II "Exponer event_results" (Fase 1 la incorpora).
- `apps/events/models.py:72` ya usa `related_name='event_results'` en `EventCompetitor.competitor` (acceso `competitor.event_results`). No es un conflicto con el campo de serializer a agregar, pero debe tenerse presente al nombrar objetos.

---

## Pre-requisitos antes de implementar

1. `.env` listo y entorno disponible (o `pip install -r requirements.txt`).
2. **Confirmar el estado del modelo** (opción 1): `Event.competition` y `Event.phase` presentes; `CompetitionStage` ausente. Si el código sigue roto a mitad del refactor, no empezar esta iteración: primero completar el refactor.
3. Conocer el código real de `apps/rankings/serializers.py`, `apps/rankings/services/competition_ranking_service.py`, `apps/rankings/views.py` y `tests/test_rankings.py` (verificar líneas antes de cada edición).
4. Suite de tests actual en verde antes de empezar (Fase 2 lo confirma).
5. Confirmar con el usuario la **estructura de `event_results`** (Fase 3): campos propuestos vs necesidad real del frontend.

---

## Fase 0 — Redactar la especificación en `PROMPT.md` (Parte II nueva)

> Objetivo: dejar asentada la "indicación" que guía esta iteración (pedido previo del usuario: "agrega al PROMPT.md para que el serializer/service de rankings exponga event_results").

### Paso 0.1: Insertar la nueva especificación en `PROMPT.md`

Insertar una nueva sección **Parte II** entre el final de la Parte II actual (línea ~249, tras `---`) y la **Parte III** (línea 252). Encabezado imprescindible:

- Título: **1. Título** → "Exponer `event_results` en el leaderboard de rankings".
- **2. Objetivo**: el frontend necesita saber qué evento corresponde a cada `event_ranks`/`event_scores`; se agrega `event_results` (desglose por evento).
- **3. Alcance**: serializers + servicio de rankings + tests; excluye modelos, migraciones, `LeaderboardViewSet`, `EventRankingService`, `event_ranks`/`event_scores`.
- **4. Cambio de modelo**: ninguno (sin migraciones).
- **5. Cambios en API**: solo se enriquece la respuesta del leaderboard (campo nuevo); sin cambios de rutas/permisos.
- **6. Lógica de negocio**: `CompetitionRankingService.calculate_competition_ranking()` debe incluir `event_results` en cada entrada.
- **7. Admin**: ninguno.
- **8. Documentación**: `Process.md`, `RESULTADOS.md`, `README.md`.
- **9. Detalle de implementación**: snipets de `EventResultSerializer`, campo nuevo en `LeaderboardEntrySerializer`, construcción de `event_results` en el servicio.
- **10. Pruebas requeridas**: tabla (presencia, longitud, consistencia suma vs `final_score`, backward-compat, caso vacío).
- **11. Criterios de aceptación**: `check`, `spectacular --validate`, pytest en verde.
- **12. Observaciones**: backward-compatible; `result` es string crudo; orden de eventos por `event_number`; consumo de bytes.

> Nota: esta fase es de especificación (solo `PROMPT.md`), no cambia código de la aplicación.
> Al final de esta fase, confirmar con el usuario que la especificación quedó como se esperaba **antes** de implementar (Parte III, punto 2 de `PROMPT.md`).

---

## Fase 1 — Descubrimiento y verificación de línea base

### Paso 1.1: Ejecutar verificaciones de referencia (solo lectura)

```bash
python manage.py check --settings=config.settings.development
python manage.py spectacular --validate --settings=config.settings.development
python -m pytest tests --settings=config.settings.development
```

**Criterio:** 0 issues, schema OK, suite completa en verde. Registrar en `Process.md` (nueva fila de iteración "Event results").
Si falla por el refactor de modelos sin terminar, **detenerse** y completar el refactor primero (no es parte de este plan).

### Paso 1.2: Releer los archivos objetivo

Verificar que las líneas citadas coinciden con el código real:
- `apps/rankings/serializers.py` (`LeaderboardEntrySerializer`, `LeaderboardSerializer`).
- `apps/rankings/services/competition_ranking_service.py` (`calculate_competition_ranking`, `_rank_competitors`).
- `apps/rankings/views.py` (acciones `qualifier`/`final`).
- `tests/test_rankings.py` y `tests/test_api.py` (patrón de tests de leaderboard).

---

## Fase 2 — Serializers: agregar `EventResultSerializer` y `event_results`

### Paso 2.1: Nuevo serializer `EventResultSerializer`

En `apps/rankings/serializers.py`, junto a los existentes:

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

### Paso 2.2: Agregar campo a `LeaderboardEntrySerializer`

```python
class LeaderboardEntrySerializer(serializers.Serializer):
    rank = serializers.IntegerField()
    competitor_id = serializers.IntegerField(source='competitor.id', read_only=True)
    display_name = serializers.SerializerMethodField()
    final_score = serializers.IntegerField()
    event_ranks = serializers.ListField(child=serializers.IntegerField())
    event_scores = serializers.ListField(
        child=serializers.IntegerField(allow_null=True),
        required=False,
    )
    event_results = EventResultSerializer(many=True, read_only=True)  # NUEVO
```

### Paso 2.3: Verificar schema

- `python manage.py spectacular --validate --settings=config.settings.development` → debe seguir limpio (drf-spectacular deriva el campo anidado sin warnings).

---

## Fase 3 — Servicio: construir y propagar `event_results`

### Paso 3.1: Ajustar `calculate_competition_ranking()`

En `apps/rankings/services/competition_ranking_service.py`:
- La firma actual recibe `stage` (verificar según modelo vigente). Para el modelo nuevo, filtrar por `competition` + `phase`:

```python
event_competitors = list(
    EventCompetitor.objects.filter(
        competitor=competitor,
        event__competition=competition,
        event__phase=phase,
    )
    .select_related('event')
    .order_by('event__event_number')
)
```

- Construir `event_results` **desde el mismo queryset** (evita N+1 y asegura orden consistente):

```python
event_results_list = [
    {
        'event_id': ec.event_id,
        'event_number': ec.event.event_number,
        'event_name': ec.event.name,
        'phase': ec.event.phase,
        'result': ec.result,
        'event_rank': ec.event_rank,
        'score': ec.score,
    }
    for ec in event_competitors
]
```

- Derivar `final_score`, `event_ranks` y `event_scores` del mismo recorrido (mantener el comportamiento actual de sumar `ec.score or 0`).
- Agregar `'event_results': event_results_list` al dict de `competitor_scores`.

> Si el refactor no está completo y se conserva `competition_stage`: usar `event__competition_stage=stage` (con `select_related('event__competition_stage')`) y `'phase': ec.event.competition_stage.stage_type`.

### Paso 3.2: Propagar `event_results` en `_rank_competitors()`

`_rank_competitors()` reconstruye el dict rankeado y **debe conservar `event_results`** (hoy solo copia `final_score`, `rank`, `event_ranks`, `event_scores`):

```python
ranked.append({
    'competitor': current['competitor'],
    'final_score': current['final_score'],
    'rank': rank,
    'event_ranks': current['event_ranks'],
    'event_scores': current['event_scores'],
    'event_results': current['event_results'],
})
```

### Paso 3.3: Confirmar integridad

- El dict retornado por `_rank_competitors()` es lo que `LeaderboardEntrySerializer` consume (vía `LeaderboardSerializer`). Verificar que `event_results` llega como lista de dicts serializable.

---

## Fase 4 — Views y API (verificación, sin cambios de ruta)

### Paso 4.1: Confirmar que `LeaderboardViewSet` no requiere cambios

- `apps/rankings/views.py` sigue llamando al servicio y serializando con `LeaderboardSerializer`; el nuevo campo se expone automáticamente.
- Si la firma del servicio cambia de `(competition, stage)` a `(competition, phase)`, adaptar las llamadas en `views.py`: accion `qualifier` → `Event.Phase.QUALIFIER`; accion `final` → `Event.Phase.FINAL`.

### Paso 4.2: Dejar sin tocar `final_qualification_service.py`

- No forma parte del contrato de respuesta; solo reusa `calculate_competition_ranking`. Verificar que su llamada compila con la nueva firma (misma adaptación que en views).

---

## Fase 5 — Tests

### Paso 5.1: Actualizar `tests/test_rankings.py`

- Adaptar las llamadas existentes a `calculate_competition_ranking(...)` (líneas ~167 y ~220) a la nueva firma (`competition`, `phase`).
- Agregar a `TestCompetitionRankingService`:
  - `test_event_results_present` → cada entry tiene `event_results` con `len == número de eventos`.
  - `test_event_results_structure` → cada elemento expone `event_id`, `event_number`, `event_name`, `phase`, `result`, `event_rank`, `score`.
  - `test_event_results_scores_sum_to_final_score` → `sum(e['score'] for e in entry['event_results']) == entry['final_score']` (usa fixture `scoring_rules`).
  - `test_event_results_ordered_by_event_number` → el orden sigue `Event.Meta.ordering`.
  - `test_event_results_empty` → competitor sin resultados → `event_results == []`.

### Paso 5.2: Agregar test de API en `tests/test_api.py` (`TestAPIRankings`)

- Crear un evento + `EventCompetitor` + `EventRankingService.calculate_event_ranking()` (para asegurar `event_rank`/`score`), y verificar:
  - `GET /api/v1/leaderboards/competition/{id}/qualifier/` → 200.
  - `response.data['results'][0]['entries'][0]` contiene `event_results`.
  - La estructura y la suma concuerdan.

### Paso 5.3: Ejecutar la suite nueva

```bash
python -m pytest tests/test_rankings.py tests/test_api.py --settings=config.settings.development -v
```

**Criterio:** casos nuevos en verde y existentes intactos.

---

## Fase 6 — Verificación completa

### Paso 6.1: Suite completa

```bash
python -m pytest tests --settings=config.settings.development
```

**Criterio:** verde (suite previa + tests nuevos).

### Paso 6.2: Checks estáticos

```bash
python manage.py check --settings=config.settings.development
python manage.py spectacular --validate --settings=config.settings.development
```

**Criterio:** 0 issues, schema OpenAPI válido (incluye `event_results` documentado).

### Paso 6.3: Confirmar migraciones

```bash
python manage.py makemigrations --check --settings=config.settings.development
```

**Criterio:** "No changes detected" (sin cambios de modelo; **si** se detecta migración pendiente por el refactor opción 1, es esperada y **no** se genera aquí: informarla al usuario).

### Paso 6.4: Smoke test manual (opcional)

```bash
python manage.py runserver --settings=config.settings.development
```

Con datos de seed: `GET /api/v1/leaderboards/competition/{id}/qualifier/` → cada `entry` incluye `event_results` con `event_name`, `result` (string crudo, p. ej. "04:36"), `event_rank` y `score`.

---

## Fase 7 — Documentación

### Paso 7.1: `Process.md`

- Nueva fila de iteración "Event results" en la tabla de estado.
- Registrar: especificación (Fase 0), archivos modificados, adaptación de firma del servicio, tests añadidos, resultados de verificación.

### Paso 7.2: `RESULTADOS.md`

- Resumen: serializers/servicio/tests modificados (conteo final), verificaciones OK, nota de compatibilidad (se conservan `event_ranks`/`event_scores`).

### Paso 7.3: `README.md`

- Sección de leaderboards/API: indicar que la respuesta incluye `event_results` (desglose por evento) con un ejemplo de la estructura.

---

## Fase 8 — Cierre

### Paso 8.1: Reporte final al usuario

Resumen de: qué se cambió (2 archivos de código: serializers + servicio; 1-2 de tests), verificaciones, y **pasos manuales del usuario** (ninguno de migración; opcional smoke test 6.4; si quedó migración detectada del refactor, indicar ejecutar `makemigrations`/`migrate` manualmente).

### Paso 8.2: No ejecutar nada pendiente

Sin migraciones/seed/createsuperuser pendientes para esta iteración.

---

## Resumen de archivos a modificar

| # | Archivo | Tipo | Fase |
|---|---------|------|------|
| 1 | `PROMPT.md` | modificar (nueva Parte II "Exponer event_results") | 0 |
| 2 | `apps/rankings/serializers.py` | modificar (`EventResultSerializer` + campo `event_results`) | 2 |
| 3 | `apps/rankings/services/competition_ranking_service.py` | modificar (construir/propagar `event_results`) | 3 |
| 4 | `apps/rankings/views.py` | modificar **solo si** cambia la firma del servicio | 4 |
| 5 | `apps/rankings/services/final_qualification_service.py` | modificar **solo si** cambia la firma del servicio | 4 |
| 6 | `tests/test_rankings.py` | modificar (firma + tests de `event_results`) | 5 |
| 7 | `tests/test_api.py` | modificar (test API de `event_results`) | 5 |
| 8 | `Process.md` | modificar (registro de iteración) | 0,1,6,7 |
| 9 | `RESULTADOS.md` | modificar | 7 |
| 10 | `README.md` | modificar (sección API/leaderboard) | 7 |

**No se modifican:** modelos, migraciones, `EventRankingService`, `ScoringService`, `LeaderboardViewSet`, `config/settings/base.py`.

---

## Orden de ejecución recomendado

```
Fase 0 (especificación en PROMPT.md) → Fase 1 (línea base + descubrimiento)
→ Fase 2 (serializers) → Fase 3 (servicio) → Fase 4 (views/API verificación)
→ Fase 5 (tests) → Fase 6 (verificación completa) → Fase 7 (documentación) → Fase 8 (cierre)
```

**Total estimado:** 2-4 archivos de código según firma del servicio + 1-2 archivos de tests + 3-4 docs + `PROMPT.md`. Sin cambios en el modelo de datos ni migraciones.