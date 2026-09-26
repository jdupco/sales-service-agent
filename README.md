# Documento Tencico y Arquitectura del Proyecto: Agente Inteligente de Ventas y Servicio al Cliente

## 1. Visión General del Proyecto

El objetivo es construir un **Agente de Inteligencia Artificial para Ventas y Servicio al Cliente** omnicanal (ej. WhatsApp/Web). El agente debe responder dudas comerciales con base en documentos (PDFs de planes y productos) y ejecutar acciones transaccionales (consultar estados de cuenta, datos de CRM y contratos), gestionando el escalamiento a asesores humanos de forma transparente.

### Requisitos Operativos

* **Escala:** ~9,000–10,000 consultas mensuales (cientos al día).
* **Costos:** Infraestructura en la nube con un consumo cercano a **$0 USD/mes** aprovechando capas gratuitas (Render y Supabase).
* **Simplicidad:** Arquitectura asíncrona ligera sin intermediarios pesados (sin Redis, Celery ni Kafka).

---

## 2. Stack Tecnológico Seleccionado

| Componente | Tecnología | Razón de Elección |
| --- | --- | --- |
| **Lenguaje & Tooling** | **Python 3.12+ / `uv` / `ruff` / `ty**` | `uv` gestiona entorno y dependencias a máxima velocidad; `ruff` hace linting y formateo instantáneo. |
| **Backend API** | **FastAPI** | Framework asíncrono ultrarrápido para procesar webhooks. |
| **Servidor / Hosting** | **Render** | Despliegue en la nube con uso eficiente de recursos. |
| **Base de Datos & Vectorstore** | **Supabase (PostgreSQL + `pgvector`)** | Almacena datos relacionales, historial de chats, estados de sesión y embeddings vectoriales. |
| **Almacenamiento de Archivos** | **Supabase Storage** | Buckets para guardar PDFs de ventas sin saturar el disco o RAM de Render. |
| **Orquestación de Agente** | **LangGraph** | Controla la máquina de estados, decisiones del agente y pausas para asesores humanos (*Human-in-the-Loop*). |
| **RAG / Ingesta Documental** | **LlamaIndex** | Procesa PDFs de ventas/productos, realiza *chunking* y gestiona búsquedas semánticas. |
| **Adaptador de LLMs** | **LiteLLM** | Gateway unificado con soporte de *fallbacks* (OpenAI, Anthropic, Gemini, Groq). |

---

## 3. Decisiones Arquitectónicas y Justificación

### A. Sin Redis ni Celery (Uso de `asyncio` y `BackgroundTasks`)

* **Alternativa Evaluada:** Usar colas de mensajes (Redis/Celery) para procesar webhooks de mensajería.
* **Decisión:** Se descartó Redis. FastAPI responde `HTTP 200 OK` en menos de 50 ms mediante `BackgroundTasks`, ejecutando la lógica del agente en segundo plano. Esto reduce costos y evita complejidad operativa.

### B. Esquema de Datos Flexible con `JSONB`

* **Incertidumbre Actual:** No se conocen los campos exactos que vendrán de futuros CRMs o bases de clientes.
* **Decisión:** La tabla `users` usará una columna `metadata` de tipo `JSONB` en PostgreSQL. Esto permite guardar cualquier atributo dinámico que entregue el CRM más adelante sin migrar la base de datos.

### C. Estrategia de Separación de Datos (Estático vs. Dinámico)

* **Información Estática (PDFs de ventas, precios, planes):** Se procesa una sola vez con **LlamaIndex** y se guarda en la extensión **`pgvector`** de Supabase para consultas por búsqueda semántica (RAG).
* **Información Dinámica (Estado de cuenta, contratos, CRM):** No usa embeddings. Se consulta en tiempo real mediante **Herramientas / Function Calling** ejecutadas por el agente.

### D. Control de Interferencia: Agente vs. Asesor Humano

La tabla de sesiones maneja una columna `status`:

* **`BOT`:** El agente procesa y responde mensajes automáticamente.
* **`WAITING_HUMAN`:** El agente pausa su ejecución y notifica al equipo de soporte.
* **`HUMAN`:** El agente ignora las entradas entrantes para dar control exclusivo al asesor humano.

---

## 4. Estructura del Proyecto (Monorepo Modular)

```text
sales-service-agent/
│
├── .venv/                              # Entorno virtual creado por uv (NO se commitea)
├── .gitignore
├── README.md
├── pyproject.toml                      # Configuración del proyecto, uv, Ruff y ty
├── uv.lock                             # Lockfile exacto de dependencias
│
├── scripts/
│   └── ingesta_pdfs.py                 # CLI: procesa PDFs desde Supabase Storage
│
├── src/
│   └── sales_service_agent/
│       ├── __init__.py
│       ├── config.py                   # Configuración global / variables de entorno
│       │
│       ├── core/
│       │   ├── __init__.py
│       │   ├── supabase_client.py      # Conexión a BD y Supabase Storage
│       │   └── litellm_client.py       # Gateway hacia modelos de IA
│       │
│       ├── rag/
│       │   ├── __init__.py
│       │   ├── ingester.py             # Extracción, parsing y chunking con LlamaIndex
│       │   └── retriever.py            # Motor de búsqueda vectorial
│       │
│       ├── agent/
│       │   ├── __init__.py
│       │   ├── state.py                # Estado del agente para LangGraph
│       │   ├── nodes.py                # Nodos: RAG, Tools, Human Handover
│       │   └── graph.py                # Grafo de decisión del agente
│       │
│       └── api/
│           ├── __init__.py
│           ├── main.py                 # Instancia principal de FastAPI
│           └── routes/
│               ├── __init__.py
│               └── webhooks.py         # Endpoints / entrada de webhooks
│
└── tests/
    ├── test_agent.py                   # Tests del agente / LangGraph
    ├── test_rag.py                     # Tests del pipeline RAG
    └── test_api.py                     # Tests de FastAPI
```
---

## 5. Roadmap de Construcción Progresiva

```text
[ Paso 1: Ingesta RAG ] ──► [ Paso 2: Base de Datos ] ──► [ Paso 3: Grafo LangGraph ] ──► [ Paso 4: FastAPI & Webhook ]
(PDFs + LlamaIndex)         (Tablas SQL en Supabase)      (Nodos + LiteLLM)             (Render + WhatsApp)

```

1. **Paso 1: Pipeline de Ingesta RAG (Punto de inicio actual)**
* Subir PDFs de productos/ventas a un Bucket en Supabase Storage.
* Escribir `scripts/ingesta_pdfs.py` para procesar documentos con LlamaIndex y guardarlos en `pgvector`.


2. **Paso 2: Esquema SQL en Supabase**
* Crear las tablas `users` (con `JSONB`), `conversations` (con campo `status`), `messages` y habilitar `pgvector`.


3. **Paso 3: Grafo del Agente con LangGraph + LiteLLM**
* Definir el grafo conversacional en Python con nodos para consultar el RAG, invocar funciones simuladas (*mock*) de CRM y ejecutar el cambio de estado a humano.


4. **Paso 4: API FastAPI y Despliegue**
* Unir el flujo al servidor FastAPI, configurar `BackgroundTasks` y desplegar en Render.

---

## 6. Puntos Postergados Intencionalmente

* **Proveedor definitivo de WhatsApp:** Se probará localmente por API antes de integrar Twilio o Meta Cloud API.
* **Integración real de CRM:** Se usarán funciones *mock* en Python para simular saldos y datos de cliente.
* **Contenedores (Docker):** Se desarrollará inicialmente con `uv run` en local; el `Dockerfile` se creará al preparar el despliegue final en Render.