import importlib
import os
import pkgutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Union

from gdown.models import GdownRsp


class BaseDownloader(ABC):
    """Abstract base class for all downloaders."""

    @abstractmethod
    def download(
        self,
        url: Union[str, List[str]],
        output: Optional[Path],
        proxy: Optional[str] = None,
        use_cookies: bool = True,
        verify: bool = True,
        user_agent: Optional[str] = None,
    ) -> Union[Union[GdownRsp, List[GdownRsp]], None]:
        """Download method to be implemented by subclasses."""
        raise NotImplementedError


class DownloaderFactory:
    """Factory class for managing and creating downloader instances dynamically.

    This class maintains a registry of available downloader classes and supports
    dynamic importing of downloader modules.
    """

    class_registry = {}

    @classmethod
    def register_class(cls, type_names):
        """Decorator to register a downloader class with specified type names.

        Parameters
        ----------
        type_names : list[str]
            List of type names that map to the class.

        Returns
        -------
        function
            Wrapper function that registers the class.
        """

        def wrapper(class_type):
            for type_name in type_names:
                cls.class_registry[type_name] = class_type
            return class_type

        return wrapper

    @classmethod
    def call_class(cls, type_name):
        """Retrieve an instance of a registered downloader class.

        Parameters
        ----------
        type_name : str
            The name of the downloader type to instantiate.

        Returns
        -------
        object
            An instance of the registered downloader class.

        Raises
        ------
        ValueError
            If the specified type name is not registered.
        """
        if type_name in cls.class_registry:
            return cls.class_registry[type_name](type_name=type_name)
        else:
            raise ValueError(f"Type '{type_name}' không được hỗ trợ.")

    @classmethod
    def auto_import_classes(cls, package_name):
        """Dynamically imports all modules in the specified package.

        This method scans the package directory and imports all available modules,
        ensuring that downloader classes are automatically registered.

        Parameters
        ----------
        package_name : str
            The name of the package containing downloader modules.
        """
        package_dir = os.path.join(os.path.dirname(__file__), package_name)
        for _, module_name, _ in pkgutil.iter_modules([package_dir]):
            importlib.import_module(f"gdown.downloader.{package_name}.{module_name}")


DownloaderFactory.auto_import_classes("classes")
