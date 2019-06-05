from datetime import datetime


def filter_response(response):
    music = response.meta['music']
    re_json = response.text[3:-2]
    music['type'] = 'kugou_music'
    music['music_data'] = re_json
    music['time'] = datetime.now().strftime("%Y-%m-%d")
    return music