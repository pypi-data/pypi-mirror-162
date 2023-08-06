from abc import abstractmethod
from tempfile import SpooledTemporaryFile
from typing import TYPE_CHECKING, Optional, Tuple

from sqlalchemy_file.helpers import INMEMORY_FILESIZE

if TYPE_CHECKING:
    from sqlalchemy_file.file import File


class Processor:
    """
    Interface that must be implemented by file processors.
    Can be used to add additional data to the stored file or change it.
    When file processors are run the file has already been stored.

    """

    @abstractmethod
    def process(
        self, file: "File", upload_storage: Optional[str] = None
    ) -> None:  # pragma: no cover
        """
        Should be overridden in inherited class
        :param file: dict-like File object,
                Use file.original_content to access uploaded file
        :param upload_storage: pass this to file.store_content to
              attach additional files to the original file
        """
        pass


class ThumbnailGenerator(Processor):
    """
    Generate thumbnail from original content.

    The default thumbnail format and size are PNG@128x128, those can be changed
    by giving custom thumbnail_size and thumbnail_format

    ThumbnailGenerator will add

    thumbnail: Dict object added to base file witch contains:

                - file_id           - This is the ID of the uploaded thumbnail file
                - path              - This is a upload_storage/file_id path which can
                                      be used with :meth:`StorageManager.get_file` to
                                      retrieve the thumbnail file
                - width             - This is the width of the thumbnail image
                - height            - his is the height of the thumbnail image
                - url               - Public url of the uploaded file provided
                                      by libcloud method :meth:`Object.get_cdn_url`
    """

    def __init__(
        self,
        thumbnail_size: Tuple[int, int] = (128, 128),
        thumbnail_format: str = "PNG",
    ) -> None:
        super().__init__()
        self.thumbnail_size = thumbnail_size
        self.thumbnail_format = thumbnail_format

    def process(self, file: "File", upload_storage: Optional[str] = None) -> None:
        from PIL import Image

        content = file.original_content
        img = Image.open(content)
        thumbnail = img.copy()
        thumbnail.thumbnail(self.thumbnail_size)
        output = SpooledTemporaryFile(INMEMORY_FILESIZE)
        thumbnail.save(output, self.thumbnail_format)
        output.seek(0)
        stored_file = file.store_content(
            output,
            upload_storage,
            metadata={
                "filename": file["filename"],
                "content_type": file["content_type"],
                "width": thumbnail.width,
                "height": thumbnail.height,
            },
        )
        file.update(
            {
                "thumbnail": {
                    "file_id": stored_file.name,
                    "width": thumbnail.width,
                    "height": thumbnail.height,
                    "path": "%s/%s" % (upload_storage, stored_file.name),
                    "url": stored_file.get_cdn_url(),
                }
            }
        )
