# Plan de Implementación — Scorely Backend

## Restricciones Globales

- No crear ramas git.
- No realizar push.
- No subir a git.
- Avisar al usuario antes de ejecutar migraciones manuales (`makemigrations`, `migrate`).
- Toda la lógica de negocio en `services/`, nunca en `views/`.
- Nunca almacenar credenciales en código.
- Nunca confiar únicamente en el frontend.

---

## Fase 0 — Infraestructura y Andamiaje

### Paso 0.1: Crear estructura de directorios

```
scorely/
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── apps/
│   ├── __init__.py
│   ├── users/
│   ├── competitions/
│   ├── participants/
│   ├── events/
│   ├── scoring/
│   └── rankings/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── ...
├── manage.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── pytest.ini
└── PROMPT.md
```

### Paso 0.2: Crear `.env.example`

```
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://scorely_user:scorely_pass@db:5432/scorely_db
POSTGRES_DB=scorely_db
POSTGRES_USER=scorely_user
POSTGRES_PASSWORD=scorely_pass
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### Paso 0.3: Crear `.gitignore`

Ignorar: `__pycache__/`, `*.pyc`, `.env`, `db.sqlite3`, `*.egg-info/`, `.pytest_cache/`, `staticfiles/`, `media/`, `.idea/`, `.vscode/`

### Paso 0.4: Crear `requirements.txt`

```
Django==4.2.*
djangorestframework==3.14.*
djangorestframework-simplejwt==5.3.*
django-filter==23.*
drf-spectacular==0.27.*
Pillow==10.*
psycopg2-binary==2.9.*
python-decouple==3.8.*
pytest==7.*
pytest-django==4.*
pytest-cov==4.*
```

### Paso 0.5: Crear `Dockerfile`

- Base: `python:3.8.10-slim`
- Instalar dependencias del sistema (`libpq-dev`, `gcc`)
- Copiar `requirements.txt`, instalar dependencias
- Copiar código de la app
- Exponer puerto 8000
- CMD: `gunicorn config.wsgi:application --bind 0.0.0.0:8000`

### Paso 0.6: Crear `docker-compose.yml`

Servicios:
- `web`: build from Dockerfile, volume del código, depende de `db`, expone 8000
- `db`: imagen `postgres:15`, variables de entorno, volumen persistente, puerto 5432

### Paso 0.7: Crear `manage.py`

Estándar de Django con `DJANGO_SETTINGS_MODULE=config.settings.development`.

### Paso 0.8: Crear settings

**`config/settings/base.py`:**
- `INSTALLED_APPS` base (django apps)
- `ROOT_URLCONF = 'config.urls'`
- `WSGI_APPLICATION = 'config.wsgi.application'`
- `AUTH_USER_MODEL = 'users.User'`
- `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'`
- Carga de variables de entorno con `python-decouple`

**`config/settings/development.py`:**
- Hereda de `base`
- `DEBUG = True`
- `ALLOWED_HOSTS = ['*']`
- Configuración PostgreSQL con `DATABASE_URL`
- `CORS_ALLOW_ALL_ORIGINS = True`

**`config/settings/production.py`:**
- Hereda de `base`
- `DEBUG = False`
- `ALLOWED_HOSTS` desde env
- CORS restrictivo

**`config/settings/__init__.py`:** Vacío.

### Paso 0.9: Crear `config/urls.py`

- Incluir `admin/`
- Incluir `api/v1/` (urlpatterns vacío por ahora)
- Incluir schema de drf-spectacular

### Paso 0.10: Crear `config/asgi.py` y `config/wsgi.py`

Estándar de Django apuntando a `config.settings.development`.

### Paso 0.11: Crear `pytest.ini`

```ini
[pytest]
DJANGO_SETTINGS_MODULE=config.settings.development
python_files = tests.py test_*.py *_tests.py
addopts = --verbose
```

---

## Fase 1 — App `users` (Sistema de Usuarios)

### Paso 1.1: Crear la app

```bash
python manage.py startapp users apps/users
```

### Paso 1.2: Modelo `User` (Custom)

Archivo: `apps/users/models.py`

Campos:
- `email` (EmailField, UNIQUE, login)
- `first_name` (CharField, max_length=150)
- `last_name` (CharField, max_length=150)
- `is_active` (BooleanField, default=True)
- `is_staff` (BooleanField, default=False)
- `created_at` (DateTimeField, auto_now_add)
- `updated_at` (DateTimeField, auto_now)

Herencia: `AbstractBaseUser` + `PermissionsMixin`

