# CLAUDE.md — edutap.image_api

Repository-specific rules. They take precedence over the global defaults.

## Language

**English only.** This repository belongs to eduTAP proper, not to any single
institution: README, changelog, documentation, docstrings, code comments, commit
messages, pull request titles and bodies, and replies to review comments.

The language follows the repository, not the conversation. A discussion held in
German still produces English artefacts here.

## What this service is

Analysis and transformation of images: biometric checks and automatic cropping for ID
photos and wallet passes. A stateless computation.

## Guard rails

**This service stores nothing, and that is the design.** Storage and delivery of
person images belong to `edutap.image_service`; the split exists because
transformation is a pure computation while delivery needs storage, access control and
cache-friendly URLs. A cache, a temp directory that outlives a request, or a database
would erase the distinction.

**Person images are the most sensitive payload in the whole stack.** They arrive, they
are transformed, they leave. Never log them, never include them in an error report,
never keep them for diagnostics.

**A biometric verdict is advice, not a decision.** The service reports what it
measured; whether a photo is acceptable is a decision for the issuing process, which
knows the rules and the exceptions.

**Reject rather than guess.** An image that cannot be assessed produces a clear
refusal, not a best-effort crop — a silently wrong crop reaches a printed card.

## Sources and confidentiality

**No vendor internals — from any vendor, not just the ones currently in play.**
Neither in files nor in commit messages.

The standard is academic: a statement counts as reliable only where it can be
evidenced from public information, with a link. Everything else came from a protected
source, from our own testing, or from insider knowledge, and the four are not
interchangeable:

* **Documented** — public source, linked. May be written as fact.
* **Verified, not citable** — obtained by a person from an access-protected area and
  checked there; the reference is recorded internally but must not be published; and
  the statement has been reduced to what is not confidential. May be written as fact,
  carrying this label. It is the rule journalism uses for source protection: the claim
  stands, we know where it comes from, the reader does not get the source.

  The four conditions hold together. A statement for which nobody can name the
  internal reference does not fall here — that is insider knowledge.
* **Measured** — established by our own tests. May be written down, but always marked
  as such, because it describes what a platform did on the day we looked, not what it
  guarantees. It can change with the next release, without notice and without an entry
  in any changelog.
* **Insider knowledge** — is not written down at all.

What a platform's behaviour *means for us* stays documentable even where the mechanism
does not.

Contract and regulatory material is wanted and citable: eduPersonAssurance, GÉANT and
eduGAIN terms, published wallet programme obligations.

## Working practice

Branch first, never commit on `main`. Push only when asked. Lint and tests green
before opening a pull request.

Design records under `docs/superpowers/` record a decision at a point in time — do not
rewrite them to match a later state; write a new one.
