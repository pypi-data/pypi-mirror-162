# 说明

Django 的视频播放器程序，现在主要是用于视频添加标记。

## 打包

```sh
cd D:\git_ldsxp\lds_spider\lds_site\django_video_play && python setup.py sdist
```

## 安装

```sh
# 本地安装
pip install django_video_play-0.0.1.tar.gz
```

添加设置

```python
INSTALLED_APPS = [
    ...
    'video_play',
    ...
]
```

模型设置的例子

```python
VIDEO_MARKER_MODEL = 'video.Marker'
VIDEO_PLAY_MODEL = 'video.Videos'
VIDEO_PLAY_MODEL_USING = 'video'
VIDEO_PLAY_DIR = VIDEO_DIR / 'video'
# 设置快速添加的标签名字
TAGS_READONLY = '标签1,标签1,其他标签'
# 后台编辑的链接
VIDEO_PLAY_ADMIN_EDIT_URL = '/admin/video_play/videosplay/{}/change/'
```

urls 设置

```python
urlpatterns = [
    ...
    path('video_play/', include('video_play.urls')),
    ...
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

继承模型需要覆盖的内容

```python
    @property
    def thumb_url(self):
        print('需要覆盖 thumb_url，支持预览图')
        return

    @property
    def mediabook_url(self):
        print('需要覆盖 mediabook_url，支持预览视频')
        return

    @property
    def videos_model(self):
        print('需要覆盖 model_videos，支持视频播放')
        return
```

