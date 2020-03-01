
class Data:

    post = {}
    row_count = 1
    bins = []

    @staticmethod
    def add_row(post):
        Data.post = post
        Data.row_count += 1

    @staticmethod
    def rm_row(post):
        if Data.row_count > 1:
            Data.row_count -= 1
            del [post["word{0}".format(Data.row_count)]]
            del [post["sub{0}".format(Data.row_count)]]
        Data.post = post

    @staticmethod
    def clear(post):
        Data.bins = []
        Data.row_count = 1
        Data.post = {}

    @staticmethod
    def update(post):
        Data.bins = []
        Data.post = post

    @staticmethod
    def add_bins(bins):
        """
        bins as [ [start, end], ... ]
        """
        Data.bins = bins.reverse() + Data.bins
