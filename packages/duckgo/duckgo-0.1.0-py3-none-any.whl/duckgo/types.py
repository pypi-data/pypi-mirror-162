class WebResult(dict):
    """A read-only dict wrapper for web search result
    """

    def __init__(self, *args, **kw):
        super(WebResult, self).__init__(*args, **kw)

    def __setitem__(self, key, value):
        raise TypeError('WebResult should be read-only')

    @property
    def title(self):
        return self['t']

    @property
    def url(self):
        return self['c']

    @property
    def snippet(self):
        return self['a']


class ImageResult(dict):
    """A read-only dict wrapper for image search result
    """

    def __init__(self, *args, **kw):
        super(ImageResult, self).__init__(*args, **kw)

    def __setitem__(self, key, value):
        raise TypeError('ImageResult should be read-only')

    @property
    def title(self) -> str:
        return self['title']

    @property
    def image_url(self) -> str:
        return self['image']

    @property
    def thumbnail_url(self) -> str:
        return self['thumbnail']

    @property
    def source_url(self) -> str:
        return self['url']

    @property
    def width(self) -> int:
        return self['width']

    @property
    def height(self) -> int:
        return self['height']


class VideoResult(dict):
    """A read-only dict wrapper for video search result
    """

    def __init__(self, *args, **kw):
        super(VideoResult, self).__init__(*args, **kw)

    def __setitem__(self, key, value):
        raise TypeError('VideoResult should be read-only')

    @property
    def title(self) -> str:
        return self['title']

    @property
    def description(self) -> str:
        return self['description']

    @property
    def url(self) -> str:
        return self['content']

