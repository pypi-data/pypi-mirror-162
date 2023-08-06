"""
This module contains HEA objects supporting items that are openable in the HEA desktop, called data objects (DataObject
below). HEA uses internet MIME types to provide additional information about the type of data in a DataObject. You can
read more about MIME types at https://www.iana.org/assignments/media-types/media-types.xhtml and
https://en.wikipedia.org/wiki/Media_type.

HEA defines the following custom MIME types that are intended only for internal use by the different parts of HEA:

application/x.folder: HEA folders (heaobject.folder.Folder)
application/x.item: HEA items (heaobject.folder.Item)
application/x.data-in-database: Data in a database (heaobject.data.DataInDatabase)
"""

from . import root
from abc import ABC, abstractmethod
from typing import Optional
from humanize import naturalsize

from .aws import S3StorageClassMixin, S3URIMixin


class DataObject(root.AbstractDesktopObject, ABC):
    """
    Interface for data objects, which are objects that are openable in the HEA desktop. The main difference between
    openable and other objects is the addition of two properties: a MIME type property, and a property containing a
    list of the MIME types that the object supports providing when it is opened.
    """

    @property
    @abstractmethod
    def mime_type(self) -> str:
        """
        The object's MIME type. Note that HEA uses '*/x.*' for all HEA-specific private
        MIME types that only need to be understood by the different parts of HEA, such as 'application/x.folder' for
        folders.
        """
        pass


class SameMimeType(ABC):
    """
    Interface to add to DataObject classes in which instances always have the same mime type.
    """
    @classmethod
    @abstractmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type of instances of the data class implementing this interface.

        :return: a mime type string.
        """
        pass


class DataFile(DataObject):
    """
    Represents files on a file system.
    """

    DEFAULT_MIME_TYPE = 'application/octet-stream'

    def __init__(self):
        """
        Creates a file object.
        """
        super().__init__()
        self.__mime_type = DataFile.DEFAULT_MIME_TYPE
        self.__mime_type_tranforms = []
        self.__size: Optional[int] = None

    @property
    def mime_type(self) -> str:
        """The mime type of the file."""
        return self.__mime_type

    @mime_type.setter
    def mime_type(self, mime_type: str) -> None:
        if mime_type is None:
            self.__mime_type = DataFile.DEFAULT_MIME_TYPE
        else:
            self.__mime_type = str(mime_type)

    @property
    def size(self) -> Optional[int]:
        """Size of the data file in bytes."""
        return self.__size

    @size.setter
    def size(self, size: Optional[int]) -> None:
        self.__size = int(size) if size is not None else None

    @property
    def human_readable_size(self) -> str:
        """Size as a human-readable string"""
        return naturalsize(self.size) if self.size is not None else None


class AWSS3FileObject(DataFile, S3StorageClassMixin, S3URIMixin):
    """
    Represents files stored in AWS S3.
    """
    pass


class DataInDatabase(DataObject, SameMimeType):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type of instances of the DataInDatabase class.

        :return: application/x.data-in-database
        """
        return 'application/x.data-in-database'

    @property
    def mime_type(self) -> str:
        """Read-only. The mime type for DataInDatabase objects, application/x.data-in-database."""
        return type(self).get_mime_type()

