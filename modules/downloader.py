from . import var
from . import utility as utl
from . import process as prc
import urllib.request, urllib.error
import psaw, praw, datetime, numpy, time
from InstagramAPI import InstagramAPI


class DownloadHandler(prc.Process):
    def __init__(self, *args, **kwargs):
        super(DownloadHandler, self).__init__(*args, **kwargs)
        self.name = "DownloadHandler"

        self.sources = kwargs['sources']

        self.start_time = None
        self.stop_time = None
        self.downloader_classes = {'reddit': RedditDownloader,
                                   'instagram': BaseDownloader}

        self.instagram_api = InstagramAPI(**var.INSTAGRAM_CREDENTIALS)
        self.start_instagram_api()

    def start_instagram_api(self):
        while not self.instagram_api.isLoggedIn:
            self.instagram_api.login()

    def _run(self):
        while True:
            self.stop_time = int((datetime.datetime.now() - var.TIME_THRESHOLD).timestamp())
            for source in self.sources[::-1]: # TODO: REMOVE THIS
                # if source[0] < 39:
                #     continue

                self.terminal.info(f"{utl.get_time()}: Starting with source {source[0]}: {source[4]} from {source[1]} (type {source[2]})")
                self._start_downloaders(source[1])
                self.start_time = source[6]
                try:
                    getattr(self, f"_get_sources_{source[1]}")(source)
                except StopIteration:
                    raise
                except Exception as e:
                    self.track_error(to_file=True, error=e,
                                     additional={'source_ID': source[0], 'value': source[3], 'name': source[4], 'site': source[1], 'type': source[2], 'start_timestamp': source[6], })
                self.terminal.info(f"{utl.get_time()}: Ended with source {source[0]}: {source[4]} from {source[1]} (type {source[2]})")
                for k in ['download', 'memes']:
                    self.wait_for_pipe(k)
                self.terminal.print("Pipes download and memes are empty")
                self._close_downloaders()
                time.sleep(3)
            self.terminal.info("All sources ended")

    def _start_downloaders(self, key):
        for i in range(var.DOWNLOADERS_NUMBER):
            self._new_subprocess(self.downloader_classes[key], f"Downloader_{i}", dict())

    def _close_downloaders(self):
        self._close_subprocess([f"Downloader_{i}" for i in range(var.DOWNLOADERS_NUMBER)])

    def _get_sources_reddit(self, source):
        api = psaw.PushshiftAPI()
        self.terminal.print(f"{self.stop_time} >>> {self.start_time}")
        submissions = api.search_submissions(before=self.stop_time, after=self.start_time, subreddit=source[3], filter=['id', 'post_hint', 'url', 'created_utc'], sort="asc")
        for item in submissions:
            try:
                if item.post_hint == "image":
                    meme = {'source_ID': source[0], 'ID': item.id, 'url': item.url, 'time': item.created_utc}
                    self.pipe_put('download', meme)
            except AttributeError:
                pass
            self.check_exit_event()

    def _get_sources_instagram(self, source):
        if source[2] == "profile":
            ID = source[3]
            while self.start_time < self.stop_time:
                max_id = ""
                while True:
                    self.instagram_api.getUserFeed(ID, maxid=max_id, minTimestamp=self.start_time, maxTimestamp=self.start_time + var.TIME_BATCH_SIZE)
                    j = self.instagram_api.LastJson
                    try:
                        for i in j["items"]:
                            if i['media_type'] == 1:
                                meme = {'source_ID': source[0], 'ID': i['code'], 'url': i['image_versions2']['candidates'][0]['url'], 'time': i['taken_at'], 'score': i['like_count']}
                                self.pipe_put('download', meme)
                    except StopIteration:
                        raise
                    except Exception as e:
                        self.track_error(to_file=True, error=e, additional=j)

                    if not j['more_available']:
                        break
                    max_id = j.get('next_max_id', '')
                self.check_exit_event()
                self.start_time = self.start_time + var.TIME_BATCH_SIZE
        elif source[2] == "hashtag":
            hashtag = source[3]
            while self.start_time < self.stop_time:
                max_id = ""
                while True:
                    self.instagram_api.getHashtagFeed(hashtag, maxid=max_id, minTimestamp=self.start_time, maxTimestamp=self.start_time + var.TIME_BATCH_SIZE)
                    j = self.instagram_api.LastJson
                    try:
                        for i in j["items"]:
                            if i['media_type'] == 1 and i['like_count'] > var.HASHTAG_SCORE_THRESHOLD:
                                meme = {'source_ID': source[0], 'ID': i['code'], 'url': i['image_versions2']['candidates'][0]['url'], 'time': i['taken_at'], 'score': i['like_count']}
                                self.pipe_put('download', meme)
                    except StopIteration:
                        raise
                    except Exception as e:
                        self.track_error(to_file=True, error=e, additional=j)

                    if not j['more_available']:
                        break
                    max_id = j.get('next_max_id', '')
                self.check_exit_event()
                self.start_time = self.start_time + var.TIME_BATCH_SIZE
        else:
            raise NotImplemented

    # def _get_sources_instagram(self, source):
    #     if source[2] == "profile":
    #         ID = source[3]
    #         while self.start_time < self.stop_time:
    #             max_id = ""
    #             while True:
    #                 self.instagram_api.getUserFeed(ID, maxid=max_id, minTimestamp=self.start_time, maxTimestamp=self.start_time + var.TIME_BATCH_SIZE)
    #                 j = self.instagram_api.LastJson
    #                 try:
    #                     for i in j["items"]:
    #                         if i['media_type'] == 1:
    #                             meme = {'source_ID': source[0], 'ID': i['code'], 'url': i['image_versions2']['candidates'][0]['url'], 'time': i['taken_at'], 'store_time': i['taken_at'],
    #                                     'score': i['like_count']}
    #                             self.pipe_put('download', meme)
    #                 except StopIteration:
    #                     raise
    #                 except Exception as e:
    #                     self.track_error(to_file=True, error=e, additional=j)
    #
    #                 if not j['more_available']:
    #                     break
    #                 max_id = j.get('next_max_id', '')
    #             self.check_exit_event()
    #             self.start_time = self.start_time + var.TIME_BATCH_SIZE
    #     elif source[2] == "hashtag":
    #         hashtag = source[3]
    #         self.start_time = -self.start_time
    #         if self.start_time == 0:
    #             self.start_time = var.INSTAGRAM_MAX_TIME
    #         max_id = ""
    #         while True:
    #             self.instagram_api.getHashtagFeed(hashtag, maxid=max_id)
    #             j = self.instagram_api.LastJson
    #             try:
    #                 for i in j["items"]:
    #                     if i['taken_at'] < self.start_time and i['media_type'] == 1 and i['like_count'] > var.HASHTAG_SCORE_THRESHOLD:
    #                         meme = {'source_ID': source[0], 'ID': i['code'], 'url': i['image_versions2']['candidates'][0]['url'], 'time': i['taken_at'], 'store_time': -i['taken_at'],
    #                                 'score': i['like_count']}
    #                         self.pipe_put('download', meme)
    #             except StopIteration:
    #                 raise
    #             except Exception as e:
    #                 self.track_error(to_file=True, error=e, additional=j)
    #
    #             if not j['more_available']:
    #                 break
    #             max_id = j.get('next_max_id', '')
    #             self.check_exit_event()
    #     else:
    #         raise NotImplemented


