from metainfo.metainfo import MetaInfo

class CStaticContextRetrieval(MetaInfo):
    def __init__(self):
        super().__init__()

    def retrieve(self, context):
        return context