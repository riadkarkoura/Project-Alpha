# ADR-0002
# Feature-Owned AI Capabilities

## Status

Accepted

## Context

The AI Execution Engine (`app/shared/ai/`) is a platform-wide capability: `AIExecutionEngine`, `AIOrchestrator`, `ProviderResolver`, and the provider/capability registries all live there, with zero knowledge of any specific feature or business capability. Concrete `AICapability` implementations, however, are inherently feature-specific - they know what a product's title, description, or category mean. Building the first real capability (Generate Product Description, for Product Intelligence) required deciding where capability *registration* happens, since `shared/ai`'s own capability registry starts empty.

The naive approach - having `shared/ai`'s own DI wiring import and register every feature's capability directly - would make `shared/ai` depend on `product_intelligence` (and every future feature that adds a capability), inverting the dependency direction the whole AI architecture depends on: features are meant to depend on `shared/ai`, never the reverse.

## Decision

Each feature that owns AI capabilities composes its own `AIExecutionEngine` instance, built from `shared/ai`'s reusable building blocks (`ProviderResolver`, `AIOrchestrator`) plus a capability registry populated with only that feature's own capabilities.

Concretely: `product_intelligence/presentation/api/dependencies.py` defines `get_product_intelligence_ai_execution_engine()`, which builds a fresh `AICapabilityRegistry`, registers `GenerateProductDescriptionCapability` into it, and combines it with `shared/ai`'s `get_provider_resolver()` / `get_ai_orchestrator()` dependencies. `shared/ai`'s own `get_ai_execution_engine()` (with its permanently empty capability registry) is untouched and remains valid as reference wiring with no capabilities - no feature depends on it directly.

Concrete `AICapability` implementations live inside the feature that owns them (e.g. `product_intelligence/infrastructure/ai/`), not inside `shared/ai/infrastructure/`, since they are adapters between a feature's domain model and the shared AI contract, not a platform-wide execution concern.

## Consequences

Benefits

- `shared/ai` never imports from any feature - dependency direction stays strictly inward.
- Adding a new capability to an existing feature, or a new feature with its own capabilities, never requires touching `shared/ai`.
- Each feature's composed engine only ever exposes the capabilities that feature actually owns - no feature can accidentally invoke another feature's capability through a shared, platform-wide registry.

Trade-offs

- Capability registries are now assembled in N places (one per feature that owns AI capabilities) instead of one central place - discovering "every capability registered anywhere" requires checking each feature's DI wiring rather than one shared registry.
- Minor duplication: each feature's "compose an engine" DI function repeats the same three-dependency assembly pattern.

## Alternatives Considered

A single, platform-wide capability registry, populated centrally in `shared/ai`'s own DI wiring by importing every feature's capabilities.

Rejected because it requires `shared/ai` to depend on every feature that defines a capability, inverting the architecture's core dependency rule and reintroducing the coupling problem this AI architecture was designed to avoid.

A shared capability registry mutated by each feature at startup via a plugin-registration hook.

Rejected as unnecessary infrastructure for the current stage - not required until multiple features need to discover capabilities registered by *other* features, which hasn't happened yet. Documented here rather than built, per Project Alpha's MVP-first direction: avoid speculative infrastructure until a concrete need exists.
