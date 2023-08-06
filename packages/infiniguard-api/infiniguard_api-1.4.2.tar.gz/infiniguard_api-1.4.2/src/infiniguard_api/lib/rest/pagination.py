import math


class Pagination:

    def __init__(self, page_size, page, number_of_objects):
        self.number_of_objects = number_of_objects
        if page_size == 0:
            self.page_size = 1
        else:
            self.page_size = page_size
        if self.page_size > self.number_of_objects:
            self.page = 1
        else:
            self.page = min(page,
                            int(math.ceil(self.number_of_objects /
                                          float(self.page_size))))

    @property
    def pages(self):
        return max(1, int(math.ceil(self.number_of_objects /
                                    float(self.page_size))))

    @property
    def offset(self):
        return self.page_size*(self.page - 1)

    @property
    def limit(self):
        return self.page_size