Manager: `UserManager` con `create_user(email, password, **extra_fields)` y `create_superuser(email, password, **extra_fields)`.

`USERNAME_FIELD = 'email'`
`REQUIRED_FIELDS = ['first_name', 'last_name']`

### Paso 1.3: Modelo `Role`

Archivo: `apps/users/models.py`

Campos:
- `code` (CharField, max_length=20, UNIQUE) — `SUPERADMIN`, `ADMIN`
- `name` (CharField, max_length=50)

`__str__` retorna `code`.

### Paso 1.4: Relación `User` → `Role`

Opción A: Campo `role` FK en `User`.
Opción B: Tabla intermedia `UserRole`.

Según el PROMPT, Role es tabla independiente y los roles son `SUPERADMIN` y `ADMIN`. La relación más simple es un FK directo en User.

Agregar a `User`:
- `role` (ForeignKey → Role, null=True, blank=True)

### Paso 1.5: Modelo `CompetitionEditionAdmin`

Archivo: `apps/users/models.py` (o en `apps/competitions/models.py` — decidirUbicación)

Campos:
- `user` (ForeignKey → User)
- `competition_edition` (ForeignKey → CompetitionEdition)

Restricción: `UNIQUE(user, competition_edition)`

> Este modelo depende de `CompetitionEdition` que se crea en la Fase 2. Se creará la migración pendiente después de ambas fases.

### Paso 1.6: Admin de `User` y `Role`

- `list_display`: email, first_name, last_name, role, is_active
- `search_fields`: email, first_name, last_name
- `list_filter`: role, is_active
- `ordering`: email

### Paso 1.7: Tests de `users`

- Crear usuario con `create_user`.
- Login con email + password.
- Email único (duplicado lanza error).
- Rol asignado correctamente.

---

## Fase 2 — App `competitions` (Competencias y Catálogos)

### Paso 2.1: Crear la app

```bash
python manage.py startapp competitions apps/competitions
```

### Paso 2.2: Modelo `CompetitionType`

Campos:
- `code` (CharField, max_length=20, UNIQUE) — `CROSSFIT`, `HYROX`
- `name` (CharField, max_length=100)

### Paso 2.3: Modelo `Affiliation`

Campos:
- `name` (CharField, max_length=200)
- `description` (TextField, blank=True)
- `logo` (ImageField, upload_to='affiliations/', blank=True, null=True)
- `city` (CharField, max_length=100)
- `state` (CharField, max_length=100)
- `country` (CharField, max_length=100)

### Paso 2.4: Modelo `Location`

Campos:
- `name` (CharField, max_length=200)
- `address` (CharField, max_length=300)
- `city` (CharField, max_length=100)
- `state` (CharField, max_length=100)
- `country` (CharField, max_length=100)
- `latitude` (DecimalField, max_digits=9, decimal_places=6, null=True, blank=True)
- `longitude` (DecimalField, max_digits=9, decimal_places=6, null=True, blank=True)

### Paso 2.5: Modelo `Competition`

Campos:
- `competition_type` (FK → CompetitionType)
- `affiliation` (FK → Affiliation)
- `location` (FK → Location)
- `name` (CharField, max_length=200)
- `description` (TextField, blank=True)

### Paso 2.6: Modelo `CompetitionEdition`

Campos:
- `competition` (FK → Competition)
- `year` (PositiveIntegerField)
- `start_date` (DateField)
- `end_date` (DateField)
- `status` (CharField, choices) — `DRAFT`, `PUBLISHED`, `FINISHED`, `CANCELLED`

Restricción: `UNIQUE(competition, year)`

### Paso 2.7: Completar `CompetitionEditionAdmin`

Si se definió en `apps/users`, asegurar que la ForeignKey apunte correctamente. Si se define aquí, importar desde `users`.

### Paso 2.8: Admin de competiciones

Registrar todos los modelos con configuración apropiada.

### Paso 2.9: Tests de competiciones

- Crear CompetitionType, Affiliation, Location.
- Crear Competition con sus FK.
- Crear CompetitionEdition con año único.
- Duplicado (misma competencia + año) lanza error.
- Transiciones de estado.

---

## Fase 3 — App `participants` (Personas, Equipos, Competidores)

### Paso 3.1: Crear la app

```bash
python manage.py startapp participants apps/participants
```

### Paso 3.2: Modelo `Person`

Campos:
- `first_name` (CharField, max_length=150)
- `last_name` (CharField, max_length=150)
- `birth_date` (DateField, null=True, blank=True)
- `gender` (CharField, max_length=20, blank=True)
- `profile_photo` (ImageField, upload_to='persons/', blank=True, null=True)
- `affiliation` (FK → Affiliation, null=True, blank=True)

