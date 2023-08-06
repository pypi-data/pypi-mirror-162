from strictyaml import Seq, Map, Str, Url, Int, Bool, Datetime, load, as_document
import feedparser
from pathlib import Path
import subprocess as sp

feed_schema = Seq(Map({
    'name': Str(),
    'url': Str(),
    'extractor': Str(),
}))

clip_schema = Seq(Map({
    'id': Str(),
    'idx': Int(),
    'title': Str(),
    'link': Url(),
    'feed': Str(),
    'date': Datetime(),
}))

hist_schema = Seq(Map({'title': Str(), 'id': Str()}))

def extract_url(res, name: str):
    if name == 'youtube':
        return res.link
    elif name == 'voa':
        return res.links[0].href
    return None

def build_feed_list(feed_file: str):
    with open(feed_file, 'r') as f:
        feeds = load(f.read(), schema=feed_schema).data
    print('\n'.join([f['name'] for f in feeds]))

def build_clip_list(feed_names: str, feed_file: str,
                    clip_file: str, hist_file: str):
    if isinstance(feed_names, str):
        names = [feed_names]
    elif isinstance(feed_names, tuple):
        names = list(feed_names)

    with open(feed_file, 'r') as f:
        feeds = load(f.read(), schema=feed_schema).data

    parsed = []
    for feed in feeds:
        if not (feed['name'] in names):
            continue
        fi = feedparser.parse(feed['url'])
        fi.update(extractor=feed['extractor'])
        parsed.append(fi)

    history = []
    if Path(hist_file).is_file():
        with open(hist_file, 'r') as f:
            history = load(f.read(), schema=hist_schema).data
    downloaded = [item['id'] for item in history]

    clips = []
    idx = 1
    for item in parsed:
        for ent in item.entries:
            clip = {'id': ent.id,
                    'idx': idx,
                    'title': ent.title,
                    'link': extract_url(ent, item.extractor),
                    'feed': item.feed.title,
                    'date': ent.published }
            idx = idx + 1
            clips.append(clip)

    doc = as_document(clips, schema=clip_schema)
    with open(clip_file, 'w') as f:
        f.write(doc.as_yaml())

    clip_list = []
    for c in clips:
        dled = '*' if c['id'] in downloaded else ''
        clip = f'{c["idx"]}{dled}: {c["title"]}, {c["date"]}, {c["feed"]}'
        clip_list.append(clip)

    print('CLIPS LIST:\n')
    print('\n'.join(clip_list))

def download_clips(idx: str, clip_file: str, hist_file: str):
    if isinstance(idx, int):
        idc = [idx]
    elif isinstance(idx, tuple):
        idc = list(idx)
    with open(clip_file, 'r') as f:
        clips = load(f.read(), schema=clip_schema).data

    pendings = [clip for clip in clips if clip['idx'] in idc]

    history = []
    if Path(hist_file).is_file():
        with open(hist_file, 'r') as f:
            history = load(f.read(), schema=hist_schema).data
    downloaded = [item['id'] for item in history]

    for c in pendings:
        url = c["link"]
        if url.endswith('mp3'):
            sp.check_call(['wget', url])
        else:
            sp.check_call(['youtube-dl', '--format', '251', '--extract-audio',
                           '--audio-format', 'mp3', url])
        if not (c['id'] in downloaded):
            history.append({'title': c['title'], 'id': c['id']})
            doc = as_document(history, schema=hist_schema)
            with open(hist_file, 'w') as f:
                f.write(doc.as_yaml())
            print(f'Clip #{c["idx"]} downloaded!\n')

