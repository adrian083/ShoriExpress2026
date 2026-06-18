from django import template
from django.templatetags.static import static

register = template.Library()


@register.filter
def producto_imagen_url(producto):
    """URL para catálogo: subida (media) > ruta en static > placeholder."""
    if getattr(producto, "imagen", None) and getattr(producto.imagen, "name", None):
        return producto.imagen.url
    rel = (getattr(producto, "imagen_catalogo", None) or "").strip().lstrip("/")
    if rel:
        return static(rel)
    return static("productos/placeholder.svg")