### Paso 3.3: Modelo `Team`

Campos:
- `competition_edition` (FK → CompetitionEdition)
- `competition_enabled_category` (FK → CompetitionEnabledCategory) — pendiente hasta Fase 4
- `affiliation` (FK → Affiliation, null=True, blank=True)
- `name` (CharField, max_length=200)

### Paso 3.4: Modelo `TeamMember`

Campos:
- `team` (FK → Team)
- `person` (FK → Person)

Restricción: `UNIQUE(team, person)`

### Paso 3.5: Modelo `Competitor`

Campos:
- `competition_edition` (FK → CompetitionEdition)
- `competitor_type` (CharField, choices) — `INDIVIDUAL`, `TEAM`
- `person` (FK → Person, null=True, blank=True)
- `team` (FK → Team, null=True, blank=True)
- `registration_number` (CharField, max_length=50, blank=True)
- `competition_enabled_category` (FK → CompetitionEnabledCategory)

Validación en `clean()` o `save()`:
- Si `competitor_type == 'INDIVIDUAL'`: `person` requerido, `team` NULL.
- Si `competitor_type == 'TEAM'`: `team` requerido, `person` NULL.

### Paso 3.6: Admin de participantes

Registrar Person, Team, TeamMember, Competitor.

### Paso 3.7: Tests de participantes

- Crear Person.
- Crear Team para una edición.
- Agregar TeamMember (único por team+person).
- Crear Competitor INDIVIDUAL con person.
- Crear Competitor TEAM con team.
- Intentar crear Competitor con ambos lanza error.
- Intentar crear Competitor sin person ni team lanza error.

---

## Fase 4 — App `events` (Categorías, Fases, Eventos, Resultados)

### Paso 4.1: Crear la app

```bash
python manage.py startapp events apps/events
```

### Paso 4.2: Modelo `CompetitionCategory`

Campos:
- `name` (CharField, max_length=100, UNIQUE)
- `min_members` (PositiveIntegerField, default=1)
- `max_members` (PositiveIntegerField, default=1)

### Paso 4.3: Modelo `CompetitionEnabledCategory`

Campos:
- `competition_edition` (FK → CompetitionEdition)
- `competition_category` (FK → CompetitionCategory)

Restricción: `UNIQUE(competition_edition, competition_category)`

### Paso 4.4: Completar FK en `Team` y `Competitor`

Ahora que `CompetitionEnabledCategory` existe, las ForeignKey en Team y Competitor apuntan correctamente. Verificar migraciones.

### Paso 4.5: Modelo `CompetitionStage`

Campos:
- `competition_edition` (FK → CompetitionEdition)
- `stage_type` (CharField, choices) — `QUALIFIER`, `FINAL`
- `qualification_count` (PositiveIntegerField, default=0)
- `order` (PositiveIntegerField)

Validación: solo un QUALIFIER y un FINAL por edición.

### Paso 4.6: Modelo `EventResultType`

Campos:
- `code` (CharField, max_length=20, UNIQUE) — `TIME`, `REPS`, `WEIGHT`, `DISTANCE`, `POINTS`
- `name` (CharField, max_length=50)

### Paso 4.7: Modelo `RankDirection`

Campos:
- `code` (CharField, max_length=10, UNIQUE) — `ASC`, `DESC`
- `name` (CharField, max_length=50)

### Paso 4.8: Modelo `Event`

Campos:
- `competition_stage` (FK → CompetitionStage)
- `event_number` (PositiveIntegerField)
- `name` (CharField, max_length=200)
- `description` (TextField, blank=True)
- `event_result_type` (FK → EventResultType)
- `rank_direction` (FK → RankDirection)

Restricción: `UNIQUE(competition_stage, event_number)`

### Paso 4.9: Modelo `StatusEventCompetitor`

Campos:
- `code` (CharField, max_length=20, UNIQUE) — `PENDING`, `VALID`, `DISQUALIFIED`
- `name` (CharField, max_length=50)

### Paso 4.10: Modelo `EventCompetitor`

Campos:
- `competitor` (FK → Competitor)
- `event` (FK → Event)
- `result` (CharField, max_length=50) — Almacenar como string (e.g., "04:36", "150", "1250")
- `event_rank` (PositiveIntegerField, null=True, blank=True) — Se calcula
- `score` (IntegerField, null=True, blank=True) — Se calcula
- `status` (FK → StatusEventCompetitor)

Restricción: `UNIQUE(competitor, event)`

### Paso 4.11: Admin de eventos

Registrar todos los modelos.

