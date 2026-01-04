"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from ninja import NinjaAPI
from app.api import auth, wallets, categories, transactions, search, budgets, recurring, debts, dashboard, chat

api = NinjaAPI(
    title="AI Smart Finance API",
    version="1.0.0",
    description="API for AI-powered personal finance management"
)

# Register API routers
api.add_router("/auth", auth.router, tags=["auth"])
api.add_router("/wallets", wallets.router, tags=["wallets"])
api.add_router("/categories", categories.router, tags=["categories"])
api.add_router("/transactions", transactions.router, tags=["transactions"])
api.add_router("/search", search.router, tags=["search"])
api.add_router("/budgets", budgets.router, tags=["budgets"])
api.add_router("/recurring", recurring.router, tags=["recurring"])
api.add_router("/debts", debts.router, tags=["debts"])
api.add_router("/dashboard", dashboard.router, tags=["dashboard"])
api.add_router("/chat", chat.router, tags=["chat"])

@api.get("/hello")
def hello(request):
    return {"message": "Hello, World!"}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", api.urls),
    path("auth/access-code", TemplateView.as_view(template_name="auth/access_code.html"), name="access_code"),
    path("dashboard/", TemplateView.as_view(template_name="dashboard/index.html"), name="dashboard"),
    path("transactions/", TemplateView.as_view(template_name="transactions/list.html"), name="transactions"),
    path("budgets/", TemplateView.as_view(template_name="budgets/index.html"), name="budgets"),
    path("chat/", TemplateView.as_view(template_name="chat/index.html"), name="chat"),
    path("settings/", TemplateView.as_view(template_name="settings/index.html"), name="settings"),
    path("", TemplateView.as_view(template_name="dashboard/index.html"), name="home"),
]

# Serve static and media files in development
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    # Serve static files from STATICFILES_DIRS (development)
    urlpatterns += staticfiles_urlpatterns()
    # Also serve from STATIC_ROOT if needed
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
