# Polybilling — Facturación políglota con arquitectura hexagonal

> Taller corte 3 · Programación Avanzada · Python 3.12 + Flask
> Cuatro motores de persistencia, un solo dominio limpio.

---

## 🚀 GUÍA DE EJECUCIÓN PARA EL DOCENTE

> ⚠️ **LEE PRIMERO** el archivo [`LEEME_PRIMERO.txt`](LEEME_PRIMERO.txt) en la
> raíz del proyecto. Contiene el resumen rápido.

### ❶ Requisitos previos — instalar UNA sola vez

| # | Instalar | Link | Importante |
|---|----------|------|------------|
| 1 | **Python 3.12** | <https://www.python.org/downloads/release/python-3120/> | ✔ Marcar **"Add Python to PATH"** durante la instalación |
| 2 | **Docker Desktop** | <https://www.docker.com/products/docker-desktop/> | Reiniciar al terminar la instalación |
| 3 | **MySQL local** (uno de los tres) | • [Laragon](https://laragon.org/download/) (**recomendado** en Windows)<br/>• [MySQL Server 8](https://dev.mysql.com/downloads/installer/)<br/>• [XAMPP](https://www.apachefriends.org/) | Usuario `root`, password `root` (si el tuyo es otro, edita `MYSQL_PASSWORD=` en `.env`) |

### ❷ ANTES DE EJECUTAR LOS `.BAT` (**cada vez**)

> 🟥 **MUY IMPORTANTE:** los `.bat` SOLO funcionan si tienes esto corriendo:

1. 🐳 **Abrir Docker Desktop** y esperar a que la ballena del icono esté **fija**
   y la app muestre *"Engine running"* abajo a la izquierda
   *(toma unos 10-20 segundos al iniciar Windows)*.
2. 🗄️ **Abrir tu MySQL local** (si es Laragon, clic en **"Start All"**).

Si te saltas estos dos pasos, los `.bat` te lo dirán con un error claro.

### ❸ Ejecución

| Paso | Cuándo | Acción |
|------|--------|--------|
| 1️⃣ | **Solo la primera vez** *(~3 min)* | Doble clic en `setup.bat` |
| 2️⃣ | **Cada vez** que quieras usar la app | Doble clic en `run.bat` |
| 3️⃣ | Cuando arranque | Abrir <http://localhost:8000> en el navegador |
| 4️⃣ | Al terminar | Doble clic en `stop.bat` *(opcional: apaga contenedores)* |

### ❹ ¿Qué hace cada `.bat`?

- **`setup.bat`** → verifica Python/Docker/MySQL, crea `venv`, instala
  dependencias, levanta Cassandra/MongoDB/Neo4j en Docker y carga los datos
  semilla en los 4 motores.
- **`run.bat`** → asegura que los contenedores estén arriba y arranca Flask.
- **`stop.bat`** → detiene los contenedores Docker (NO toca tu MySQL local).

---

Aplicación web de facturación construida sobre **arquitectura hexagonal**
(puertos y adaptadores), que demuestra cómo coexisten cuatro sistemas
de almacenamiento, cada uno aplicado donde mejor encaja:

| Motor       | Tipo            | Responsabilidad                           |
|-------------|-----------------|-------------------------------------------|
| Cassandra   | SGBD NR columnar| Personas (clientes y empleados)           |
| MongoDB     | SGBD NR documento| Catálogo de productos                     |
| MySQL       | SGBD relacional | `factura` y `detalle_factura` (ACID)      |
| Neo4j       | SGBD NR grafo   | Motor de recomendaciones contextuales     |

---

## Arquitectura

```
app/
├── domain/                # núcleo: entidades + puertos (interfaces)
│   ├── entities/          # Person, Product, Invoice, InvoiceDetail
│   └── ports/             # interfaces de repositorio
├── application/           # casos de uso: orquestación
│   └── services/
├── infrastructure/        # adaptadores concretos
│   ├── config/            # settings via dotenv
│   └── adapters/
│       ├── cassandra/     # CassandraPersonRepository
│       ├── mongo/         # MongoProductRepository
│       ├── mysql/         # MySQLInvoiceRepository
│       └── neo4j/         # Neo4jRecommendationRepository
└── interfaces/web/        # Flask: blueprints, container DI, templates
```

El **dominio** desconoce por completo a Cassandra, Mongo, MySQL y Neo4j: solo
habla con sus puertos. Los **adaptadores** son los únicos que importan los
drivers reales. El **container** (`app/interfaces/web/container.py`)
cablea los puertos con los adaptadores y los inyecta en los servicios.

---

## Requisitos

- Python **3.12**
- Cassandra 4.x (puerto 9042)
- MongoDB 6.x+ (puerto 27017)
- MySQL 8.x (puerto 3306)
- Neo4j 5.x (puerto 7687)

> Cualquiera de los 4 motores puede levantarse con Docker. Ejemplo rápido:
>
> ```bash
> docker run -d --name cassandra -p 9042:9042 cassandra:5
> docker run -d --name mongo     -p 27017:27017 mongo:7
> docker run -d --name mysql     -p 3306:3306 \
>     -e MYSQL_ROOT_PASSWORD=root -e MYSQL_DATABASE=billing mysql:8
> docker run -d --name neo4j     -p 7687:7687 -p 7474:7474 \
>     -e NEO4J_AUTH=neo4j/neo4j12345 neo4j:5
> ```

---

## Instalación

```bash
# 1) Clonar / descomprimir
cd "taller corte 3 python"

# 2) Entorno virtual aislado
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

# 3) Dependencias
pip install -r requirements.txt

# 4) Variables de entorno
cp .env.example .env       # o copy .env.example .env  en Windows
# editar .env con las credenciales reales
```

### Para añadir/actualizar dependencias

```bash
pip install <paquete>
pip freeze > requirements.txt    # reescribir
# o
pip freeze >> requirements.txt   # agregar sin perder orden
```

---

## Diligenciar las bases de datos

Toda la carpeta `dbs/` trae datos semilla para no arrancar en cero.

### Opción A — automática (recomendada)

```bash
python dbs/seed_all.py
```

Ejecuta los 4 scripts en orden contra los motores configurados en `.env`.

### Opción B — manualmente, motor por motor

```bash
# Cassandra
cqlsh -f dbs/01_cassandra.cql

# MongoDB
mongosh < dbs/02_mongo.js

# MySQL
mysql -u root -p < dbs/03_mysql.sql

# Neo4j
cypher-shell -u neo4j -p neo4j12345 -f dbs/04_neo4j.cypher
```

---

## Arrancar la aplicación

```bash
python run.py
```

Disponible en <http://localhost:8000>.

Navegación:

- `/persons` — CRUD de personas (Cassandra)
- `/products` — CRUD de productos (MongoDB)
- `/invoices` — listar, ver y crear facturas (MySQL)
- `/recommendations` — recomendaciones por cliente (Neo4j)

---

## Motor de recomendaciones (Neo4j)

El servicio combina **tres señales** ponderadas:

1. **Filtrado colaborativo geográfico**: lo que compraron clientes que
   viven en el mismo barrio y comparten género y estrato.
2. **Similitud por contenido**: productos que comparten categoría o tags
   con compras previas del cliente.
3. **Popularidad barrial**: top de productos vendidos en el barrio.

Cada recomendación viene con un `score` agregado y la razón principal
("clientes similares en tu barrio", "similar a productos que ya compraste",
"popular en tu barrio").

---

## Estructura del proyecto

```
.
├── app/                      # código (arquitectura hexagonal)
├── dbs/                      # scripts de semilla por motor + seed_all.py
├── docs/
│   └── prompts.docx          # prompts y tecnologías utilizadas
├── tests/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

---

## Nota sobre Python 3.12 y cassandra-driver

`cassandra-driver 3.29` aún intenta importar `asyncore` (removido en Python 3.12)
al cargar `cassandra.cluster`. El proyecto resuelve esto registrando un stub
mínimo y forzando `AsyncioConnection` como reactor. Si migras a un driver
oficial con soporte nativo para 3.12, puedes eliminar el bloque del stub
en `app/infrastructure/adapters/cassandra/cassandra_connection.py`.

---

## Buenas prácticas aplicadas

- Arquitectura hexagonal (puertos + adaptadores).
- Inyección de dependencias vía contenedor.
- Validaciones de invariantes en el dominio (`__post_init__`).
- Transacciones explícitas en MySQL (commit/rollback).
- Índices propios en cada motor (clave en Cassandra, único en Mongo, FK en MySQL).
- `.env` fuera del repositorio (`.gitignore`).
- Entorno virtual aislado (`venv`).
- Templates Jinja2 con Bootstrap 5 y mensajes flash.

---

## Autor

Juan Carlos Pastuzán Quintero · ITP · 2026
