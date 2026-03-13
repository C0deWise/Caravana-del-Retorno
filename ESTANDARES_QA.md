**1. INTRODUCCIÓN**

Este documento define las directrices técnicas y de calidad obligatorias para el proyecto "Caravana del Retorno". El cumplimiento de estos estándares es requisito para la aprobación de Pull Requests (PR) y el despliegue en los entornos de Staging y Producción.

##### **2. ESTÁNDARES DE NOMENCLATURA Y CODIFICACIÓN**

###### 2.1 Backend (FastAPI / Python)

* **Estilo:** Cumplimiento estricto de **PEP 8**.
* **Variables y Funciones:** `snake_case` (ej. `obtener_usuario_por_id`).
* **Clases (Modelos, Esquemas, Servicios):** `PascalCase` (ej. `UsuarioRegistro`).
* **Estructura Modular:** Se debe respetar la jerarquía por módulos para asegurar la escalabilidad y el orden del monolito.
* **Organización por Módulo:** Cada funcionalidad dentro de `app/` (ej. `app/usuarios/`, `app/colonias/`) debe ser autónoma y contener sus propias capas:
    * `api/`: Endpoints específicos del módulo.
    * `models/`: Modelos de base de datos del módulo (SQLAlchemy/Tortoise).
    * `schemas/`: Esquemas de Pydantic para validación de datos.
    * `repositories/`: Lógica de acceso a datos y consultas (Queries).
    * `services/`: Lógica de negocio y reglas de validación complejas.
* **Core:** La carpeta `app/core/` se reserva exclusivamente para configuraciones globales del sistema (conexión a DB, seguridad JWT, constantes globales).

###### **2.2 Frontend (Next.js / TypeScript)**

- Componentes: PascalCase con extensión .tsx (ej. RegisterForm.tsx).

- Hooks y Variables: camelCase (ej. useAuth, isSubmitting).

- Estilos: Implementación de diseño Mobile-First según requerimientos no funcionales.

###### **2.3 Idioma y Diccionario**

- **Backend:** Código fuente, variables, base de datos y comentarios deben escribirse en **Español**.

- **Frontend:** Se usa **Inglés** para la nomenclatura de componentes, hooks y lógica, dada la naturaleza del framework (Next.js).

- Documentación de Negocio: Historias de Usuario, criterios de aceptación y manuales de usuario se mantendrán en Español.

##### **3. ESTRATEGIA DE PRUEBAS** 

###### **3.1 Pruebas Unitarias (Responsabilidad: Desarrollo)**

- No se aceptará ningún PR que reduzca el porcentaje de cobertura o no incluya sus respectivos tests.

Cobertura Mínima: Se exige un 70% de cobertura de código (code coverage). Tecnologías: pytest (Backend) y Jest + React Testing Library (Frontend).

- Validaciones Obligatorias en código:

- Documento: Numérico, > 0.

- Celular: Numérico, exacto 10 dígitos, > 0.

- Edad: Cálculo basado en fecha de nacimiento, debe ser >= 18 años.

- Personas a cargo: Numérico, >= 0 y < 10.

- Fechas de Retorno: fecha\_fin nunca debe ser inferior a fecha\_inicio.

###### **3.2 Pruebas de API e Integración (Responsabilidad: QA)**

- Toda funcionalidad expuesta debe estar documentada automáticamente en Swagger/OpenAPI.

- Herramienta: Postman / Newman para automatización en CI/CD.

- Estándar de Mensajes de Error (JSON):

Para mantener la consistencia en el consumo desde el Frontend, todo error de API debe seguir esta estructura:

JSON

{

  "status": "error",

  "code": "ERROR\_CODE\_NAME",

  "message": "Descripción clara en español para el usuario final",

  "details": { "field": "Nombre del campo afectado si aplica" }

}

##### **4. GESTIÓN DE CONFIGURACIÓN Y GIT WORKFLOW**

###### **4.1 Convención de Commits y Pull Requests**

- Se adopta el estándar de Conventional Commits. El formato de los mensajes debe ser:

\<tipo>(\<ID-HU>): \<descripción en español>

- Tipos permitidos: feat, fix, docs, style, refactor, test, chore.

Ejemplo: feat(1GU-1): implementación de la lógica de validación de edad

- Descripción obligatoria del PR: Todo Pull Request debe incluir una descripción con la siguiente estructura:

  - ¿Qué hace este PR?: Resumen funcional de la tarea.

  - Cambios realizados: Lista técnica de archivos o módulos modificados.

  - Cómo probar: Instrucciones paso a paso para que el QA verifique la funcionalidad (comandos de Docker, endpoints de Swagger, etc.).

Ejemplo:

¿Qué hace este PR? Permite crear una colonia con país, departamento, ciudad y líder\_id. Para colonias colombianas, departamento y ciudad son obligatorios. Para colonias extranjeras, solo se requiere el país. Cambios realizados colonia\_model.py: campos departamento, ciudad y lider\_id opcionales colonia\_schemas.py: validaciones de ubicación y normalización de texto tests/colonias/test\_colonia\_schemas.py: pruebas unitarias del schema Cómo probar Levantar: docker compose up --build Pruebas unitarias: docker compose exec api pytest tests/ -v Pruebas manuales en: http\://localhost:8000/docs

###### **4.2 Gestión de Secretos (Seguridad)**

- Prohibición: Queda prohibido el versionamiento de archivos .env o cualquier secreto en texto plano.

- Herramientas: Uso obligatorio de age y sops para el cifrado de archivos de configuración. El archivo env.encrypted es el único que debe subir al repositorio.

##### **5. CRITERIOS DE ACEPTACIÓN PARA PULL REQUESTS (QA GATE)**

Como responsable de la aprobación de cambios, se verificará:

- Integridad Funcional: La HU cumple con los pasos descritos en el Checklist de QA.

- Validación de Esquemas: Los campos cumplen con las restricciones de tipo y rango (ej. parentesco bilateral).

- Análisis Estático: El código no presenta errores de linting.

- Consistencia de Datos: El modelo relacional (Figura 4 de Especificaciones) se mantiene íntegro.

- Documentación Técnica: Se verificará que:

Todo archivo nuevo incluye un párrafo inicial (máx. 50 palabras) explicando su propósito.

Los métodos complejos tienen comentarios detallando parámetros, retornos y excepciones.

Los endpoints en Swagger tienen resumen, descripción, tipos de parámetros (obligatorios/opcionales) y códigos de respuesta HTTP.

- Consistencia de Datos: IDs autoincrementales y respeto al modelo relacional.