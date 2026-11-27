# EVOKS Migration Guide

If you are already using EVOKS, you must perform the following migration steps before upgrading to SKOSMOS 3.

## Background

### Problem

Previous versions of EVOKS allowed terms to be created without a language tag.

SKOSMOS 3 does not include such terms in the alphabetical index. As a result, affected concepts may no longer be visible through the index navigation after the upgrade.

### Solution

All terms without a language tag must be updated.

The affected data is stored in the Fuseki databases (`fuseki-dev` and, if applicable, `fuseki-live`). A migration script is provided in the `migration` directory:

```bash
migration/migrateFuseki2Skosmos3.sh
```

The script checks all available vocabularies for terms without a language tag. If affected terms are found, the script prompts for a default language (for example `en`) and updates the terms accordingly.

## Configuration Changes

SKOSMOS 3 introduces several breaking changes in `skosmos-[dev|live]/config.ttl`:

| SKOSMOS 2 | SKOSMOS 3 |
|------------|------------|
| `skosmos:uiHoneypotEnabled` | `skosmos:feedbackHoneypotEnabled` |
| `skosmos:uiHoneypotTime` | `skosmos:feedbackHoneypotTime` |
| `skosmos:sparqlDialect "JenaText"` | `skosmos:sparqlDialect "Generic"` |

---

# Migration Steps

## 1. Create a Backup

Before starting the migration, you should **at least** export or download all vocabularies available in EVOKS.
Alternatively, you may create a complete backup or snapshot of the server and its data volumes.

## 2. Update the Git Repository

```bash
cd EVOKS
git pull
```

## 3. Migrate Development Vocabularies (`skosmos-dev`)

Run the migration script:

```bash
bash migration/migrateFuseki2Skosmos3.sh
```

Example output:

```text
Fuseki container: evoks_evoks_fuseki-dev
Fuseki network: evoks_fuseki-dev
Vocabularies found: Test

=========================================================================================
Check for terms in vocabulary 'Test'...
--------------------------------------------
    There are 1 term(s) without a linked language
    Try to fix the vocabulary...
    Use the following language as default [en, 'x'=SKIP]:
    Use en as default language.
   ... fixed!
=========================================================================================

Migration of EVOKS finished!
```

## 4. Migrate Released Vocabularies (`skosmos-live`)

If you have already published vocabularies, run the migration for the live environment as well:

```bash
bash migration/migrateFuseki2Skosmos3.sh live
```

Example output for two released vocabularies:

```text
Fuseki container: evoks_evoks_fuseki-live
Fuseki network: evoks_fuseki-live
Vocabularies found: Test-1 Test-2

=========================================================================================
Check for terms in vocabulary 'Test-1'...
--------------------------------------------
    There are 1 term(s) without a linked language
    Try to fix the vocabulary...
    Use the following language as default [en, 'x'=SKIP]:
    Use en as default language.
   ... fixed!
=========================================================================================
Check for terms in vocabulary 'Test-2'...
--------------------------------------------
    There are 1 term(s) without a linked language
    Try to fix the vocabulary...
    Use the following language as default [en, 'x'=SKIP]:
    Use en as default language.
   ... fixed!
=========================================================================================

Migration of EVOKS finished!
```

## 5. Update the SKOSMOS Configuration

Update all affected `config.ttl` files according to the changes listed in the **Configuration Changes** section above.

## 6. Pull the New SKOSMOS Images

```bash
docker compose build --pull
```

## 7. Restart EVOKS

```bash
docker compose up -d
```

## 8. Verify the Installation

Open both SKOSMOS instances (`dev` and `live`) and verify that:

- all vocabularies are available,
- the alphabetical index is displayed,
- concepts previously missing a language tag are now visible in the index.

## Migration Complete

The migration to SKOSMOS 3 is now complete.

# Important Note for Future Imports

If older vocabularies created with previous EVOKS versions are imported after the migration, they may still contain terms without a language tag.

In this case, run the migration script again for the affected environment (dev or live) to update the imported terms:

```bash
bash migration/migrateFuseki2Skosmos3.sh [live]
```
The script can safely be executed multiple times. It only updates vocabularies that still contain terms without a language tag.
