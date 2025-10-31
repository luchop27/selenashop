# apps/catalogo/views.py
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from .models import Categoria, Estilo, Producto


# =========================
#  VISTAS PÚBLICAS
# =========================

class ProductoListView(ListView):
    """
    Lista general de productos.
    /productos/?categoria=slug&estilo=slug&q=texto
    """
    model = Producto
    template_name = "catalogo/producto_list.html"  # usa siempre el mismo nombre
    context_object_name = "productos"
    paginate_by = 12

    def get_queryset(self):
        qs = (
            Producto.objects
            .filter(activo=True)
            .select_related("categoria", "estilo")
            .prefetch_related("imagenes", "variantes")
            .order_by("-created_at")
        )

        # ?categoria=vestidos
        categoria_slug = self.request.GET.get("categoria")
        if categoria_slug:
            qs = qs.filter(categoria__slug=categoria_slug, categoria__estado=True)

        # ?estilo=gala
        estilo_slug = self.request.GET.get("estilo")
        if estilo_slug:
            qs = qs.filter(estilo__slug=estilo_slug, estilo__activo=True)

        # ?q=blusa
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nombre__icontains=q)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categorias"] = Categoria.objects.filter(estado=True).order_by("posicion", "nombre")
        ctx["estilos"] = Estilo.objects.filter(activo=True).order_by("posicion", "nombre")
        return ctx


class ProductoDetailView(DetailView):
    """
    Detalle de un producto.
    /producto/<slug>/
    """
    model = Producto
    template_name = "catalogo/producto_detail.html"
    context_object_name = "producto"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Producto.objects
            .filter(activo=True)
            .select_related("categoria", "estilo")
            .prefetch_related("imagenes", "variantes")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        producto = self.object
        relacionados = (
            Producto.objects
            .filter(activo=True, categoria=producto.categoria)
            .exclude(pk=producto.pk)[:8]
        )
        ctx["relacionados"] = relacionados
        return ctx


class CategoriaProductoListView(ListView):
    """
    /categoria/<slug>/
    """
    model = Producto
    template_name = "catalogo/producto_list.html"
    context_object_name = "productos"
    paginate_by = 12

    def get_queryset(self):
        self.categoria = get_object_or_404(
            Categoria,
            slug=self.kwargs["slug"],
            estado=True
        )
        return (
            Producto.objects
            .filter(activo=True, categoria=self.categoria)
            .select_related("categoria", "estilo")
            .prefetch_related("imagenes", "variantes")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categoria_actual"] = self.categoria
        ctx["categorias"] = Categoria.objects.filter(estado=True)
        return ctx


class EstiloProductoListView(ListView):
    """
    /estilo/<slug>/
    """
    model = Producto
    template_name = "catalogo/producto_list.html"
    context_object_name = "productos"
    paginate_by = 12

    def get_queryset(self):
        self.estilo = get_object_or_404(
            Estilo,
            slug=self.kwargs["slug"],
            activo=True
        )
        return (
            Producto.objects
            .filter(activo=True, estilo=self.estilo)
            .select_related("categoria", "estilo")
            .prefetch_related("imagenes", "variantes")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["estilo_actual"] = self.estilo
        ctx["estilos"] = Estilo.objects.filter(activo=True)
        return ctx


# =========================
#  VISTAS DEL PANEL (admin-ecomus)
# =========================

def panel_productos_list(request):
    """
    Renderiza tu HTML del panel: admin-ecomus/product-list.html
    """
    productos = (
        Producto.objects
        .select_related("categoria", "estilo")
        .prefetch_related("variantes")
        .all()
    )
    return render(request, "product-list.html", {
        "productos": productos
    })


def panel_producto_crear(request):
    """
    Renderiza el HTML de crear producto del panel.
    Luego lo cambiamos a un ModelForm.
    """
    return render(request, "add-product.html")


def panel_categorias_list(request):
    categorias = Categoria.objects.filter(estado=True).order_by("posicion", "nombre")
    return render(request, "category-list.html", {
        "categorias": categorias
    })


def panel_categoria_crear(request):
    return render(request, "new-category.html")
