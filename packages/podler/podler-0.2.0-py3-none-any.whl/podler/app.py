import fire
import pkg_resources
from podler.downloader import build_feed_list, build_clip_list, download_clips

FEEDS = 'feeds.yml'
CLIP = 'clips.yml'
HIST = 'history.yml'

class Podler:
    def list_feeds(self, feed_file: str = FEEDS):
        build_feed_list(feed_file)

    def lsf(self, feed_file: str = FEEDS):
        '''List name of all feeds in the feeds file'''
        self.list_feeds(feed_file)

    def list_clips(self, feed_names: str, feed_file: str = FEEDS,
                   clip_file: str = CLIP, hist_file: str = HIST):
        build_clip_list(feed_names, feed_file, clip_file, hist_file)

    def lsc(self, feed_names: str, feed_file: str = FEEDS,
            clip_file: str = CLIP, hist_file: str = HIST):
        '''Build new clip list based on a feed'''
        self.list_clips(feed_names, feed_file, clip_file, hist_file)

    def download_selected_clips(self, idx: str, clip_file: str = CLIP, hist_file: str = HIST):
        download_clips(idx, clip_file, hist_file)

    def dl(self, idx: str, clip_file: str = CLIP, hist_file: str = HIST):
        self.download_selected_clips(idx, clip_file, hist_file)

    def version(self):
        print(pkg_resources.require("podler")[0].version)

    def ver(self):
        '''Print app version'''
        self.version()

def main():
    fire.Fire(Podler)

if __name__ == '__main__':
    main()
