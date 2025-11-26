# Semantic Indexing and Encyclopedia Design

## Goals
- Convert existing Markdown corpus into a navigable semantic library without altering original sources.
- Remove conversational/noisy text while preserving technical meaning and structure.
- Split sources into existing logical units (chapters, sections, concepts) and index each unit with stable location codes.
- Produce an encyclopedia layer that points to source locations with brief descriptions and rich semantic metrics (axiom counts, clusters, contradictions, etc.) without duplicating source text.
- Provide a CLI for ingestion, analysis, and querying.

## Source Ingestion and Cleaning
1. **Scope**: Traverse all `.md` files under the repository; each file becomes a source document with an internal ID.
2. **Parsing**: Use a Markdown parser that preserves heading hierarchy, lists, blockquotes, code fences, tables, and inline math markers.
3. **Conversational Removal**:
   - Detect Q/A patterns, imperatives to the reader, meta-commentary ("note to self", "todo", "please see"), and dialogue markers; strip or tag them as `conversational` and exclude from semantic metrics.
   - Normalize whitespace, punctuation, and heading levels; deduplicate repeated sentences across files via hashing to avoid redundant metrics.
4. **Normalization**:
   - Standardize heading slugs and capture exact line ranges per block.
   - Preserve citations/identifiers (e.g., `Am154nb2`) as anchors rather than content to be transformed.

## Section Detection and Location Codes
- **Segmentation**: Split documents along existing headings. Within a heading, further split when encountering lists or paragraphs that contain self-contained propositions/axioms.
- **Location Code Format**: `source-path::slug-chain::block-seq`. Example: `intake/BOX_CALCULUS__TECHNICAL_INTRODUCTION_DUAL-COLUMN_CROSS-REFERENCED.md::box-algebra::b3`.
- **Stability Rules**:
  - Use heading slug chain (H1→H2→H3) plus a deterministic block sequence number.
  - Store line ranges to allow reproducible references without embedding source text in the index.
- **Anchoring External IDs**: If a block begins with an inline ID like `Am154nb2 11/25/2025`, map it to the same location code and store the inline ID as an alias.

## Encyclopedia Entry Model
Each encyclopedia item references one segmented block and **never stores full source text**.

```yaml
id: ENC-000123
source_path: intake/BOX_CALCULUS__TECHNICAL_INTRODUCTION_DUAL-COLUMN_CROSS-REFERENCED.md
location_code: intake/BOX_CALCULUS__TECHNICAL_INTRODUCTION_DUAL-COLUMN_CROSS-REFERENCED.md::box-algebra::b3
aliases: [Am154nb2]
heading: Box Algebra
description: "Defines Box as a δ-geometry, Φ-projection, Π-evaluation operator."
metrics:
  axiom_count: 3
  concept_terms: [Box, δ-geometry, Φ-projection, Π-evaluation]
  embedding_cluster: box-algebra
  contradiction_flags: []
  dependency_links: [ENC-000120]
  date_tags: [2025-11-25]
relationships:
  children: []
  parents: [ENC-000050]  # higher-level chapter/section
  references: [Am458mk5]
```

## Semantic Metrics to Capture
- **Axiom Count**: Detect sentences declared as axioms or propositions; count per block and aggregate per section.
- **Concept Density**: Terms per sentence, domain glossary match rate, entropy of concept distribution.
- **Entity Extraction**: Symbols (δ, Φ, Π), operators (Box), transformations (route, collapse), dates, and version tags.
- **Clustering**: Embedding-based clusters at document and block levels; cluster labels derived from top terms.
- **Contradiction Signals**: Natural-language inference on block pairs within the same cluster; flags saved without source duplication.
- **Dependency Graph**: Directed edges for cross-references, prerequisite sections, and transformations (e.g., δ→Φ→Π pipeline).
- **Temporal/Revision**: Capture inline dates (e.g., `11/25/2025`) for timeline queries.

## Processing Pipeline
1. **Scan**: Enumerate Markdown sources and register documents.
2. **Clean**: Strip conversational blocks and normalize text; log removals for audit.
3. **Segment**: Build heading tree; split into atomic concept blocks with line ranges and aliases.
4. **Annotate**: Compute metrics (axioms, concepts, embeddings, contradiction flags, dependencies).
5. **Index**: Persist encyclopedia entries plus metrics in a queryable store; keep raw sources untouched.
6. **Validate**: Ensure one-to-one mapping between source blocks and encyclopedia entries (no duplicated text).

## Storage Layout
- `data/sources/`: Checksums and metadata per Markdown file.
- `data/clean/`: Cleaned, normalized Markdown (same structure as sources, no conversational text).
- `data/segments.jsonl`: One JSON object per block with location code, heading chain, aliases, line range.
- `data/metrics.sqlite`:
  - `sources(id, path, checksum)`
  - `segments(id, source_id, location_code, heading, aliases, line_start, line_end)`
  - `metrics(segment_id, axiom_count, cluster_id, contradiction_flag, concept_vector, date_tags, dependency_ids)`
  - `clusters(id, label, centroid_vector)`
- `data/encyclopedia.jsonl`: Thin records with `id`, `location_code`, `description`, and key metrics.

## CLI Design (No Implementation Yet)
Command group: `hgg-index`

- `hgg-index ingest <path>`: Register Markdown sources, compute checksums.
- `hgg-index clean [--preview]`: Produce cleaned copies and a diff report of removed conversational text.
- `hgg-index segment [--source <path>] [--min-lines N]`: Build segments, assign location codes, and list alias mappings (e.g., `Am230mnbh`).
- `hgg-index annotate [--metrics all|axioms|clusters|contradictions]`: Compute semantic metrics and store in SQLite/JSONL.
- `hgg-index encyclopedia [--export jsonl|csv]`: Emit pointer records (id, location_code, description, metrics summary).
- `hgg-index search "query" [--by location|alias|fulltext|semantic]`: Query by text, semantic embedding, alias ID, or location code; return matching encyclopedia entries with scores.
- `hgg-index entry <id>`: Show a single entry with description, metrics, and source pointer (line range + heading chain).
- `hgg-index graph [--cluster <id>]`: Render dependency/cluster graph for segments.
- `hgg-index doctor`: Validate that every segment has exactly one encyclopedia entry and that no source text is duplicated in outputs.

## QA and Next Steps
- Validate cleaning rules on representative files (e.g., `intake/BOX_CALCULUS__TECHNICAL_INTRODUCTION_DUAL-COLUMN_CROSS-REFERENCED.md`) to ensure technical statements are preserved.
- Confirm that location codes and alias handling satisfy the provided `Am154nb2`, `Am458mk5`, and `Am230mnbh` patterns.
- Once approved, proceed to implement parsers, metrics modules, and CLI commands following this design.
