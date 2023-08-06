import re
import os
import csv
import json
from pathlib import Path

import mimetypes
from wsgiref.util import FileWrapper

from django.http import StreamingHttpResponse
from django.shortcuts import render
from django.conf import settings
from django.shortcuts import get_object_or_404, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe

from video_play.version import version

VIDEO_PLAY_DIR = settings.VIDEO_PLAY_DIR

MARKERS_DIR = Path(settings.MEDIA_ROOT) / 'markers'
if not MARKERS_DIR.exists():
    MARKERS_DIR.mkdir(parents=True)

SCENES_DIR = Path(settings.MEDIA_ROOT) / 'scenes'

TAGS_READONLY = '标签1,标签1,其他标签'

# if not SCENES_DIR.exists():
#     SCENES_DIR.mkdir()


def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
    with open(file_name, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data


def stream_video(request):
    """将视频文件以流媒体的方式响应"""
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    range_match = range_re.match(range_header)
    path = request.GET.get('path')
    if '::' in path and settings.DEBUG:
        video_file = path[2:]
    else:
        video_file = VIDEO_PLAY_DIR / path
    size = os.path.getsize(video_file)
    content_type, encoding = mimetypes.guess_type(str(video_file))
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = first_byte + 1024 * 1024 * 10
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(file_iterator(video_file, offset=first_byte, length=length), status=206,
                                     content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
        print(f'path:{path}\tvideo_file:{video_file}|size:{size}\tfirst_byte:{first_byte}\tlast_byte:{last_byte}')
    else:
        # 不是以视频流方式的获取时，以生成器方式返回整个文件，节省内存
        print(f'path:{path}\tvideo_file:{video_file}|size:{size}\tcontent_type:{content_type}')
        resp = StreamingHttpResponse(FileWrapper(open(video_file, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    # print(resp)
    return resp


# @csrf_protect
@login_required
def detail(request, model, pk, using=None):
    # '/test_resp/'+test
    print(model, pk)

    try:
        video = model.objects.using(using).get(pk=pk)
    except Exception as e:
        return HttpResponse(str(e))

    # video_src = r"/video_play/v_resp/?path=::D:\迅雷下载\eagle-360.mp4"
    video_src = r"/video_play/v_resp/?path=" + video.get_play_path()
    markers = []
    for marker in video.markers.all().order_by('time'):
        markers.append({'time': float(marker.time), 'text': marker.name, 'id': marker.id, })
    print(markers)
    video.update_views()
    return render(request, 'video_detail.html',
                  {'video': video, 'markers': mark_safe(json.dumps(markers, ensure_ascii=False)),
                   'video_src': video_src, 'autoplay': 'autoplay', 'tags_readonly': TAGS_READONLY,
                   'version': version, })


# @csrf_protect
@login_required
def add_video_markers(request, model, marker_model, pk, using=None):
    """
    添加视频标记
    """
    if request.method == 'POST':
        # print(request)
        ret = {}
        # data = json.loads(request.body)
        # env = request.POST['data']
        data = request.POST.get("data")
        if data:
            data = json.loads(data)[0]
        else:
            return HttpResponse('None')
        print(data, model, pk)

        marker_name = data['text'] or '标记'
        marker_time = data['time']

        # 创建标记
        marker, is_created = marker_model.objects.using(using).get_or_create(name=marker_name, time=marker_time)

        # 添加创建的标记到视频
        videos = model.objects.using(using).get(pk=pk)
        videos.markers.add(marker)
        # videos.markers.create(name=marker_name, time=marker_time)
        # 移除标记
        # print(videos.markers.remove(marker))
        # # 全部移除
        # videos.markers.all().delete()
        # print('查看标记', videos.markers.all())

        markers = [
            {
                'id': marker.id,
                'time': marker_time,
                'text': marker_name,
                # 'overlayText': '标记显示',
                # 'class': 'custom-marker'
            }
        ]

        ret = {'code': 200,
               'msg': '添加成功',
               'data': markers,
               }
        return HttpResponse(json.dumps(ret))
    else:
        return HttpResponse('None')


@login_required
def del_video_marker(request, marker_model, using=None):
    """
    删除视频标记
    """
    if request.method == 'POST':
        # print(request)
        marker_pk = request.POST.get("data")
        if marker_pk:
            # 删除标记
            marker = marker_model.objects.using(using).get(pk=marker_pk).delete()
            print(marker, marker_model, marker_pk)
            ret = {'code': 200,
                   'msg': '删除成功',
                   }
            return HttpResponse(json.dumps(ret))
        else:
            return HttpResponse('None')
    else:
        return HttpResponse('None')


@login_required
def update_video_marker(request, marker_model, using=None):
    """
    删除视频标记
    """
    if request.method == 'POST':
        # print(request)
        data = request.POST.get("data")
        if data:
            data = json.loads(data)
        else:
            return HttpResponse('None')
        print(data, marker_model, using)
        marker_pk = data['marker_id']
        marker_name = data['text'] or '标记'
        if marker_pk:
            # 更新标记
            marker = marker_model.objects.using(using).get(pk=marker_pk)
            marker.name = marker_name
            marker.save(update_fields=('name',))
            markers = [
                {
                    'id': marker.id,
                    'time': marker.time,
                    'text': marker.name,
                    # 'overlayText': '标记显示',
                    # 'class': 'custom-marker'
                }
            ]
            ret = {'code': 200,
                   'msg': '更新成功',
                   'data': markers,
                   }
            print(marker, marker_model, marker_pk)
            return HttpResponse(json.dumps(ret))
        else:
            return HttpResponse('None')
    else:
        return HttpResponse('None')


def switch_bool(request, model, pk, name, using):
    """
    切换标记
    """
    if request.method == 'POST':
        data = request.POST.get("data")

        videos = model.objects.using(using).get(pk=pk)
        if data.startswith('◻'):
            ret_data = data.replace('◻', '☑', 1)
            # videos.is_mosaic = True
            setattr(videos, name, True)
        elif data.startswith('☑'):
            ret_data = data.replace('☑', '◻', 1)
            # videos.is_mosaic = False
            setattr(videos, name, False)
        else:
            return HttpResponse('未知参数')
        videos.save(update_fields=(name,))
        print(data, ret_data)
        ret = {'code': 200,
               'msg': '',
               'data': ret_data,
               }
        return HttpResponse(json.dumps(ret))
    else:
        return HttpResponse('None')


@login_required
def mosaic(request, model, pk, using=None):
    """
    马赛克
    """
    return switch_bool(request, model, pk, 'is_mosaic', using)


@login_required
def watermark(request, model, pk, using=None):
    """
    水印
    """
    return switch_bool(request, model, pk, 'is_watermark', using)


@login_required
def favorite(request, model, pk, using=None):
    """
    收藏
    """
    return switch_bool(request, model, pk, 'is_favorite', using)


@login_required
def load_scenes(request, model, md5, using=None):
    """
    载入场景
    """
    data_type = request.POST.get("type")
    file = SCENES_DIR / f'{md5}.csv'

    markers = []
    # 读取csv文件
    with open(file, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f)  # delimiter=':', quoting=csv.QUOTE_NONE

        iter_reader = iter(reader)
        header = next(iter_reader)  # fieldnames
        print('load_scenes', file, header, data_type)

        try:
            for row in iter_reader:
                # 多添加 0.1 秒，因为有时候分割的差一点
                markers.append({'text': row[0], 'time': float(row[1]) + 0.1, })
        except csv.Error as e:
            return HttpResponse(f'file {file}, line {reader.line_num}: {e}')

    ret = {'code': 200,
           'msg': '',
           'data': markers,
           }
    return HttpResponse(json.dumps(ret))


@login_required
def load_user_markers(request, model, pk, using=None):
    """
    载入用户标记
    """
    print(model, pk)
    try:
        video = model.objects.using(using).get(pk=pk)
    except Exception as e:
        return HttpResponse(str(e))

    markers = []
    for marker in video.markers.all():
        markers.append({'time': float(marker.time), 'text': marker.name, 'id': marker.id, })
    print(markers)

    ret = {'code': 200,
           'msg': '',
           'data': markers,
           }
    return HttpResponse(json.dumps(ret))


@login_required
def load_markers(request, model, md5, using=None):
    """
    载入标记
    """
    data_type = request.POST.get("type")
    file = MARKERS_DIR / f'{md5}.json'
    print('load_markers', file, data_type)
    try:
        with open(file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(e)
        if settings.DEBUG:
            return HttpResponse(str(e))
        else:
            return HttpResponse('读取文件错误!')
    ret = {'code': 200,
           'msg': '',
           'data': data,
           }
    return HttpResponse(json.dumps(ret))


@login_required
def save_markers(request, model, md5, using=None):
    """
    保存标记
    """
    if request.method == 'POST':
        data = request.POST.get("data")
        data_type = request.POST.get("type")
        if data:
            # name = str(model._meta)
            # if '.' in name:
            #     name = name.split('.')[-1]
            # if using:
            #     markers_dir = MARKERS_DIR / f'{name}_{using}'
            # else:
            #     markers_dir = MARKERS_DIR / name
            # if not markers_dir.exists():
            #     markers_dir.mkdir()
            file = MARKERS_DIR / f'{md5}.json'
            print('save_markers', file, data_type)
            # data = json.loads(data)
            try:
                with open(file, 'w', encoding='utf-8') as f:
                    f.write(data)
            except Exception as e:
                print(e)
                if settings.DEBUG:
                    return HttpResponse(str(e))
                else:
                    return HttpResponse('保存文件错误!')
            ret = {'code': 200,
                   'msg': '保存成功!',
                   }
            return HttpResponse(json.dumps(ret))
        else:
            return HttpResponse('没有找到要保存的标记')
