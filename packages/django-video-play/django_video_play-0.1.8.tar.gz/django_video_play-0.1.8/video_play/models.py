import os
import datetime
from pathlib import Path

from ilds.file import get_file_md5

from django.apps import apps  # https://docs.djangoproject.com/zh-hans/3.1/ref/applications/
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.conf import settings
from django_extensions.db.models import CreationDateTimeField, ModificationDateTimeField

from model_utils.models import TimeStampedModel

video_play_model_using = getattr(settings, 'VIDEO_PLAY_MODEL_USING', None)

VIDEO_PLAY_ADMIN_EDIT_URL = getattr(settings, 'VIDEO_PLAY_ADMIN_EDIT_URL', '/admin/video_play/videosplay/{}/change/')

SETTLEMENT_VR_PROJECTION_ITEMS = (
    ('NONE', 'NONE'),  # 该视频不是 360 视频
    ('AUTO', 'AUTO'),  # 检查 player.mediainfo.projection 当前视频是否为 360 视频
    ('180', '180'),  # 该视频是半球形，用户应该不能向后看
    ('360', '360'),  # '360', 'Sphere', or 'equirectangular' 视频是一个球体
    ('Cube', 'Cube'),  # or '360_CUBE' 该视频是一个立方体
    ('360_LR', '360_LR'),  # 用于并排 360 度视频
    ('360_TB', '360_TB'),  # 用于从上到下的 360 视频
    ('EAC', 'EAC'),  # 用于等角立方体贴图视频
    ('EAC_LR', 'EAC_LR'),  # 用于并排的等角立方体贴图视频
)


class VideosMarker(TimeStampedModel):
    name = models.CharField(verbose_name='标签', max_length=256, default='标签')
    time = models.FloatField(verbose_name='时间', blank=True, null=True)
    fps = models.FloatField(verbose_name='帧率', blank=True, null=True)
    notes = models.TextField(verbose_name='备注', blank=True)

    def __str__(self):
        return f'{self.name} <时间：[{self.time}] 帧率：[{self.fps}] 备注：[{self.notes}]>'

    class Meta:
        abstract = True
        verbose_name = "标记"
        verbose_name_plural = verbose_name


class VideosPlayThrough(models.Model):
    marker = models.ForeignKey('Marker', on_delete=models.CASCADE)
    video = models.ForeignKey('VideosPlay', on_delete=models.CASCADE)
    created = models.DateTimeField(verbose_name='创建时间', default=timezone.now)

    class Meta:
        verbose_name = "视频标签中间件"
        verbose_name_plural = verbose_name


