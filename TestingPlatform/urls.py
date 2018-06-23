"""TestingPlatform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
# from django.contrib import admin
import xadmin
from TestingPlatform.settings import MEDIA_ROOT, STATIC_ROOT
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token
from case.views import ProductViewSet, ModuleCategoryViewSet, CaseSetViewSet,CaseReleteCaseSetSet

router = DefaultRouter()
router.register(r'products', ProductViewSet, base_name='products')
router.register(r'modules', ModuleCategoryViewSet, base_name='modules')
router.register(r'casesets', CaseSetViewSet, base_name='casesets')
router.register(r'casereletecaseset', CaseReleteCaseSetSet, base_name='casereletecaseset')
urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include_docs_urls(title='TestingPlatform')),

    url(r'^', include(router.urls)),
    url(r'^login/', obtain_jwt_token),
    url(r'^verify_jwt_token/', verify_jwt_token),
]
