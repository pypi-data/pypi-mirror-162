"""Exceptions for Sinai."""


class MetricNotFound(Exception):
    """The search did not yield any result."""

    ...


class SourceError(Exception):
    """The Source did not return the required result."""

    ...


class DependencyMissing(Exception):
    """Missing a dependency to use an optional feature."""

    ...


class SourceNotFound(Exception):
    """Could not find the requested source instance."""
