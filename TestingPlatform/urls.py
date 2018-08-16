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
from django.views.static import serve
from rest_framework.documentation import include_docs_urls
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import obtain_jwt_token, verify_jwt_token

# from django.contrib import admin
import xadmin
from TestingPlatform.settings import MEDIA_ROOT, STATIC_ROOT
from case.views import ProductViewSet, ModuleCategoryViewSet, CaseSetViewSet, CaseViewSet, CaseReleteCaseSetViewSet, \
    TestTaskViewSet, CaseReleteTestTaskViewSet, CaseReleteCaseSetSortUpdateViewSet, CaseReleteTestTaskSortUpdateViewSet, \
    CaseScriptViewSet
from dataconfig.views import TestDataConfigViewSet, DataBaseConfigViewSet, UrlDataConfigViewSet
from device.views import DeviceViewSet, DeviceSyncView
from uitest.views import DeviceRelateApKViewSet, EnvConfigViewSet, TaskStartView, ApKConfigViewSet, WebConfigViewSet, \
    ClientReadyView, TaskStopView, ClientEnvCleaerView

router = DefaultRouter()
router.register(r'products', ProductViewSet, base_name='products')
router.register(r'modules', ModuleCategoryViewSet, base_name='modules')
router.register(r'casesets', CaseSetViewSet, base_name='casesets')
router.register(r'case', CaseViewSet, base_name='case')
router.register(r'case_relete_caseset', CaseReleteCaseSetViewSet, base_name='case_relete_caseset')
router.register(r'update_case_relete_sort', CaseReleteCaseSetSortUpdateViewSet, base_name='update_case_relete_sort')
router.register(r'case_relete_test_task', CaseReleteTestTaskViewSet, base_name='case_relete_test_task')
router.register(r'case_script', CaseScriptViewSet, base_name='case_script')
router.register(r'update_case_relete_testtask_sort', CaseReleteTestTaskSortUpdateViewSet,
                base_name='update_case_relete_testtask_sort')
# 测试任务
router.register(r'test_task', TestTaskViewSet, base_name='test_task')
router.register(r'device', DeviceViewSet, base_name='device')
router.register(r'data_config', TestDataConfigViewSet, base_name='data_config')
router.register(r'device_config', DeviceRelateApKViewSet, base_name='device_config')
router.register(r'task_env', EnvConfigViewSet, base_name='task_env')
router.register(r'database_config', DataBaseConfigViewSet, base_name='database_config')
router.register(r'url_config', UrlDataConfigViewSet, base_name='url_config')
router.register(r'apk_config', ApKConfigViewSet, base_name='apk_config')
router.register(r'web_config', WebConfigViewSet, base_name='web_config')

urlpatterns = [
    url(r'^xadmin/', xadmin.site.urls),
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^docs/', include_docs_urls(title='TestingPlatform')),

    url(r'^', include(router.urls)),
    url(r'^login/', obtain_jwt_token),
    url(r'^verify_jwt_token/', verify_jwt_token),
    # 任务开始
    url(r'^task_start', TaskStartView.as_view(), name="task_start"),
    # 设备状态同步
    url(r'^device_sync', DeviceSyncView.as_view(), name="device_sync"),
    # 执行机准备结果通知
    url(r'^client_ready', ClientReadyView.as_view(), name="client_ready"),
    # 停止任务
    url(r'^task_stop', TaskStopView.as_view(), name="task_stop"),
    # 执行机环境清理
    url(r'^client_env_clear', ClientEnvCleaerView.as_view(), name="client_env_clear"),
]
