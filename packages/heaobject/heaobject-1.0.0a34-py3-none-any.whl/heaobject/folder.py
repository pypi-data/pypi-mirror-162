from .data import DataObject, SameMimeType
from .aws import S3URIMixin, S3StorageClassMixin
from typing import Optional
import copy
from humanize import naturalsize


class Folder(DataObject, SameMimeType):
    """
    Represents a directory in the HEA desktop.
    """
    def __init__(self):
        super().__init__()

    @classmethod
    def get_mime_type(cls) -> str:
        """
        Returns the mime type of instances of the Folder class.

        :return: application/x.folder
        """
        return 'application/x.folder'

    @property
    def mime_type(self) -> str:
        """
        Read-only. Always returns 'application/x.folder'.
        """
        return type(self).get_mime_type()


class AWSS3Folder(Folder, S3StorageClassMixin, S3URIMixin):
    """
    Represents folders stored in AWS S3.
    """
    pass


class Item(DataObject):
    """
    Represents an item in a folder. Items contain the actual object being pointed to as a nested
    """
    def __init__(self):
        super().__init__()
        self.__actual_object_type_name: Optional[str] = None
        self.__actual_object_id: Optional[str] = None
        self.__actual_object_uri: Optional[str] = None
        self.__folder_id: Optional[str] = None
        self.__volume_id: Optional[str] = None
        self.__size: Optional[int] = None

    @property
    def mime_type(self) -> str:
        """
        Read-only. Always returns 'application/x.item'.
        """
        return 'application/x.item'

    @property
    def actual_object_type_name(self) -> Optional[str]:
        """
        The name of the type of the actual HEAObject.
        """
        return self.__actual_object_type_name

    @actual_object_type_name.setter
    def actual_object_type_name(self, actual_object_type_name: Optional[str]) -> None:
        self.__actual_object_type_name = str(actual_object_type_name) if actual_object_type_name is not None else None

    @property
    def actual_object_id(self) -> Optional[str]:
        """
        The id of the actual HEAObject.
        """
        return self.__actual_object_id

    @actual_object_id.setter
    def actual_object_id(self, actual_object_id: Optional[str]) -> None:
        self.__actual_object_id = str(actual_object_id) if actual_object_id is not None else None

    @property
    def actual_object_uri(self) -> Optional[str]:
        """
        The actual HEAObject's URI.
        """
        return self.__actual_object_uri

    @actual_object_uri.setter
    def actual_object_uri(self, actual_object_uri: Optional[str]) -> None:
        self.__actual_object_uri = str(actual_object_uri) if actual_object_uri is not None else None

    @property
    def folder_id(self) -> Optional[str]:
        """
        The id of this item's folder.
        """
        return self.__folder_id

    @folder_id.setter
    def folder_id(self, folder_id: Optional[str]) -> None:
        self.__folder_id = str(folder_id) if folder_id is not None else None

    @property
    def volume_id(self) -> Optional[str]:
        """
        The id of this item's volume.
        """
        return self.__volume_id

    @volume_id.setter
    def volume_id(self, volume_id: Optional[str]) -> None:
        self.__volume_id = str(volume_id) if volume_id is not None else None

    @property
    def size(self) -> Optional[int]:
        """Size of the item in bytes"""
        return self.__size

    @size.setter
    def size(self, size: Optional[int]) -> None:
        self.__size = int(size) if size is not None else None

    @property
    def human_readable_size(self) -> str:
        return naturalsize(self.size) if self.size else None


class AWSS3Item(Item, S3StorageClassMixin, S3URIMixin):
    """
    Represents items stored in AWS S3.
    """
    pass
