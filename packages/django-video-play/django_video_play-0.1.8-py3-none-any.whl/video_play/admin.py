from django.contrib import admin
from django.db.models import Sum
from django.db import transaction
from django.contrib import messages  # 常用：INFO（默认）WARNING（黄色）、ERROR（红色）
from django.utils.safestring import mark_safe
from django.conf import settings
from django.utils import timezone

import os
import time
from pathlib import Path

from djlds.admin import MultiDBModelAdmin

from .util import human_size
from .models import Marker, VideosPlayThrough, VideosPlay


class VideosPlayMultiDBModelAdmin(MultiDBModelAdmin):
    using = video_play_model_using = getattr(settings, 'VIDEO_PLAY_MODEL_USING', None)


@admin.register(Marker, site=None)
class MarkerAdmin(VideosPlayMultiDBModelAdmin):
    ...


@admin.register(VideosPlayThrough, site=None)
class VideosPlayThroughAdmin(VideosPlayMultiDBModelAdmin):
    list_display = ('video', 'marker',)
    raw_id_fields = ('marker', 'video',)
    search_fields = ('marker__name', 'marker__notes', 'video__title', 'video__notes',)


@admin.register(VideosPlay, site=None)
class VideosPlayAdmin(VideosPlayMultiDBModelAdmin):
    list_display = (
        'display_thumb', 'display_mediabook', 'display_play', 'source', 'is_favorite', 'is_repeat', 'is_ignore',
        'is_download', 'is_delete', 'is_err', 'notes', 'tags_text', 'views_count', 'created',)
    list_filter = (
        'source', 'tags_text', 'is_download', 'is_favorite', 'is_mark_file', 'is_repeat', 'is_ignore', 'is_err',
        'is_delete')
    search_fields = (
        'title', 'title_cn', 'video_file_name', 'video_file_dir', 'vkey', 'md5', 'tags_text', 'pornstars_name',
        'descriptions', 'source')
    list_editable = ('is_repeat', 'is_ignore', 'is_download', 'is_favorite', 'is_delete',)
    raw_id_fields = ('related_file',)
    actions = ['action_user_has_deleted_video', 'action_watched_preview', 'action_mark_downloaded_files',
               'action_calc_file_size', 'action_move_markers', 'action_delete_files', 'action_delete_files_2',
               'action_set_vr_projection_360',
               ]
    actions_on_bottom = True

    def action_calc_file_size(self, request, queryset):
        """计算选择内容的文件大小"""
        field = 'video_file_size'
        exclude_count = queryset.filter(**{field: None}).count()
        if exclude_count:
            info = f'（跳过 {exclude_count} 个文件大小为空的内容）'
            queryset = queryset.exclude(**{field: None})
        else:
            info = ''
        file_size = queryset.aggregate(**{field: Sum(field)})[field]
        # print(human_size(file_size))
        self.message_user(request, f'选择内容的文件大小：{human_size(file_size)}' + info, level=messages.INFO)

    action_calc_file_size.short_description = "计算选择内容的文件大小"

    def action_move_markers(self, request, queryset):
        """
        移动标记信息
        """
        is_err = False
        marker_count = 0
        count = queryset.count()

        if count > 2:
            self.message_user(request, '选择内容多于 2 个', level=messages.WARNING)
            is_err = True
        elif count < 2:
            self.message_user(request, '选择内容少于 2 个', level=messages.WARNING)
            is_err = True

        obj_1 = None
        obj_2 = None

        for obj in queryset:
            if obj.is_delete:
                obj_1 = obj
            else:
                obj_2 = obj

        try:
            if obj_1.is_delete == obj_2.is_delete:
                self.message_user(request, '选择内容中，需要一个标记为删除', level=messages.WARNING)
                is_err = True
        except Exception as e:
            self.message_user(request, f'选择内容中，需要一个标记为删除', level=messages.WARNING)
            is_err = True

        if is_err:
            self.message_user(request, f'说明：选择两个相同视频的内容，移动内容标记删除的标记到另一个内容。', level=messages.INFO)
            return

        with transaction.atomic():
            for marker_obj in obj_1.markers.all():
                # print(marker_obj)
                marker_count += 1
                obj_1.markers.remove(marker_obj)
                # 添加标记到视频
                obj_2.markers.add(marker_obj)

        self.message_user(request, f'移动标记信息：{marker_count}', level=messages.INFO)

    action_move_markers.short_description = "移动标记信息"

    def action_delete_files(self, request, queryset, is_delete=True):
        """
        删除视频文件
        """
        count = queryset.count()
        download_count = 0

        for obj in queryset:
            video_file = obj.video_file
            if video_file and os.path.exists(video_file):
                os.remove(video_file)
                download_count += 1
                if is_delete:
                    obj.is_delete = True
                    obj.save(update_fields=('is_delete',))

        self.message_user(request, f'选择文件 {count}，删除文件 {download_count}', level=messages.INFO)

    action_delete_files.short_description = "删除视频文件"

    def action_delete_files_2(self, request, queryset):
        """
        删除视频文件(不标记内容为删除)
        """
        self.action_delete_files(request, queryset, is_delete=False)

        self.message_user(request, '只删除了文件，没有标记内容为删除', level=messages.INFO)

    action_delete_files_2.short_description = "删除视频文件(不标记内容为删除)"

    def action_set_vr_projection_360(self, request, queryset):
        """
        更新选中的内容 VR 投影（vr_projection）为 360
        """
        self.message_user(request, f'更新 {queryset.update(vr_projection=360)} 个内容的 VR 投影（vr_projection）为 360',
                          level=messages.INFO)

    action_set_vr_projection_360.short_description = "更新选中的内容 VR 投影（vr_projection）为 360"

    def view_on_site(self, obj):
        """
        我们使用多个数据库的时候，直接返回地址比较方便
        """
        return f'/video_play/video_detail/{obj.id}'

    def get_actions(self, request):
        # https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/
        actions = super().get_actions(request)
        if request.user.username.upper() != 'LDS':
            if 'delete_selected' in actions:
                del actions['delete_selected']
        return actions