### Paso 4.12: Tests de categorías, fases y eventos

- Crear CompetitionCategory con min/max members.
- Habilitar categoría en edición.
- Crear CompetitionStage QUALIFIER y FINAL.
- Intentar crear dos QUALIFIER lanza error.
- Crear Event con resultado TIME y dirección ASC.
- Crear Event con resultado REPS y dirección DESC.
- Crear EventCompetitor con resultado.
- Duplicado (competitor + event) lanza error.

---

## Fase 5 — App `scoring` (Reglas de Puntuación)

### Paso 5.1: Crear la app

```bash
python manage.py startapp scoring apps/scoring
```

### Paso 5.2: Modelo `ScoringRule`

Campos:
- `competition_edition` (FK → CompetitionEdition)
- `position` (PositiveIntegerField)
- `points` (PositiveIntegerField)

Restricción: `UNIQUE(competition_edition, position)`

### Paso 5.3: Admin de scoring

Registrar ScoringRule.

### Paso 5.4: Tests de scoring

- Crear ScoringRule para una edición (1→100, 2→94, 3→88).
- Verificar que posición duplicada lanza error.
- Verificar que otra edición puede tener tabla diferente.

---

## Fase 6 — Servicios de Negocio

### Paso 6.1: Crear estructura de services

Cada app obtiene un directorio `services/`:

```
apps/events/services/__init__.py
apps/events/services/result_parser.py
apps/events/services/event_ranking_service.py

apps/scoring/services/__init__.py
apps/scoring/services/scoring_service.py

apps/rankings/services/__init__.py
apps/rankings/services/competition_ranking_service.py
apps/rankings/services/final_qualification_service.py
```

### Paso 6.2: `ResultParser`

Responsabilidad: Interpretar resultados crudos según el tipo.

- `TIME`: Convertir "HH:MM:SS" o "MM:SS" a segundos (int).
- `REPS`: Convertir a int.
- `WEIGHT`: Convertir a decimal.
- `DISTANCE`: Convertir a decimal (metros).
- `POINTS`: Convertir a int.

Método: `parse(result_string: str, result_type: str) -> float`

### Paso 6.3: `EventRankingService`

Responsabilidad: Calcular posiciones de un evento.

Método principal: `calculate_event_ranking(event: Event)`

Pasos:
1. Obtener todos los `EventCompetitor` del evento con status `VALID`.
2. Parsear resultados con `ResultParser`.
3. Ordenar según `rank_direction` (ASC = menor primero, DESC = mayor primero).
4. Resolver empates con ranking deportivo (dense ranking).
5. Asignar `event_rank`.
6. Buscar `ScoringRule` de la edición por posición.
7. Asignar `score` (puntos).
8. Guardar en base de datos.

### Paso 6.4: `ScoringService`

Responsabilidad: Convertir posición a puntos usando ScoringRule.

Método: `get_points(edition: CompetitionEdition, position: int) -> int`

- Buscar `ScoringRule` donde `competition_edition=edition` y `position=pos`.
- Si no existe, retornar 0.

### Paso 6.5: `CompetitionRankingService`

Responsabilidad: Calcular Score Final y ranking general.

Método principal: `calculate_competition_ranking(edition: CompetitionEdition, stage: CompetitionStage)`

Pasos:
1. Para cada categoría habilitada en la edición:
   a. Obtener todos los Competitor de esa categoría.
   b. Para cada Competitor, sumar scores de todos los EventCompetitor válidos del stage → Score Final.
   c. Ordenar por Score Final descendente.
   d. Aplicar desempates (ver reglas abajo).
   e. Asignar posición final.
2. Retornar ranking completo.

**Algoritmo de desempate:**
1. Mayor Score Final.
2. Contar 1eros lugares (más es mejor).
3. Contar 2do lugares.
4. Contar 3eros lugares.
5. Mejor resultado en el último evento común.
6. Mantener empate.

### Paso 6.6: `FinalQualificationService`

Responsabilidad: Determinar quiénes clasifican de Qualifier a Final.

Método: `get_qualifiers(edition: CompetitionEdition) -> list[Competitor]`

Pasos:
1. Obtener el stage QUALIFIER de la edición.
2. Calcular ranking del Qualifier con `CompetitionRankingService`.
3. Para cada categoría, tomar los top N según `qualification_count`.
4. Retornar lista de competidores clasificados.

### Paso 6.7: Tests de servicios

**ResultParser:**
- Parsear "04:36" → 276 segundos.
- Parsear "150" como REPS → 150.
- Parsear "125.5" como WEIGHT → 125.5.

