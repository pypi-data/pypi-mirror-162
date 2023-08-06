"""  URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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

from django.apps import apps  # https://docs.djangoproject.com/zh-hans/3.1/ref/applications/
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls import url

from video_play import views

app_name = 'video_play'

video_marker_model = apps.get_model(getattr(settings, 'VIDEO_MARKER_MODEL', 'video_play.Marker'))
video_play_model = apps.get_model(getattr(settings, 'VIDEO_PLAY_MODEL', 'video_play.VideosPlay'))
video_play_model_using = getattr(settings, 'VIDEO_PLAY_MODEL_USING', None)

urlpatterns = [
    # http://127.0.0.1:801/video/video_detail/3864
    path('video_detail/<int:pk>', views.detail, name='video_detail',
         kwargs={"model": video_play_model, 'using': video_play_model_using}),
    # http://127.0.0.1:801/video/video_markers/add/3864
    path('video_markers/add/<int:pk>', views.add_video_markers, name='add_video_markers',
         kwargs={"model": video_play_model, 'marker_model': video_marker_model, 'using': video_play_model_using}),
    path('video_markers/del', views.del_video_marker, name='del_video_marker',
         kwargs={'marker_model': video_marker_model, 'using': video_play_model_using}),
    path('video_markers/update', views.update_video_marker, name='update_video_marker',
         kwargs={'marker_model': video_marker_model, 'using': video_play_model_using}),
    path('mosaic/<int:pk>', views.mosaic, name='mosaic',
         kwargs={"model": video_play_model, 'using': video_play_model_using}),
    path('watermark/<int:pk>', views.watermark, name='watermark',
         kwargs={"model": video_play_model, 'using': video_play_model_using}),
    path('favorite/<int:pk>', views.favorite, name='favorite',
         kwargs={"model": video_play_model, 'using': video_play_model_using}),
    path('load_scenes/<slug:md5>', views.load_scenes, name='load_scenes',
         kwargs={"model": video_play_model, 'using': video_play_model_using}),
    path('video_markers/load_user_markers/<int:pk>', views.load_user_markers, name='load_user_markers',
         kwargs={"model": video_play_model, 'using': video_play_model_using}),
    path('load_markers/<slug:md5>', views.load_markers, name='load_markers',
         kwargs={"model": video_play_model, 'using': video_play_model_using}),
    path('save_markers/<slug:md5>', views.save_markers, name='save_markers',
         kwargs={"model": video_play_model, 'using': video_play_model_using}),
    url('v_resp/', views.stream_video),
]

if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # https://docs.djangoproject.com/zh-hans/2.2/ref/contrib/staticfiles/#static-file-development-view
    # 文档说明这个只在调试模式使用，但是我没看到相关代码
    urlpatterns += staticfiles_urlpatterns()
