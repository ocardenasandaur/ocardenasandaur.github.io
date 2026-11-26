# Instalación y mantenimiento de los álbumes

1. Haz una copia de seguridad del repositorio y comprueba si ya tienes algún workflow de publicación de Pages. No mantengas dos workflows que publiquen el mismo sitio. Si ya tienes uno personalizado, integra el paso de generación del índice en él en lugar de sustituirlo sin revisar.
2. Copia `index.html`, `data.json`, `media-index.json`, `scripts/build_media_index.py` y `.github/workflows/pages.yml` a sus rutas exactas en la raíz del repositorio. No borres las imágenes, CV, tesis ni otros archivos existentes. El ZIP contiene también la carpeta oculta `.github`.
3. En GitHub, abre Settings → Pages → Build and deployment → Source y selecciona **GitHub Actions**. Este workflow está diseñado para un sitio HTML estático, no para un sitio que requiere Jekyll. Si la rama publicada no es `main` o `master`, modifica `branches` en el workflow. En Actions, selecciona **Publish website and media index** → Run workflow, en la rama publicada (si la ejecución inicial no empezó o falló antes de seleccionar la fuente). Confirma que termina en verde y que la web sigue visible.
4. En adelante, sube archivos a `images/combate-medieval/`, `images/entrenamiento/`, `images/musica/`, `images/congresos/` o `images/viajes/`. Cada push a la rama configurada genera un índice nuevo y publica el sitio. No tienes que editar `media-index.json`. El índice generado vive en la publicación, no se vuelve a guardar en el repositorio.

## Formatos y portadas
- Imágenes: JPG, JPEG, PNG, WebP, GIF, AVIF. Vídeos: MP4 (preferentemente H.264/AAC) y WebM.
- Una imagen llamada `portada` con una extensión admitida (sin importar mayúsculas) tiene prioridad y aparece además como primera imagen dentro del álbum. Usa una sola portada por carpeta. Si no existe, se elige la primera imagen por orden alfabético; si no hay imágenes, se usa el fondo con icono.
- Solo se indexan archivos directamente dentro de cada una de las cinco carpetas. No se indexan subcarpetas ni archivos ocultos.
- No hay imágenes ni vídeos personales incluidos en el paquete. Los vídeos no se reproducen automáticamente. Procura comprimir los vídeos y evitar subir archivos muy grandes; el sitio y todos sus medios son públicos.

## Metadatos opcionales
El campo `photos` de cada registro de `interests` en `data.json` permite añadir información a un archivo detectado, sin duplicarlo. Ejemplo:

```json
{"src":"images/viajes/Toledo.jpg","caption":"Una tarde en Toledo","captionEn":"An afternoon in Toledo","location":"Toledo, España","locationEn":"Toledo, Spain","year":2025}
```

Se puede añadir `poster` con la ruta a una imagen para la miniatura de un vídeo (si está en la carpeta indexada, esa imagen también aparecerá en el álbum). Las rutas deben coincidir exactamente con el nombre real del archivo. El índice es la fuente de verdad: si borras un archivo, sus metadatos no lo harán reaparecer.

## Prueba local o alternativa manual
Desde la raíz del repositorio, ejecuta `python3 scripts/build_media_index.py` y luego `python3 -m http.server 8000`. Abre `http://localhost:8000`. Si prefieres conservar el sistema de publicación por rama, puedes generar y subir manualmente `media-index.json` cada vez que cambien los archivos, sin activar el workflow personalizado.