**EventRankingService:**
- 4 competidores con tiempos diferentes → posiciones correctas.
- 2 competidores empatados → ambos con misma posición (1, 2, 2, 4).
- Score asignado correctamente según ScoringRule.

**ScoringService:**
- Posición 1 → 100 puntos.
- Posición 2 → 94 puntos.
- Posición sin regla → 0 puntos.

**CompetitionRankingService:**
- 5 eventos: 94+100+94+100+100 = 488 (Score Final).
- Ranking por categoría.
- Desempate correcto.

**FinalQualificationService:**
- qualification_count=5 → top 5 clasifican.
- Ranking independiente en Final.

---

## Fase 7 — App `rankings` (Leaderboard)

### Paso 7.1: Crear la app

```bash
python manage.py startapp rankings apps/rankings
```

### Paso 7.2: Endpoint de leaderboard

Esta app expone los endpoints de consulta de rankings. No tiene modelos propios — consume los servicios de `scoring` y `events`.

### Paso 7.3: Tests de rankings

- Consultar leaderboard de una edición.
- Leaderboard por categoría.
- Leaderboard de Qualifier.
- Leaderboard de Final (independiente).

---

## Fase 8 — API REST

### Paso 8.1: Serializers por app

**`apps/users/serializers.py`:**
- `UserSerializer` (list, create, update)
- `UserCreateSerializer` (con password write-only)
- `RoleSerializer`

**`apps/competitions/serializers.py`:**
- `CompetitionTypeSerializer`
- `AffiliationSerializer`
- `LocationSerializer`
- `CompetitionSerializer`
- `CompetitionEditionSerializer`
- `CompetitionEditionAdminSerializer`

**`apps/participants/serializers.py`:**
- `PersonSerializer`
- `TeamSerializer`
- `TeamMemberSerializer`
- `CompetitorSerializer`

**`apps/events/serializers.py`:**
- `CompetitionCategorySerializer`
- `CompetitionEnabledCategorySerializer`
- `CompetitionStageSerializer`
- `EventResultTypeSerializer`
- `RankDirectionSerializer`
- `EventSerializer`
- `StatusEventCompetitorSerializer`
- `EventCompetitorSerializer`

**`apps/scoring/serializers.py`:**
- `ScoringRuleSerializer`

**`apps/rankings/serializers.py`:**
- `LeaderboardEntrySerializer` (read-only)
- `LeaderboardSerializer` (agrupado por categoría)

### Paso 8.2: ViewSets por app

Cada app obtiene `views.py` con ViewSets:

- `UserViewSet` (ModelViewSet)
- `RoleViewSet` (ReadOnlyModelViewSet)
- `CompetitionViewSet` (ModelViewSet)
- `CompetitionEditionViewSet` (ModelViewSet)
- `PersonViewSet` (ModelViewSet)
- `TeamViewSet` (ModelViewSet)
- `CompetitorViewSet` (ModelViewSet)
- `EventViewSet` (ModelViewSet)
- `EventCompetitorViewSet` (ModelViewSet)
- `ScoringRuleViewSet` (ModelViewSet)
- `LeaderboardViewSet` (ReadOnlyModelViewSet, custom actions)

### Paso 8.3: Routers y URL configuration

**`apps/users/urls.py`:**
```python
router = DefaultRouter()
router.register('users', UserViewSet)
router.register('roles', RoleViewSet)
urlpatterns = router.urls
```

**`apps/competitions/urls.py`:**
```python
router = DefaultRouter()
router.register('competitions', CompetitionViewSet)
router.register('competition-editions', CompetitionEditionViewSet)
urlpatterns = router.urls
```

*(Similar para cada app)*

**`config/urls.py`:**
```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.users.urls')),
    path('api/v1/', include('apps.competitions.urls')),
    path('api/v1/', include('apps.participants.urls')),
    path('api/v1/', include('apps.events.urls')),
    path('api/v1/', include('apps.scoring.urls')),
    path('api/v1/', include('apps.rankings.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
```

### Paso 8.4: Configurar DRF y Spectacular

En `config/settings/base.py`:
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Scorely API',
    'DESCRIPTION': 'API for managing sports competition results',
    'VERSION': '1.0.0',
}
```

### Paso 8.5: Tests de API

Para cada endpoint principal:
- GET lista (requiere auth).
- POST crear (requiere auth + permiso).
- GET detalle.
- PUT/PATCH actualizar.
- DELETE eliminar.
- Verificar paginación.
- Verificar filtrado.
- Verificar búsqueda.

---

## Fase 9 — Seguridad

### Paso 9.1: Autenticación JWT

Configurar en `config/settings/base.py`:
```python
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

