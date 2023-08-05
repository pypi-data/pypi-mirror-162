"""
base class to handle cacheable object info

:authors: Daniel Abercrombie <dabercro@mit.edu>
"""

import os
import json
import time
import threading

from functools import wraps

def cached_json(attribute, timeout=None):
    """
    A decorator for caching dictionaries in local files.

    :param str attribute: The key of the :py:class:`WorkflowInfo` cache to
                          set using the decorated function.
    :param int timeout: The amount of time before refreshing the JSON file, in seconds.
    :returns: Function decorator
    :rtype: func
    """

    def cache_decorator(func):
        """
        The actual decorator (since decorator takes an argument)

        :param func func: A function to modify
        :returns: Decorated function
        :rtype: func
        """

        @wraps(func)
        def function_wrapper(self, *args, **kwargs):
            """
            Executes the :py:class:`WorkflowInfo` function

            :returns: Output of the originally decorated function
            :rtype: dict
            """
            tmout = timeout
            print( attribute, self.cache_dir)
            if not os.path.exists(self.cache_dir):
                os.mkdir(self.cache_dir)
                print('created')
            #self.cachelock.acquire()
            #if attribute not in self.cachelocks:
            #    self.cachelocks[attribute] = threading.Lock()

            #self.cachelocks[attribute].acquire()
            #self.cachelock.release()

            check_var = self.cache.get(attribute)

            if check_var is None:
                file_name = self.cache_filename(attribute)
                print( attribute , file_name )
                if os.path.exists(file_name) and \
                        (tmout is None or time.time() - tmout < os.stat(file_name).st_mtime):
                    try:
                        with open(file_name, 'r') as cache_file:
                            check_var = json.load(cache_file)
                    except ValueError:
                        print('JSON file no good. Deleting %s. Try again later.' % file_name)
                        os.remove(file_name)

                # If still None, call the wrapped function
                if check_var is None:
                    print( 'cached file not found' )
                    check_var = func(self, *args, **kwargs)
                    with open(file_name, 'w') as cache_file:
                        json.dump(check_var, cache_file)

                self.cache[attribute] = check_var

            #self.cachelocks[attribute].release()

            return check_var or {}

        return function_wrapper

    return cache_decorator


class CacheableBase(object):
    """
    Implements shared operations on the cache
    """

    def __init__(self):
        # Stores things using the cached_json decorator
        self.cache = {}
        self.cache_dir = os.path.join(os.environ.get('TMPDIR', '/tmp'), 'workflowinfo')
        self.bak_dir = os.path.join(self.cache_dir, 'bak')
        #self.cachelock = threading.Lock()
        #self.cachelocks = {}

    def __str__(self):
        pass

    def cache_filename(self, attribute):
        """
        Return the name of the file for caching

        :param str attribute: The information to store in the file
        :returns: The full file name to store the cache
        :rtype: str
        """
        return os.path.join(self.cache_dir, '%s_%s.cache.json' % (self, attribute))

    def reset(self):
        """
        Reset the cache for this object and clear out the files.
        """
        print('Reseting %s' % self)

        if not os.path.exists(self.bak_dir):
            os.mkdir(self.bak_dir)

        for attribute in self.cache:
            cache_file = self.cache_filename(attribute)
            if os.path.exists(cache_file):
                os.rename(cache_file, cache_file.replace(self.cache_dir, self.bak_dir))

        self.cache.clear()

