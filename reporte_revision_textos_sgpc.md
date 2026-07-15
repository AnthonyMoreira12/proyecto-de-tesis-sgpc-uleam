# Reporte de revisi?n de textos y etiquetas SGPC ULEAM

Fecha de generaci?n: 08/07/2026 09:57:35

Proyecto analizado: `C:\Users\TONYMOR\Desktop\SOFTWARE DE GESTIÓN DE PRODUCCIÓN CIENTÍFICA PARA LA FACULTAD DE CIENCIAS DE LA VIDA Y TECNOLOGÍAS`

Total de hallazgos: **34**

## docker-compose.yml

- L?nea **10** | **Referencia antigua a FCVT**
  - Texto encontrado: `POSTGRES_DB: ${DB_NAME:-SGPC_FCVT_2}`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **30** | **Referencia antigua a FCVT**
  - Texto encontrado: `context: ./BACKEND_SGPC_FCVT`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **36** | **Referencia antigua a FCVT**
  - Texto encontrado: `- DB_NAME=${DB_NAME:-SGPC_FCVT_2}`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **53** | **Referencia antigua a FCVT**
  - Texto encontrado: `context: ./FRONTEND_SGPC_FCVT`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## .github\workflows\ci-cd.yml

- L?nea **25** | **Referencia antigua a FCVT**
  - Texto encontrado: `pip install -r BACKEND_SGPC_FCVT/requirements.txt`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **29** | **Referencia antigua a FCVT**
  - Texto encontrado: `DJANGO_SETTINGS_MODULE: BACKEND_SGPC_FCVT.settings`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **31** | **Referencia antigua a FCVT**
  - Texto encontrado: `cd BACKEND_SGPC_FCVT`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **45** | **Referencia antigua a FCVT**
  - Texto encontrado: `cd BACKEND_SGPC_FCVT`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## BACKEND_SGPC_FCVT\manage.py

- L?nea **9** | **Referencia antigua a FCVT**
  - Texto encontrado: `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BACKEND_SGPC_FCVT.settings')`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## BACKEND_SGPC_FCVT\BACKEND_SGPC_FCVT\asgi.py

- L?nea **2** | **Referencia antigua a FCVT**
  - Texto encontrado: `ASGI config for BACKEND_SGPC_FCVT project.`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **14** | **Referencia antigua a FCVT**
  - Texto encontrado: `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BACKEND_SGPC_FCVT.settings')`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## BACKEND_SGPC_FCVT\BACKEND_SGPC_FCVT\settings.py

- L?nea **1** | **Referencia antigua a FCVT**
  - Texto encontrado: `# Archivo de configuración principal de Django para SGPC-FCVT:`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **86** | **Referencia antigua a FCVT**
  - Texto encontrado: `ROOT_URLCONF = "BACKEND_SGPC_FCVT.urls"`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **109** | **Referencia antigua a FCVT**
  - Texto encontrado: `WSGI_APPLICATION = "BACKEND_SGPC_FCVT.wsgi.application"`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **118** | **Referencia antigua a FCVT**
  - Texto encontrado: `"NAME": os.getenv("DB_NAME", "SGPC_FCVT_2").strip(),`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## BACKEND_SGPC_FCVT\BACKEND_SGPC_FCVT\wsgi.py

- L?nea **4** | **Referencia antigua a FCVT**
  - Texto encontrado: `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'BACKEND_SGPC_FCVT.settings')`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## BACKEND_SGPC_FCVT\core\admin\serializers\admin_publicaciones_serializers.py

- L?nea **3** | **Uso de Registrador en t?tulos**
  - Texto encontrado: `# usuario creador, administrador registrador, adjuntos, disponibilidad de PDF y autor principal.`
  - Sugerencia: Revisar si debe decir Registrar. Ejemplo: Registrar Ponencia, Registrar Libro.

## BACKEND_SGPC_FCVT\core\auth\views\auth_password_reset_views.py

- L?nea **97** | **Referencia antigua a FCVT**
  - Texto encontrado: `"Recuperación de contraseña — SGPC-FCVT",`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## BACKEND_SGPC_FCVT\core\models\publicaciones\base.py

