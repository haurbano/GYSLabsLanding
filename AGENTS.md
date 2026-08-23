# AGENTS.md — GYS Labs Landing

Landing estática de GYS Labs: HTML plano + un solo `styles.css`, sin build
step, framework ni backend. Cloudflare despliega el repositorio según
`wrangler.jsonc`; probar localmente abriendo el HTML o con un servidor
estático, sin añadir dependencias por defecto.

## Tres páginas, un solo sitio

| URL | Archivo | Qué vende |
|---|---|---|
| `/` | `index.html` | Solo GYS Labs: qué es la empresa y la sección "¿Qué hacemos?" con una tarjeta por servicio |
| `/agents` | `agents/index.html` | Agentes de IA: experto a la medida y proceso automatizado |
| `/greentax` | `greentax/index.html` | GreenTax: certificación ambiental ante la UPME, con "Ingresar" al portal de clientes |

La raíz **no** habla de producto: las dos tarjetas de servicio son la única
puerta a `/agents` y `/greentax`. Al agregar un servicio nuevo va una tarjeta
más ahí y una carpeta más acá, no una sección nueva en la home.

El botón "Ingresar" de `/greentax` apunta a
`https://greentax.gyslabs.com/clientes/` — **plural y en español**. Es el path
real del portal (`nginx/templates/default.conf.template` en
`productos/greentax-dashboard`); `/clients/` da 404.

Las subpáginas referencian `/styles.css` y `/sentry.js` con path absoluto para
que resuelvan desde cualquier profundidad.

## Archivos

| Archivo | Rol |
|---|---|
| `index.html`, `agents/index.html`, `greentax/index.html` | Contenido, CTAs y carga de observabilidad de cada página |
| `styles.css` | Todo el estilo de las tres páginas — un solo sistema, sin CSS por página |
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

El website de Umami es `gyslabs.com`; **las tres páginas** cargan el script
desde `track.haurtech.com`. Solo están permitidos los eventos semánticos
literales `contact_email` y `contact_whatsapp`. Nunca agregar al evento el
email, teléfono, mensaje, URL de WhatsApp, parámetros de campaña u otra
propiedad dinámica.

Los clics a `/agents`, `/greentax` y al portal de clientes **no están
instrumentados** a propósito: medirlos exigiría nombres nuevos en la
allowlist. Si se agregan, tienen que ser literales y sin propiedades, y el
test de abajo hay que ampliarlo en el mismo cambio.

Cada página carga el SDK y luego `sentry.js`. Ese archivo debe conservar
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

El test corre sobre las **tres** páginas: hosts, eventos permitidos, ausencia
de propiedades dinámicas, y que los enlaces entre páginas y los anclas
internos existan de verdad. Cuando cambie la instrumentación o se agregue una
página, ampliar `PAGES` y el test antes de abrir un PR.

## Verificar el render en móvil

Chrome headless **no aplica el meta viewport**: `--window-size=390,844` da un
viewport de escritorio recortado a 390 px, y todo se ve desbordado aunque el
CSS esté bien (la landing original falla igual). Para un viewport real de
390 px, servir el sitio y meterlo en un iframe:

```bash
python3 -m http.server 8791 &
cat > __frame.html <<'EOF'
<!doctype html><meta charset="utf-8"><body style="margin:0">
<iframe src="http://127.0.0.1:8791/greentax" style="width:390px;height:3000px;border:0;display:block"></iframe>
EOF
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --window-size=400,3000 --screenshot=out.png http://127.0.0.1:8791/__frame.html
rm __frame.html
```
