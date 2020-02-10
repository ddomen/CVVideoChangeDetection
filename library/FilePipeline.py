import os

from library.Pipeline import Pipeline

class FilePipeline(Pipeline):
    def __init__(self, path, context={}):
        Pipeline.__init__(self)
        self.__path = path
        self.__context = context
        self.__exception = None
        self.__lastEdit = 0
        self.__lastContent = None

    def __error(self, frame): return frame.blankCopy().text('Error in {}'.format(self.__path), (0,15), fontSize=0.7)

    def __changeDetection(self):
        lastEdit = os.path.getmtime(self.__path)
        if self.__lastEdit != lastEdit or self.__lastContent is None:
            self.__lastEdit = lastEdit
            with open(self.__path, 'r') as content_file:
                try:
                    self.__lastContent = content_file.read()
                    exec(self.__lastContent, self.__context)
                    self.functions = self.__context.get('pipe', [])
                    self.__exception = None
                except Exception as exc:
                    self.__exception = exc
                    self.functions = [ lambda f: self.__error(f) ]

    def apply(self, image, *args, **kwargs):
        self.__changeDetection()
        return Pipeline.apply(self, image, *args, **kwargs)
