from django import template
from django.templatetags.static import static
from django.utils.text import slugify

register = template.Library()


@register.filter
def producto_imagen_url(producto):
    """URL para catálogo: subida (media) > ruta en static > productos/{slug}.jpg."""
    if getattr(producto, "imagen", None) and getattr(producto.imagen, "name", None):
        return producto.imagen.url
    rel = (getattr(producto, "imagen_catalogo", None) or "").strip().lstrip("/")
    if rel:
        return static(rel)
    slug = slugify(producto.nombre_producto) or f"producto-{producto.pk}"
    return static(f"productos/{slug}.jpg")
