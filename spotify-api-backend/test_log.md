# MOCKED UNIT TESTING 
## Test case result for get_user_top_track function
### First test
```===================== test session starts =====================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- /home/minhcranel/Documents/projects/MusicVault/spotify-api-backend/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/minhcranel/Documents/projects/MusicVault/spotify-api-backend
collected 5 items                                             

tests/services/test_spotify_service.py::test_get_user_top_track_rejects_limit_above_50 PASSED [ 20%]
tests/services/test_spotify_service.py::test_get_user_top_track_rejects_limit_below_1 PASSED [ 40%]
tests/services/test_spotify_service.py::test_get_user_top_track_rejects_invalid_time_range PASSED [ 60%]
tests/services/test_spotify_service.py::test_get_user_top_track_rejects_negative_offset PASSED [ 80%]
tests/services/test_spotify_service.py::test_get_user_top_track_success FAILED [100%]

========================== FAILURES ===========================
_______________ test_get_user_top_track_success _______________

args = (), keywargs = {}

    @wraps(func)
    def patched(*args, **keywargs):
>       with self.decoration_helper(patched,
                                    args,
                                    keywargs) as (newargs, newkeywargs):

/usr/lib/python3.12/unittest/mock.py:1387: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
/usr/lib/python3.12/contextlib.py:137: in __enter__
    return next(self.gen)
           ^^^^^^^^^^^^^^
/usr/lib/python3.12/unittest/mock.py:1369: in decoration_helper
    arg = exit_stack.enter_context(patching)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/usr/lib/python3.12/contextlib.py:526: in enter_context
    result = _enter(cm)
             ^^^^^^^^^^
/usr/lib/python3.12/unittest/mock.py:1442: in __enter__
    self.target = self.getter()
                  ^^^^^^^^^^^^^
/usr/lib/python3.12/pkgutil.py:513: in resolve_name
    mod = importlib.import_module(modname)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

name = 'backend', package = None

    def import_module(name, package=None):
        """Import a module.
    
        The 'package' argument is required when performing a relative import. It
        specifies the package to use as the anchor point from which to resolve the
        relative import to an absolute import.
    
        """
        level = 0
        if name.startswith('.'):
            if not package:
                raise TypeError("the 'package' argument is required to perform a "
                                f"relative import for {name!r}")
            for character in name:
                if character != '.':
                    break
                level += 1
>       return _bootstrap._gcd_import(name[level:], package, level)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       ModuleNotFoundError: No module named 'backend'

/usr/lib/python3.12/importlib/__init__.py:90: ModuleNotFoundError
=================== short test summary info ===================
FAILED tests/services/test_spotify_service.py::test_get_user_top_track_success - ModuleNotFoundError: No module named 'backend'
================= 1 failed, 4 passed in 0.24s =================
```
#Second Test
```(.venv) minhcranel@minhcranel-Latitude-3301:~/Documents/projects/MusicVault/spotify-api-backend$ pytest tests/services/test_spotify_service.py -v
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- /home/minhcranel/Documents/projects/MusicVault/spotify-api-backend/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/minhcranel/Documents/projects/MusicVault/spotify-api-backend
collected 5 items                                                              

tests/services/test_spotify_service.py::test_get_user_top_track_rejects_limit_above_50 PASSED [ 20%]
tests/services/test_spotify_service.py::test_get_user_top_track_rejects_limit_below_1 PASSED [ 40%]
tests/services/test_spotify_service.py::test_get_user_top_track_rejects_invalid_time_range PASSED [ 60%]
tests/services/test_spotify_service.py::test_get_user_top_track_rejects_negative_offset PASSED [ 80%]
tests/services/test_spotify_service.py::test_get_user_top_track_success PASSED [100%]

============================== 5 passed in 0.21s ===============================
(.venv) minhcranel@minhcranel-Latitude-3301:~/Documents/projects/MusicVault/spot
```
**Result**: SpotifyService can be instatiated with access token. The function get_user\_top\_track() has rejected invalid limits and construct Spotify request correctly. It also correctly handles a successful mocked spotify response.  

# Test case for get_track function 
### First test 
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-9.1.1, pluggy-1.6.0 -- /home/minhcranel/Documents/projects/MusicVault/spotify-api-backend/.venv/bin/python3
cachedir: .pytest_cache
rootdir: /home/minhcranel/Documents/projects/MusicVault/spotify-api-backend
collected 8 items                                                              

tests/services/test_spotify_service.py::test_get_user_top_track_rejects_limit_above_50 PASSED [ 12%]
tests/services/test_spotify_service.py::test_get_user_top_track_rejects_limit_below_1 PASSED [ 25%]
tests/services/test_spotify_service.py::test_get_user_top_track_rejects_invalid_time_range PASSED [ 37%]
tests/services/test_spotify_service.py::test_get_user_top_track_rejects_negative_offset PASSED [ 50%]
tests/services/test_spotify_service.py::test_get_user_top_track_success PASSED [ 62%]
tests/services/test_spotify_service.py::test_search_track_success PASSED [ 75%]
tests/services/test_spotify_service.py::test_search_track_rejects_empty_query PASSED [ 87%]
tests/services/test_spotify_service.py::test_search_track_rejects_blank_query PASSED [100%]

============================== 8 passed in 0.15s ===============================
```
**Result**: search track successfully getting track with valid input query. It's also successfully reject invalid input. 