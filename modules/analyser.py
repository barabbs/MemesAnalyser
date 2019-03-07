from . import var
from . import utility as utl
from . import process as prc
from .meme import Meme


class Analyser(prc.Process):
    """
    Class of the Analyser process
    """

    def __init__(self, *args, **kwargs):
        """
        Initialises a new Analyser object

        :param args:
        :param kwargs:
        """
        super(Analyser, self).__init__(*args, **kwargs)
        self.templates = kwargs['templates']

    def _run(self):
        """
        Method called by the run() method at process start
        Gets new memes from the memes pipe, analyses them and puts them in the database pipe

        :return:
        """
        new = None
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
        """
        Compares the given meme with all the templates and finds the best match

        :param meme: The meme to analyse
        :return:
        """
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
        """
        Primary compare of the memes. Calls primary_search for all templates

        :param meme: The meme to analyse
        :return:
        """
        results = list()
        for templ in self.templates:
            results.append([templ, templ.primary_search(meme)])
        return results

    def secondary_compare(self, meme, templates):
        """
        Secondary compare of the memes. Calls secondary_search for the given templates

        :param meme: The meme to analyse
        :param templates: The templates to compare
        :type templates: list
        :return:
        """
        results = list()
        for templ in templates:
            results.append([templ[0], templ[0].secondary_search(meme)])
        return results
