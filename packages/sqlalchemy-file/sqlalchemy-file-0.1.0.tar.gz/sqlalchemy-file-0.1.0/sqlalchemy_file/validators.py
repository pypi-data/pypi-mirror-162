from abc import abstractmethod
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

from sqlalchemy_file.exceptions import (
    AspectRatioValidationError,
    ContentTypeValidationError,
    DimensionValidationError,
    InvalidImageError,
    SizeValidationError,
)
from sqlalchemy_file.helpers import convert_size

if TYPE_CHECKING:
    from sqlalchemy_file.file import File


class Validator:
    """
    Interface that must be implemented by file validators.
    File validators get executed before a file is stored on the database
    using one of the supported fields. Can be used to add additional data
    to file object or change it.

    """

    @abstractmethod
    def process(self, file: "File", attr_key: str) -> None:  # pragma: no cover
        """
         Should be overridden in inherited class
        :param file: dict-like File object,
                Use file.original_content to access uploaded file
        :param attr_key: current SQLAlchemy column key.
                Could be useful when raised ValidationError
        """
        pass


class SizeValidator(Validator):
    """Validate file maximum size"""

    def __init__(self, max_size: Union[int, str] = 0) -> None:
        super().__init__()
        self.max_size = convert_size(max_size)

    def process(self, file: "File", attr_key: str) -> None:
        if file.size > self.max_size:
            raise SizeValidationError(
                attr_key,
                "The file is too large (%s). Allowed maximum size is %s."
                % (file.size, self.max_size),
            )


class ContentTypeValidator(Validator):
    """Validate file content types"""

    def __init__(self, allowed_content_types: Optional[List[str]] = None) -> None:
        super().__init__()
        self.allowed_content_types = allowed_content_types

    def process(self, file: "File", attr_key: str) -> None:
        if (
            self.allowed_content_types is not None
            and file.content_type not in self.allowed_content_types
        ):
            raise ContentTypeValidationError(
                attr_key,
                "File content_type %s is not allowed. Allowed content_types are: %s"
                % (file.content_type, self.allowed_content_types),
            )


class ImageValidator(ContentTypeValidator):
    """
     Default Validator for ImageField
    :param min_wh: Minimum allowed dimension (w, h).
    :param max_wh: Maximum allowed dimension (w, h).
    :param allowed_content_types: An iterable whose items
            are allowed content types. Default use image/*
    :param min_aspect_ratio: Minimum allowed image aspect ratio.
    :param max_aspect_ratio: Maximum allowed image aspect ratio.

    ex: ImageField(
        image_validator=ImageValidator(
            min_wh=(200, 200),
            max_wh=(400, 400),
            min_aspect_ratio=12 / 15,
            max_aspect_ratio=1,
        )
    )

    Will add `width` and `height` properties to the file object
    """

    def __init__(
        self,
        min_wh: Optional[Tuple[int, int]] = None,
        max_wh: Optional[Tuple[int, int]] = None,
        min_aspect_ratio: Optional[float] = None,
        max_aspect_ratio: Optional[float] = None,
        allowed_content_types: Optional[List[str]] = None,
    ):
        from PIL import Image

        Image.init()
        super().__init__(
            allowed_content_types
            if allowed_content_types is not None
            else [type for type in Image.MIME.values()]
        )
        self.min_width, self.min_height = min_wh if min_wh else (None, None)
        self.max_width, self.max_height = max_wh if max_wh else (None, None)
        self.min_aspect_ratio = min_aspect_ratio
        self.max_aspect_ratio = max_aspect_ratio
        self.image = Image

    def process(self, file: "File", attr_key: str) -> None:
        super().process(file, attr_key)
        import PIL

        try:
            image = self.image.open(file.original_content)
        except (PIL.UnidentifiedImageError, OSError):
            raise InvalidImageError(attr_key, "Provide valid image file")
        width, height = image.width, image.height
        if self.min_width and width < self.min_width:
            raise DimensionValidationError(
                attr_key,
                f"Minimum allowed width is: {self.min_width}, but {width} is given.",
            )
        if self.min_height and height < self.min_height:
            raise DimensionValidationError(
                attr_key,
                f"Minimum allowed height is: {self.min_height}, but {height} is given.",
            )

        if self.max_width and self.max_width < width:
            raise DimensionValidationError(
                attr_key,
                f"Maximum allowed width is: {self.max_width}, but {width} is given.",
            )

        if self.max_height and self.max_height < height:
            raise DimensionValidationError(
                attr_key,
                f"Maximum allowed height is: {self.max_height}, but {height} is given.",
            )
        aspect_ratio = width / height
        if (self.min_aspect_ratio and self.min_aspect_ratio > aspect_ratio) or (
            self.max_aspect_ratio and self.max_aspect_ratio < aspect_ratio
        ):
            raise AspectRatioValidationError(
                attr_key,
                f"Invalid aspect ratio {width} / {height} = {aspect_ratio},"
                "accepted_range: "
                f"{self.min_aspect_ratio} - {self.max_aspect_ratio}",
            )
        file.update({"width": width, "height": height})
        file.original_content.seek(0)
