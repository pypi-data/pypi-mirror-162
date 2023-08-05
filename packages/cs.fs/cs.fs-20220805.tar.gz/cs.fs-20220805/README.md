Assorted filesystem related utility functions,
some of which have been bloating cs.fileutils for too long.

*Latest release 20220805*:
Doc update.

## Function `atomic_directory(*da, **dkw)`

Decorator for a function which fills in a directory
which calls the function against a temporary directory
then renames the temporary to the target name on completion.

Parameters:
* `infill_func`: the function to fill in the target directory
* `make_placeholder`: optional flag, default `False`:
  if true an empty directory will be make at the target name
  and after completion it will be removed and the completed
  directory renamed to the target name

## Function `fnmatchdir(dirpath, fnglob)`

Return a list of the names in `dirpath` matching the glob `fnglob`.

## Class `FSPathBasedSingleton(cs.obj.SingletonMixin, HasFSPath)`

The basis for a `SingletonMixin` based on `realpath(self.fspath)`.

## Class `HasFSPath`

An object with a `.fspath` attribute representing a filesystem location.

*Method `HasFSPath.fnmatch(self, fnglob)`*:
Return a list of the names in `self.fspath` matching the glob `fnglob`.

*Method `HasFSPath.pathto(self, subpath)`*:
The full path to `subpath`, a relative path below `self.fspath`.

*Property `HasFSPath.shortpath`*:
The short version of `self.fspath`.

## Function `is_clean_subpath(subpath: str)`

Test that `subpath` is clean:
- not empty or '.' or '..'
- not an absolute path
- normalised
- does not walk up out of its parent directory

Examples:

    >>> is_clean_subpath('')
    False
    >>> is_clean_subpath('.')

## Function `longpath(path, environ=None, prefixes=None)`

Return `path` with prefixes and environment variables substituted.
The converse of `shortpath()`.

## Function `needdir(dirpath, mode=511, *, use_makedirs=False)`

Create the directory `dirpath` if missing.

Parameters:
* `dirpath`: the required directory path
* `mode`: the permissions mode, default `0o777`
* `use_makedirs`: optional creation mode, default `False`;
  if true, use `os.makedirs`, otherwise `os.mkdir`

## Function `rpaths(dirpath='.', *, only_suffixes=None, skip_suffixes=None, sort_paths=False)`

Yield relative file paths from a directory.

Parameters:
* `dirpath`: optional top directory, default `'.'`
* `only_suffixes`: optional iterable of suffixes of interest;
  if provided only files ending in these suffixes will be yielded
* `skip_suffixes`: optional iterable if suffixes to ignore;
  if provided files ending in these suffixes will not be yielded
* `sort_paths`: optional flag specifying that filenames should be sorted,
  default `False`

## Function `shortpath(path, environ=None, prefixes=None)`

Return `path` with the first matching leading prefix replaced.

Parameters:
* `environ`: environment mapping if not os.environ
* `prefixes`: iterable of `(prefix,subst)` to consider for replacement;
  each `prefix` is subject to environment variable
  substitution before consideration
  The default considers "$HOME/" for replacement by "~/".

# Release Log



*Release 20220805*:
Doc update.

*Release 20220530*:
FSPathBasedSingleton._resolve_fspath: new `envvar` and `default_attr` parameters.

*Release 20220429*:
* New HasFSPath and FSPathBasedSingleton.
* Add longpath and shortpath from cs.fileutils.
* New is_clean_subpath(subpath).
* New needdir(path).
* New fnmatchdir(dirpath,fnglob) pulled out from HasFSPath.fnmatch(fnglob).

*Release 20220327*:
New module cs.fs to contain more filesystem focussed functions than cs.fileutils, which is feeling a bit bloated.
