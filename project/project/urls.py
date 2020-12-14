"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import include, path
from django.contrib.auth import views as auth_views
#this are used to import static files like images....
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('nutrihacker/', include('nutrihacker.urls')),
    path('admin/', admin.site.urls),
    #to be able to work with template (will come back to it)
    # path('login/', auth_views.LoginView.as_view(template_name='index.html'), name='login')
    # path('logout/', auth_views.LogoutView.as_view(), name='logout')
]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#-------------------------Profile pic stuff --------------------------------------
if settings.DEBUG:
          urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
          
