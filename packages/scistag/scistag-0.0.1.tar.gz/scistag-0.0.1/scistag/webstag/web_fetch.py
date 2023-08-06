from threading import RLock
from typing import Optional

import requests
import time
import os
import base64
import tempfile
import shutil


def file_age_in_seconds(pathname: str) -> float:
    """
    Returns the age of a file in seconds
    :param pathname: The file's path
    :return The age in seconds:
    """
    stat = os.stat(pathname)
    return time.time() - stat.st_mtime


class WebCache:
    lock = RLock()
    "Access lock"
    cache_dir = tempfile.gettempdir() + "/scistag/"
    "The cache directory"
    app_name = "scistag"
    "The application's name"
    max_general_age = 60 * 60 * 7
    "The maximum age of any file loaded via the cache"
    max_cache_size = 200000000
    "The maximum file size in the cache"
    total_size = 0
    "Total cache size"
    files_stored = 0
    "Files stored in this session"
    cleaned = False
    "Defines if the cache was cleaned yet"

    @classmethod
    def set_app_name(cls, name: str):
        """
        Modifies the application's name (and thus the cache path)
        :param name: The application's name
        """
        with cls.lock:
            cls.app_name = name
            cls.cache_dir = tempfile.tempdir + f"/scistag/{name}/"
            cls.cleanup()

    @classmethod
    def fetch(cls, url: str, max_age: float) -> Optional[bytes]:
        """
        Tries to fetch a file from the cache
        :param url: The original url
        :param max_age: The maximum age in seconds
        :return: On success the file's content
        """
        encoded = base64.urlsafe_b64encode(url.encode('utf-8'))
        encoded_name = encoded.rstrip(b'=').decode('ascii')
        full_name = cls.cache_dir + encoded_name
        try:
            with cls.lock:
                if os.path.exists(full_name):
                    if file_age_in_seconds(full_name) <= max_age:
                        return open(full_name, "rb").read()
                    else:
                        cls.total_size -= os.stat(full_name).st_size
                        os.remove(full_name)
                        return None
        except FileNotFoundError:
            return None

    @classmethod
    def find(cls, url: str) -> Optional[str]:
        """
        Searches for a file in the cache and returns it's disk path
        :param url: The url
        :return: The file name if the file could be found
        """
        encoded_name = base64.urlsafe_b64encode(url).rstrip(b'=').decode('ascii')
        full_name = cls.cache_dir + encoded_name
        if os.path.exists(full_name):
            return full_name
        return None

    @classmethod
    def store(cls, url: str, data: bytes):
        """
        Caches the new web element on disk.
        :param url: The url
        :param data: The data
        """
        if not cls.cleaned:
            WebCache.cleanup()
        with cls.lock:
            cls.files_stored += 1
            if cls.files_stored == 1:
                os.makedirs(cls.cache_dir)
            if cls.total_size >= cls.max_cache_size:
                cls.flush()
            encoded_name = base64.urlsafe_b64encode(url.encode('utf-8')).rstrip(b'=').decode('ascii')
            full_name = cls.cache_dir + encoded_name
            with open(full_name, "wb") as file:
                file.write(data)
            cls.total_size += len(data)

    @classmethod
    def cleanup(cls):
        """
        Cleans up the cache and removes old files
        """
        with cls.lock:
            cls.cleaned = True
            try:
                files = os.listdir(cls.cache_dir)
            except FileNotFoundError:
                files = []
            cur_time = time.time()
            cls.total_size = 0
            for cur_file in files:
                full_name = cls.cache_dir + cur_file
                stat = os.stat(full_name)
                if cur_time - stat.st_mtime > cls.max_general_age:
                    os.remove(full_name)
                else:
                    cls.total_size += stat.st_size
            if cls.total_size >= cls.max_cache_size:  # still very unelegant way, should delete files sorted by age
                cls.flush()

    @classmethod
    def flush(cls):
        """
        Clean the cache completely
        """
        with cls.lock:
            cls.total_size = 0
            try:
                shutil.rmtree(cls.cache_dir)
            except FileNotFoundError:
                pass
            os.makedirs(cls.cache_dir, exist_ok=True)


def web_fetch(url: str, timeout_s: float = 10.0, max_cache_age=0.0,
              filename: Optional[str] = None) -> Optional[bytes]:
    """
    Fetches a file from the web via HTTP GET
    :param url: The URL
    :param timeout_s: The timeout in seconds
    :param max_cache_age: The maximum cache age in seconds. Note that the internal cache is everything else than
    optimized so this should only be used to load e.g. the base data for an app once.
    :param filename: If specified the data will be stored in this file
    :return: The file's content if available and not timed out, otherwise None
    """
    if max_cache_age != 0:
        data = WebCache.fetch(url, max_age=max_cache_age)
        if data is not None:
            if filename is not None:
                with open(filename, "wb") as file:
                    file.write(data)
            return data
    try:
        response = requests.get(url=url, timeout=timeout_s)
    except requests.exceptions.RequestException:
        return None
    if max_cache_age != 0:
        WebCache.store(url, response.content)
    if filename is not None:
        with open(filename, "wb") as file:
            file.write(response.content)
    return response.content