class Videos(models.Model):
    """
    定义一个通用的视频信息模型
    """

    # percent = models.CharField(verbose_name='好评率', max_length=100, blank=True)
    # data_entrycode = models.CharField(verbose_name='data_entrycode', max_length=100, blank=True)
    # data_id = models.CharField(verbose_name='data_id', max_length=100, blank=True)
    # data_segment = models.CharField(verbose_name='data_segment', max_length=100, blank=True)
    # is_premium = models.BooleanField(verbose_name='会员视频', default=False)

    vkey = models.CharField(verbose_name='vkey', max_length=256, blank=True)
    title = models.CharField(verbose_name='标题', max_length=256, blank=True)
    title_cn = models.CharField(verbose_name='中文标题', max_length=256, blank=True)
    thumbnail = models.CharField(verbose_name='高清缩略图', max_length=100, blank=True)

    pornstars_name = models.CharField(verbose_name='色情明星', max_length=256, blank=True, null=True)
    user_type = models.CharField(verbose_name='色情明星类型', max_length=256, blank=True, null=True)

    # 视频基本信息（可以自动获取）
    is_hd = models.BooleanField(verbose_name='高清', default=False)
    width = models.IntegerField(verbose_name='宽度', default=0)
    high = models.IntegerField(verbose_name='高', default=0)
    bitrate = models.IntegerField(verbose_name='比特率', default=0)
    md5 = models.CharField(verbose_name='MD5', max_length=32, blank=True)
    sha1 = models.CharField(verbose_name='SHA1', max_length=64, blank=True, null=True,
                            help_text='SHA-1 40位 预留 64 位字段')
    hash = models.CharField(verbose_name='Hash', max_length=136, blank=True, null=True,
                            help_text='sha256[哈希算法名字，统一用小写]:[分隔符]128[哈希]，最多字符数 136')
    # video_file = models.CharField(verbose_name='视频文件', max_length=256, blank=True)
    video_file_dir = models.CharField(verbose_name='文件所在路径', max_length=256, blank=True)
    video_file_name = models.CharField(verbose_name='文件名', max_length=256, blank=True)
    video_extension = models.CharField(verbose_name='后缀名', max_length=50, blank=True)
    video_file_size = models.IntegerField(verbose_name='文件大小', default=0)
    views = models.CharField(verbose_name='观看次数', max_length=50, blank=True)
    added = models.CharField(verbose_name='添加于', max_length=100, blank=True)

    # 视频基本信息
    vr_projection = models.CharField(verbose_name='VR投影', max_length=10, choices=SETTLEMENT_VR_PROJECTION_ITEMS,
                                     default='NONE', blank=True)
    type = models.CharField(verbose_name='类型', max_length=50, blank=True, null=True)
    is_mosaic = models.BooleanField(verbose_name='马赛克', default=False)
    is_watermark = models.BooleanField(verbose_name='水印', default=False)
    related_file = models.ForeignKey('self', verbose_name='相关文件', blank=True, null=True, on_delete=models.SET_NULL)

    # 其他信息
    descriptions = models.TextField(verbose_name='描述', blank=True)
    tags_text = models.CharField(verbose_name='标签文本', max_length=365, blank=True)
    is_pbf = models.BooleanField(verbose_name='暴风影音书签', default=False)
    is_mark_file = models.BooleanField(verbose_name='标记文件', default=False)
    notes = models.TextField(verbose_name='备注', blank=True)
    source = models.CharField(verbose_name='资料来源', max_length=256, blank=True)
    is_delete = models.BooleanField(verbose_name='删除', default=False)
    is_favorite = models.BooleanField(verbose_name='收藏', default=False)
    is_download = models.BooleanField(verbose_name='下载', default=False)
    is_err = models.BooleanField(verbose_name='错误', default=False)
    err_info = models.TextField(verbose_name='错误信息', blank=True)
    is_ignore = models.BooleanField(verbose_name='忽略', default=False, help_text='收藏的文件，如果忽略也可以不备份')

    save_as = models.CharField(verbose_name='文件保存在', max_length=500, blank=True, null=True)
    create_name = models.CharField(verbose_name='创建者名称', max_length=100, blank=True)
    write_name = models.CharField(verbose_name='最后修改者名称', max_length=100, blank=True)
    created = models.DateTimeField(verbose_name='创建时间', default=timezone.now)
    # modified = models.DateTimeField(verbose_name='修改时间', default=timezone.now)
    # 支持 obj.save(update_modified=False)，不保存修改时间
    modified = ModificationDateTimeField(verbose_name='修改时间')
    is_repeat = models.BooleanField(verbose_name='重复', default=False)
    views_count = models.IntegerField(verbose_name='查看次数', default=0)
    last_viewed_time = models.DateTimeField(verbose_name='上次查看时间', blank=True, null=True)

    # https://github.com/ldsxp/videoproject/blob/master/video/models.py#L56
    # liked = models.ManyToManyField(settings.AUTH_USER_MODEL,
    #                                blank=True, related_name="liked_videos")

    class Meta:
        abstract = True
        verbose_name = "视频"
        verbose_name_plural = verbose_name

    def update_views(self):
        if isinstance(self.last_viewed_time, datetime.datetime):
            # 访问间隔不到 60 分钟
            if self.last_viewed_time + datetime.timedelta(minutes=60) >= timezone.now():
                self.last_viewed_time = timezone.now()
                self.save(update_fields=['last_viewed_time'])
                return self.views_count

        self.views_count += 1
        self.last_viewed_time = timezone.now()
        self.save(update_fields=['views_count', 'last_viewed_time'])
        return self.views_count

    # def switch_like(self, user):
    #     if user in self.liked.all():
    #         self.liked.remove(user)
    #     else:
    #         self.liked.add(user)

    def switch_favorite(self):
        if self.is_favorite:
            self.is_favorite = False
        else:
            self.is_favorite = True
        self.save(update_fields=('is_favorite',))

    def switch_watermark(self):
        if self.is_watermark:
            self.is_watermark = False
        else:
            self.is_watermark = True
        self.save(update_fields=('is_watermark',))

    def switch_mosaic(self):
        if self.is_mosaic:
            self.is_mosaic = False
        else:
            self.is_mosaic = True
        self.save(update_fields=('is_mosaic',))

    def check_md5(self):
        """
        校验文件md5是否正确

        例子：
        print(Md5File.objects.get(pk=3000).check_md5())
        """
        # print(self.md5, self.file)
        if self.md5 and os.path.exists(self.video_file):
            if get_file_md5(self.video_file) == self.md5:
                return True

    def get_title(self):
        if self.title:
            return self.title
        elif self.title_cn:
            return self.title_cn
        elif self.md5:
            return self.md5
        else:
            return '无'

    @property
    def video_file(self):
        return os.path.join(self.video_file_dir, self.video_file_name + self.video_extension)

    def get_play_path(self):
        """
        获取视频文件路径

        注意：需要覆盖她，因为只有在调试模式我们支持传递本地路径（路径前面添加::），
             不是本地路径的时候播放文件：VIDEO_PLAY_DIR / self.get_play_path()
        """
        return f"::{self.video_file}"

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

    @property
    def admin_edit_url(self):
        """
        获取视频后台编辑的URL
        """
        return VIDEO_PLAY_ADMIN_EDIT_URL.format(self.id)

    def display_thumb(self):
        """
        自定义的 list_display 显示预览图

        from django.conf.urls.static import static
        urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        display_thumb.allow_tags = True  # 设置不转义 HTML 输出。为了避免 XSS 漏洞，应该使用 format_html() 转义用户提供的输入
        """
        thumb_url = self.thumb_url
        if thumb_url:
            thumb_html = format_html(
                '{}<br>'
                '<img src="{}" width="320" height="180" alt="{}">',
                self.get_title(),
                thumb_url, self.title
            )
        else:
            # thumb = os.path.join(settings.MEDIA_URL, 'placeholder.png')
            thumb_html = self.get_title()

        return thumb_html

    display_thumb.short_description = '预览图'

    def display_play(self):
        """
        自定义的 播放 按钮
        """
        return format_html(
            '<a href="/video_play/video_detail/{}" target="_blank">Play</a><br>',
            self.id,
        )

    display_play.short_description = '播放'

    def display_mediabook(self):
        """
        自定义的 list_display 显示

        from django.conf.urls.static import static
        urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
        display_mediabook.allow_tags = True  # 设置不转义 HTML 输出。为了避免 XSS 漏洞，应该使用 format_html() 转义用户提供的输入

        autoplay="autoplay"  取消了自动播放
        """
        html = """
        <video class="video" controls="controls" controlslist="nodownload"  width="320" height="180"
            disablePictureInPicture>
            <source src="{}" type="video/mp4">
        </video>
        """
        mediabook_url = self.mediabook_url
        if mediabook_url:
            mediabook_html = format_html(html, mediabook_url)
        else:
            # mediabook = os.path.join(settings.MEDIA_URL, 'placeholder.png')
            mediabook_html = '-'

        return mediabook_html

    display_mediabook.short_description = '预览视频'

    def get_absolute_url(self):
        return reverse('video_play:video_detail', kwargs={'pk': self.pk, 'model': self.videos_model})

    def get_previous(self):
        """上一个"""
        try:
            return self.videos_model.objects.using(video_play_model_using).get(pk=self.pk - 1)
        except Exception as e:
            print('get_previous_url Exception', e)

    def get_next(self):
        """下一个"""
        try:
            return self.videos_model.objects.using(video_play_model_using).get(pk=self.pk + 1)
        except Exception as e:
            print('get_next_url Exception', e)

    def get_previous_html(self):
        """上一个"""
        obj = self.get_previous()
        print(obj)
        if obj:
            return mark_safe(
                f'<a href="{obj.get_absolute_url()}" class="pull-left">上一个 {obj.title or obj.title_cn or obj.vkey}</a>')

    def get_next_html(self):
        """下一个"""
        obj = self.get_next()
        print(obj)
        if obj:
            return mark_safe(
                f'<a href="{obj.get_absolute_url()}" class="pull-right">下一个 {obj.title or obj.title_cn or obj.vkey}</a>')


class Marker(VideosMarker):
    ...


class VideosPlay(Videos):
    """
    视频播放
    """

    markers = models.ManyToManyField(Marker, through='VideosPlayThrough')

    @property
    def videos_model(self):
        return VideosPlay

    # class Meta:
    #     verbose_name = "视频播放"
    #     verbose_name_plural = verbose_name

    def __str__(self):
        if self.title_cn:
            return self.title_cn
        elif self.title:
            return self.title
        else:
            return self.vkey
