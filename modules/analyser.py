from . import var
from . import utility as utl
from . import process as prc
from .meme import Meme


class Analyser(prc.Process):
    def __init__(self, *args, **kwargs):
        super(Analyser, self).__init__(*args, **kwargs)
        self.templates = kwargs['templates']

    def _run(self):
        new=None
        while True:
            try:
                new = self.pipe_get('memes')
                meme = Meme(**new)
                # self.terminal.print(f"Got a new Meme from source {meme.source_ID}")
                if meme.image is not None:
                    self.compare(meme)
            except StopIteration:
                raise
            except Exception as e:
                self.track_error(to_file=True, error=e, additional=new)

    def compare(self, meme):
        raw_result = self.primary_compare(meme)
        raw_result.sort(key=lambda x: x[1][0], reverse=True)
        results = self.secondary_compare(meme, raw_result[:var.FIRST_SELECTION_NUMBER])
        for i in range(var.FIRST_SELECTION_NUMBER):
            results[i].append(utl.result_calc(results[i][1]))
        results.sort(key=lambda x: x[2], reverse=True)
        best = results[0]
        meme.template_ID = best[0].ID
        meme.part_match = best[1]
        meme.match = best[2]
        self.pipe_put('database', meme)

    def primary_compare(self, meme):
        results = list()
        for templ in self.templates:
            results.append([templ, templ.primary_search(meme)])
        return results

    def secondary_compare(self, meme, templates):
        results = list()
        for templ in templates:
            results.append([templ[0], templ[0].secondary_search(meme)])
        return results
