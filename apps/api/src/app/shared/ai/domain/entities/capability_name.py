from typing import NewType

CapabilityName = NewType("CapabilityName", str)
"""Identifies an AICapability, e.g. "generate_title".

A NewType, not an enum: capabilities are meant to be numerous and
pluggable (unlike the small, deliberate set of AIProviderName values), so
adding one must never require editing a shared type. This wrapper exists
so capability identifiers aren't spread as bare `str` throughout the
codebase - every signature that takes a capability identifier uses this
type, giving one place to upgrade to a richer value object later (e.g. one
that also carries a version) without touching call sites' logic, only
their type imports.
"""