Endpoint de login:
- `POST /api/v1/auth/login/` → retorna access + refresh token.

Endpoint de refresh:
- `POST /api/v1/auth/refresh/` → retorna nuevo access token.

### Paso 9.2: Permisos por edición

Crear permiso custom: `apps/users/permissions.py`

```python
class IsEditionAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role and request.user.role.code == 'SUPERADMIN':
            return True
        return CompetitionEditionAdmin.objects.filter(
            user=request.user,
            competition_edition=obj.competition_edition
        ).exists()
```

### Paso 9.3: CORS

Configurar `django-cors-headers` en settings:
```python
CORS_ALLOWED_ORIGINS = env('CORS_ALLOWED_ORIGINS').split(',')
```

### Paso 9.4: Tests de seguridad

- Usuario no autenticado no accede a endpoints protegidos.
- ADMIN no accede a edición no asignada.
- SUPERADMIN accede a todo.
- JWT expira correctamente.

---

## Fase 10 — Django Admin

### Paso 10.1: Registrar todos los modelos

En cada `apps/*/admin.py`:

| App | Modelos |
|-----|---------|
| `users` | User, Role, CompetitionEditionAdmin |
| `competitions` | CompetitionType, Affiliation, Location, Competition, CompetitionEdition |
| `participants` | Person, Team, TeamMember, Competitor |
| `events` | CompetitionCategory, CompetitionEnabledCategory, CompetitionStage, Event, EventResultType, RankDirection, EventCompetitor, StatusEventCompetitor |
| `scoring` | ScoringRule |

### Paso 10.2: Configurar cada Admin

Para cada modelo:
- `list_display`: campos relevantes
- `list_filter`: filtros útiles
- `search_fields`: campos de búsqueda
- `ordering`: orden por defecto
- `autocomplete_fields`: FK con muchos registros

---

## Fase 11 — Seed Data

### Paso 11.1: Crear management command

Archivo: `apps/users/management/commands/seed_data.py` (o en una app central)

### Paso 11.2: Datos a crear

```python
# Roles
Role.objects.get_or_create(code='SUPERADMIN', name='Superadmin')
Role.objects.get_or_create(code='ADMIN', name='Admin')

# CompetitionTypes
CompetitionType.objects.get_or_create(code='CROSSFIT', name='CrossFit')
CompetitionType.objects.get_or_create(code='HYROX', name='HYROX')

# StatusEventCompetitor
StatusEventCompetitor.objects.get_or_create(code='PENDING', name='Pending')
StatusEventCompetitor.objects.get_or_create(code='VALID', name='Valid')
StatusEventCompetitor.objects.get_or_create(code='DISQUALIFIED', name='Disqualified')

# EventResultType
for code, name in [('TIME','Time'),('REPS','Reps'),('WEIGHT','Weight'),('DISTANCE','Distance'),('POINTS','Points')]:
    EventResultType.objects.get_or_create(code=code, name=name)

# RankDirection
RankDirection.objects.get_or_create(code='ASC', name='Ascending')
RankDirection.objects.get_or_create(code='DESC', name='Descending')

# Categories
categories = [
    ('Individual Male', 1, 1),
    ('Individual Female', 1, 1),
    ('Team Male', 2, 2),
    ('Team Female', 2, 2),
    ('Team Mixed', 2, 2),
    ('Master Male', 1, 1),
    ('Master Female', 1, 1),
]
for name, min_m, max_m in categories:
    CompetitionCategory.objects.get_or_create(name=name, defaults={'min_members': min_m, 'max_members': max_m})

# Example ScoringRule (if an edition exists)
# ...
```

### Paso 11.3: Test del seed

- Ejecutar `seed_data`.
- Verificar que los datos existen.
- Ejecutar dos veces sin errores (idempotente).

---

## Fase 12 — Documentación API

### Paso 12.1: Configurar drf-spectacular

Ya configurado en Fase 8.

### Paso 12.2: Decoradores y schemas

Agregar `@extend_schema` a ViewSets para describir operaciones.

### Paso 12.3: Verificar endpoints de documentación

- `/api/schema/` →返回 OpenAPI JSON.
- `/api/docs/` → Swagger UI funcional.
- `/api/redoc/` → ReDoc funcional.

---

## Fase 13 — Testing Completo

### Paso 13.1: Estructura de tests

```
tests/
├── __init__.py
├── conftest.py          # Fixtures compartidos
├── test_users.py
├── test_competitions.py
├── test_participants.py
├── test_events.py
├── test_scoring.py
├── test_rankings.py
├── test_api.py
└── test_security.py
```

