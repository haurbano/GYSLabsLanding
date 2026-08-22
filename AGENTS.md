# AGENTS.md — GYS Labs Landing

Landing estática de GYS Labs: `index.html` + `styles.css`, sin build step,
framework ni backend. Cloudflare despliega el repositorio según
`wrangler.jsonc`; probar localmente abriendo el HTML o con un servidor
estático, sin añadir dependencias por defecto.

## Archivos

| Archivo | Rol |
|---|---|
| `index.html` | Contenido, CTAs y carga de observabilidad |
| `styles.css` | Todo el estilo de la landing |
| `sentry.js` | Configuración de errores del navegador, separada para no ensuciar el HTML |
| `tests/test_observability.py` | Contrato estático de hosts, eventos y protección de errores |
| `wrangler.jsonc` | Configuración de despliegue Cloudflare |

## Observabilidad compartida Haurtech

| Host | Uso | Acceso |
|---|---|---|
| `analytics.haurtech.com` | Panel Umami | Cloudflare Access |
| `track.haurtech.com` | Tracker de la landing | público |
| `logs.haurtech.com` | Panel GlitchTip | Cloudflare Access |
| `ingest.haurtech.com` | Errores Sentry/GlitchTip | público |

El website de Umami es `gyslabs.com`; `index.html` carga el script desde
`track.haurtech.com`. Solo están permitidos los eventos semánticos literales
`contact_email` y `contact_whatsapp`. Nunca agregar al evento el email,
teléfono, mensaje, URL de WhatsApp, parámetros de campaña u otra propiedad
dinámica.

`index.html` carga el SDK y luego `sentry.js`. Ese archivo debe conservar
`sendDefaultPii: false`, cero breadcrumbs y el scrub de request, usuario,
extras y mensajes de excepción; la telemetría no guarda contenido ni
identidad del visitante. El DSN va a `ingest.haurtech.com` y no es un secreto
que deba copiarse a documentos. Bloqueos por ad blocker o red deben ser
inofensivos para la página.

La fuente operativa del stack es el repositorio privado
`GysLabs/infra/haurtech-observability`; no desplegar Umami o GlitchTip desde
este repositorio.

## Verificación

```bash
python3 -m unittest tests/test_observability.py -v
```

Cuando cambie la instrumentación, ampliar ese test para comprobar los hosts,
eventos y salvaguardas de privacidad antes de abrir un PR.