class BaseDownloader(prc.Process):
    def __init__(self, *args, **kwargs):
        super(BaseDownloader, self).__init__(*args, **kwargs)

    def download(self, meme):
        req = urllib.request.Request(meme['url'], data=None, headers={'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0"})
        raw_data = self.retrieve(req)
        if raw_data:
            meme['np_array'] = numpy.asarray(bytearray(raw_data.read()), dtype="uint8")
            self.pipe_put('memes', meme)

    def retrieve(self, request, retry=1):
        try:
            return urllib.request.urlopen(request, timeout=var.DOWNLOAD_TIMEOUT)
        except Exception as e:
            if retry == var.MAX_RETIRES:
                self.terminal.warning(f"Error {e} with url {request.get_full_url()}")
                # self.track_error(to_file=True, additional={'url': request.get_full_url()})
                return None
            else:
                return self.retrieve(request, retry + 1)

    def _run(self):
        new = None
        while True:
            try:
                new = self.pipe_get('download')
                self.download(new)
            except StopIteration:
                raise
            except Exception as e:
                self.track_error(to_file=True, error=e, additional=new)


class RedditDownloader(BaseDownloader):

    def __init__(self, *args, **kwargs):
        super(RedditDownloader, self).__init__(*args, **kwargs)
        self.reddit = praw.Reddit(**var.REDDIT_CREDENTIALS)

    def download(self, meme):
        sub = self.reddit.submission(id=meme['ID'])
        sub.comment_limit = 1
        score = sub.score
        if score >= var.SCORE_THRESHOLD:
            meme['score'] = score
            super(RedditDownloader, self).download(meme)