### Paso 13.2: Fixtures (conftest.py)

Crear fixtures:
- `user` → Usuario estándar
- `superadmin` → Usuario SUPERADMIN
- `admin_user` → Usuario ADMIN
- `competition_type` → CROSSFIT
- `affiliation` → Affiliation de prueba
- `location` → Location de prueba
- `competition` → Competition de prueba
- `edition` → CompetitionEdition PUBLISHED
- `category` → CompetitionCategory
- `enabled_category` → CompetitionEnabledCategory
- `stage_qualifier` → CompetitionStage QUALIFIER
- `stage_final` → CompetitionStage FINAL
- `event` → Event de prueba
- `scoring_rules` → ScoringRule (1→100, 2→94, 3→88)
- `person` → Person de prueba
- `competitor` → Competitor INDIVIDUAL
- `team` → Team de prueba
- `team_competitor` → Competitor TEAM

### Paso 13.3: Tests por área

**Usuarios (test_users.py):**
- Crear usuario con email + password.
- Login con credenciales correctas.
- Login con credenciales incorrectas → error.
- Email duplicado → error.
- Asignar rol SUPERADMIN.
- Asignar rol ADMIN.

**Competencias (test_competitions.py):**
- Crear Competition con todos los FK.
- Crear CompetitionEdition.
- Año duplicado → error.
- Transiciones de estado (DRAFT → PUBLISHED → FINISHED).

**Participantes (test_participants.py):**
- Crear Person.
- Crear Team.
- Agregar TeamMember.
- Duplicado TeamMember → error.
- Crear Competitor INDIVIDUAL.
- Crear Competitor TEAM.
- Competitor con ambos → error.
- Competitor sin ninguno → error.

**Categorías (test_events.py):**
- Crear CompetitionCategory.
- Habilitar en edición.
- Duplicado → error.
- Crear CompetitionStage QUALIFIER.
- Segundo QUALIFIER → error.
- Crear Event con TIME/ASC.
- Crear Event con REPS/DESC.

**Scoring (test_scoring.py):**
- Crear ScoringRule (1→100, 2→94, 3→88).
- Posición duplicada → error.
- Otra edición con tabla diferente.

**Rankings (test_rankings.py):**
- EventRankingService con 4 competidores.
- Empate en posición 2 → (1, 2, 2, 4).
- Score correcto según tabla.
- Score Final = 94+100+94+100+100 = 488.
- Qualifier → top 5 clasifican.
- Final tiene ranking independiente.

**API (test_api.py):**
- GET /api/v1/users/ sin auth → 401.
- GET /api/v1/users/ con auth → 200.
- POST /api/v1/competitions/ → 201.
- GET /api/v1/rankings/ → leaderboard.

**Seguridad (test_security.py):**
- JWT expirado → 401.
- ADMIN sin permiso → 403.
- SUPERADMIN → 200.

---

## Fase 14 — Verificación Final

### Paso 14.1: Docker build

```bash
docker compose up --build
```

Verificar que el contenedor levanta sin errores.

### Paso 14.2: Migraciones

