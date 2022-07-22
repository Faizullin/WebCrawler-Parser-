from django.conf.urls.static import static
from django.urls import path
from .views import *
urlpatterns = [
    path('', CrawlerIndex.as_view(),name='home'),
    path("search/",CrawlerSearch,name="search"),
    
    path('download/',Download,name='download'),
    path('accounts/login/', CrawlerLogin,name='login'),
    path('accounts/logout/', CrawlerLogout,name='logout'),
    path('accounts/register/', CrawlerRegister,name='register'),
    path('urls_list/',CrawlerUrlsList.as_view(),name='urls_list')
]
if settings.DEBUG:
    urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)