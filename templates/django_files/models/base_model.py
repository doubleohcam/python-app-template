"""Module for the base model class.

The BaseModel has various attributes and methods that are required
across all models in the {app_name_pretty} application.
"""

from __future__ import annotations

from typing import ClassVar

import auto_prefetch  # reduce n+1 queries
from dirtyfields import DirtyFieldsMixin  # track changes to model fields
from django.db import models


class BaseModel(DirtyFieldsMixin, auto_prefetch.Model):
    """Base model class."""

    id: int

    created_at = models.DateTimeField(
        verbose_name="Created At",
        auto_now_add=True,
        help_text="The date and time that the record was created.",
    )

    updated_at = models.DateTimeField(
        verbose_name="Updated At",
        auto_now=True,
        help_text="The date and time that the record was last updated.",
    )

    class Meta(auto_prefetch.Model.Meta):
        """Meta options for the base model class."""

        abstract: bool = True
        ordering: ClassVar[list[str]] = ["-created_at", "-updated_at"]

    def __str__(self) -> str:
        """Return a string representation of the model."""
        return f"{self.__class__.__name__} object ({self.id})"