```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

Verificar que todas las apps generan migraciones correctamente.

### Paso 14.3: Seed data

```bash
docker compose exec web python manage.py seed_data
```

### Paso 14.4: Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

### Paso 14.5: Tests

```bash
docker compose exec web pytest
```

Todos los tests deben pasar.

### Paso 14.6: Documentación

Verificar que `/api/docs/` carga correctamente.

### Paso 14.7: Revisión de código

- Verificar que no hay lógica de negocio en views.
- Verificar que no hay credenciales hardcodeadas.
- Verificar que la cadena Result→Position→Points→Score→Leaderboard está respetada.
- Verificar que los empates usan ranking deportivo.
- Verificar que Qualifier y Final son independientes.

---

## Resumen de Archivos a Crear

| # | Archivo | Fase |
|---|---------|------|
| 1 | `.env.example` | 0 |
| 2 | `.gitignore` | 0 |
| 3 | `requirements.txt` | 0 |
| 4 | `Dockerfile` | 0 |
| 5 | `docker-compose.yml` | 0 |
| 6 | `manage.py` | 0 |
| 7 | `pytest.ini` | 0 |
| 8 | `config/__init__.py` | 0 |
| 9 | `config/settings/__init__.py` | 0 |
| 10 | `config/settings/base.py` | 0 |
| 11 | `config/settings/development.py` | 0 |
| 12 | `config/settings/production.py` | 0 |
| 13 | `config/urls.py` | 0 |
| 14 | `config/asgi.py` | 0 |
| 15 | `config/wsgi.py` | 0 |
| 16 | `apps/__init__.py` | 0 |
| 17 | `apps/users/__init__.py` | 1 |
| 18 | `apps/users/models.py` | 1 |
| 19 | `apps/users/admin.py` | 1 |
| 20 | `apps/users/serializers.py` | 8 |
| 21 | `apps/users/views.py` | 8 |
| 22 | `apps/users/urls.py` | 8 |
| 23 | `apps/users/permissions.py` | 9 |
| 24 | `apps/users/services/__init__.py` | 6 |
| 25 | `apps/competitions/__init__.py` | 2 |
| 26 | `apps/competitions/models.py` | 2 |
| 27 | `apps/competitions/admin.py` | 2 |
| 28 | `apps/competitions/serializers.py` | 8 |
| 29 | `apps/competitions/views.py` | 8 |
| 30 | `apps/competitions/urls.py` | 8 |
| 31 | `apps/participants/__init__.py` | 3 |
| 32 | `apps/participants/models.py` | 3 |
| 33 | `apps/participants/admin.py` | 3 |
| 34 | `apps/participants/serializers.py` | 8 |
| 35 | `apps/participants/views.py` | 8 |
| 36 | `apps/participants/urls.py` | 8 |
| 37 | `apps/events/__init__.py` | 4 |
| 38 | `apps/events/models.py` | 4 |
| 39 | `apps/events/admin.py` | 4 |
| 40 | `apps/events/serializers.py` | 8 |
| 41 | `apps/events/views.py` | 8 |
| 42 | `apps/events/urls.py` | 8 |
| 43 | `apps/events/services/__init__.py` | 6 |
| 44 | `apps/events/services/result_parser.py` | 6 |
| 45 | `apps/events/services/event_ranking_service.py` | 6 |
| 46 | `apps/scoring/__init__.py` | 5 |
| 47 | `apps/scoring/models.py` | 5 |
| 48 | `apps/scoring/admin.py` | 5 |
| 49 | `apps/scoring/serializers.py` | 8 |
| 50 | `apps/scoring/views.py` | 8 |
| 51 | `apps/scoring/urls.py` | 8 |
| 52 | `apps/scoring/services/__init__.py` | 6 |
| 53 | `apps/scoring/services/scoring_service.py` | 6 |
| 54 | `apps/rankings/__init__.py` | 7 |
| 55 | `apps/rankings/serializers.py` | 8 |
| 56 | `apps/rankings/views.py` | 8 |
| 57 | `apps/rankings/urls.py` | 8 |
| 58 | `apps/rankings/services/__init__.py` | 6 |
| 59 | `apps/rankings/services/competition_ranking_service.py` | 6 |
| 60 | `apps/rankings/services/final_qualification_service.py` | 6 |
| 61 | `apps/users/management/commands/seed_data.py` | 11 |
| 62 | `tests/__init__.py` | 0 |
| 63 | `tests/conftest.py` | 13 |
| 64 | `tests/test_users.py` | 13 |
| 65 | `tests/test_competitions.py` | 13 |
| 66 | `tests/test_participants.py` | 13 |
| 67 | `tests/test_events.py` | 13 |
| 68 | `tests/test_scoring.py` | 13 |
| 69 | `tests/test_rankings.py` | 13 |
| 70 | `tests/test_api.py` | 13 |
| 71 | `tests/test_security.py` | 13 |

---

## Orden de Ejecución Recomendado

```
Fase 0 (Andamiaje)
  ↓
Fase 1 (Users) + Fase 2 (Competitions)  ← en paralelo, sin dependencias cruzadas aún
  ↓
Fase 3 (Participants) ← depende de Fase 2 (CompetitionEdition)
  ↓
Fase 4 (Events) ← depende de Fase 2 y 3
  ↓
Fase 5 (Scoring) ← depende de Fase 2
  ↓
Fase 6 (Services) ← depende de Fase 4 y 5
  ↓
Fase 7 (Rankings) ← depende de Fase 6
  ↓
Fase 8 (API) ← depende de Fase 1-5 (models + serializers)
  ↓
Fase 9 (Security) ← depende de Fase 8
  ↓
Fase 10 (Admin) ← puede hacerse en paralelo con Fase 8-9
  ↓
Fase 11 (Seed Data) ← después de todos los models
  ↓
Fase 12 (Docs) ← después de Fase 8
  ↓
Fase 13 (Tests) ← después de todo funcione
  ↓
Fase 14 (Verificación Final)
```

**Total estimado: ~71 archivos, 14 fases.**
