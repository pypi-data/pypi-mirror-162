
from manhattan.assets.transforms.base import BaseTransform

__all__ = ['Output']


class Output(BaseTransform):
    """
    Set the output format of an image. The list of support formats will vary
    depending on service, however as a minimum the following formats should be
    supported by all services:

    - jpg
    - gif
    - png
    - webp
    """

    _id = 'image.output'

    def __init__(self, format, quality=None, lossless=None):
        settings = {'format': format}
        if quality is not None:
            settings['quality'] = quality

        if lossless is not None:
            settings['lossless'] = lossless

        super().__init__(settings)
