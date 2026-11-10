# MusicPDF Studio

Webapp responsive en español para cargar partituras PDF o imágenes, previsualizarlas y convertirlas a MusicXML mediante Audiveris.

## Estado

- Interfaz web adaptable a iPad, móvil y ordenador.
- API FastAPI con límite de subida y endpoint de salud `/api/health`.
- La conversión real requiere instalar Audiveris y configurar `AUDIVERIS_BIN` en el servidor. La imagen Docker incluida todavía no instala Audiveris, por lo que el servicio no convertirá partituras hasta completar ese paso.
- MIDI no está implementado en esta versión.

## Ejecución local

Instala Python 3.11+, Audiveris y ejecuta:

```bash
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8000
```

Abre http://localhost:8000.

## Despliegue

Conecta este repositorio a un servicio compatible con Docker (por ejemplo Render). Antes de producción, instala Audiveris en la imagen, configura `AUDIVERIS_BIN`, añade limpieza periódica de trabajos temporales, límites de abuso y política de privacidad. Documentación CLI: https://audiveris.github.io/audiveris/_pages/guides/advanced/cli/