- L?nea **252** | **Uso de Registrador en t?tulos**
  - Texto encontrado: `"El usuario registrador debe tener privilegios administrativos."`
  - Sugerencia: Revisar si debe decir Registrar. Ejemplo: Registrar Ponencia, Registrar Libro.

## BACKEND_SGPC_FCVT\core\publicaciones\services\publicaciones_factory_services.py

- L?nea **85** | **Uso de Registrador en t?tulos**
  - Texto encontrado: `{"admin_registrador": ["El usuario registrador debe ser administrador."]}`
  - Sugerencia: Revisar si debe decir Registrar. Ejemplo: Registrar Ponencia, Registrar Libro.

## BACKEND_SGPC_FCVT\core\publicaciones\utils\publicaciones_creation_context_utils.py

- L?nea **29** | **Uso de Registrador en t?tulos**
  - Texto encontrado: `{"detail": ["El administrador registrador no es válido."]}`
  - Sugerencia: Revisar si debe decir Registrar. Ejemplo: Registrar Ponencia, Registrar Libro.

## BACKEND_SGPC_FCVT\core\templates\emails\password_reset.html

- L?nea **7** | **Referencia antigua a FCVT**
  - Texto encontrado: `<div style="font-size:16px;font-weight:700;">SGPC-FCVT</div>`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **34** | **Referencia antigua a FCVT**
  - Texto encontrado: `Universidad Laica Eloy Alfaro de Manabí — FCVT`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## FRONTEND_SGPC_FCVT\index.html

- L?nea **10** | **Referencia antigua a FCVT**
  - Texto encontrado: `<title>SGPC-FCVT</title>`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## FRONTEND_SGPC_FCVT\package-lock.json

- L?nea **2** | **Referencia antigua a FCVT**
  - Texto encontrado: `"name": "frontend-sgpc-fcvt",`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

- L?nea **8** | **Referencia antigua a FCVT**
  - Texto encontrado: `"name": "frontend-sgpc-fcvt",`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## FRONTEND_SGPC_FCVT\package.json

- L?nea **2** | **Referencia antigua a FCVT**
  - Texto encontrado: `"name": "frontend-sgpc-fcvt",`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## FRONTEND_SGPC_FCVT\src\administracion\gestion-facultades-carreras\GestionFacultadesCarrerasView.vue

- L?nea **184** | **Referencia antigua a FCVT**
  - Texto encontrado: `placeholder: "Ej.: FCVT",`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## FRONTEND_SGPC_FCVT\src\publicaciones\articulo-alto-impacto\ArticuloAltoImpactoForm.vue

- L?nea **1480** | **Referencia antigua a FCVT**
  - Texto encontrado: `<style src="../componentes/sgpc-fcvt.css"></style>`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## FRONTEND_SGPC_FCVT\src\publicaciones\articulo-regional\ArticuloRegionalForm.vue

- L?nea **1427** | **Referencia antigua a FCVT**
  - Texto encontrado: `<style src="../componentes/sgpc-fcvt.css"></style>`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## FRONTEND_SGPC_FCVT\src\publicaciones\capitulo-libro\CapituloLibroForm.vue

- L?nea **1253** | **Referencia antigua a FCVT**
  - Texto encontrado: `<style src="../componentes/sgpc-fcvt.css"></style>`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## FRONTEND_SGPC_FCVT\src\publicaciones\detalle-publicacion\EditarPublicacionView.vue

- L?nea **1105** | **Referencia antigua a FCVT**
  - Texto encontrado: `<style src="../componentes/sgpc-fcvt.css"></style>`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## FRONTEND_SGPC_FCVT\src\publicaciones\libro\LibroForm.vue

- L?nea **1235** | **Referencia antigua a FCVT**
  - Texto encontrado: `<style src="../componentes/sgpc-fcvt.css"></style>`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

## FRONTEND_SGPC_FCVT\src\publicaciones\ponencia\PonenciaRegistro.vue

- L?nea **1315** | **Referencia antigua a FCVT**
  - Texto encontrado: `<style src="../componentes/sgpc-fcvt.css"></style>`
  - Sugerencia: Revisar si debe cambiarse a SGPC ULEAM o a una referencia institucional general.

