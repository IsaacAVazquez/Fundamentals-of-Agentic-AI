"""Errors the CLI turns into a one-line message and an exit code."""


class WikiError(Exception):
    """Base class. `cli.main` prints `wiki: <message>` and exits with `exit_code`."""

    exit_code = 1


class UsageError(WikiError):
    exit_code = 2


class OllamaUnreachable(WikiError):
    exit_code = 3


class ModelMissing(WikiError):
    exit_code = 4


class VaultMissing(WikiError):
    exit_code = 5


class NothingToIndex(WikiError):
    exit_code = 6


class BackendError(WikiError):
    exit_code = 1


class DoctorFailure(WikiError):
    exit_code = 10


class OnlineWhenOfflineRequired(WikiError):
    exit_code = 11
