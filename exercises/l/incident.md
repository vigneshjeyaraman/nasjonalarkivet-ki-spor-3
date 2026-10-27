# Incident Report: New documents missing from search

## Timeline (2026-09-15)
- **01:00**: Reindex of `records-2026` to `records-2026-v2` started on `search-2`. (search.log)
- **06:02**: Reindex completed. (search.log)
- **06:13**: `search-2` exceeded low disk watermark (85%). (search.log)
- **07:23**: `search-2` exceeded high disk watermark (90%). (search.log)
- **08:31**: `search-2` exceeded flood stage disk watermark (95%). (search.log)
- **08:31**: `search-2` marked all indices read-only: `index.blocks.read_only_allow_delete = true`. (search.log)
- **08:31**: Indexer began receiving `429 cluster_block_exception`. (indexer.log)
- **08:31 - 10:00**: Indexer retries fail; batches returned to queue. Queue depth grows from 4 to 2674. (indexer.log, metrics.csv)
- **09:05**: Ticket 4711 reported: new documents missing from search. (ticket.md)

## Hypotheses

### H1: Disk saturation due to duplicate indices (Strongest)
**Evidence For:** 
- Reindex created `records-2026-v2`. (search.log)
- Disk usage on `search-2` rose steadily from 71% (00:00) to 95% (08:31). (metrics.csv)
- flood stage watermark triggered read-only block exactly when indexing stopped. (search.log)
**Evidence Against:** None.
**Rule out:** Verify if both `records-2026` and `records-2026-v2` exist and occupy significant space.

### H2: Frontend deploy caused the issue
**Evidence For:** Deploy happened at 07:40. (ticket.md)
**Evidence Against:** 
- Only a short burst of 5xx errors. (search.log)
- Indexing continued normally until 08:31. (indexer.log)
**Rule out:** This is a correlation, not a cause.

### H3: TLS Certificate expiry
**Evidence For:** Warning at 08:12 about cert expiring in 29 days. (indexer.log)
**Evidence Against:**
- Indexing continued for 20 minutes after the warning. (indexer.log)
- 429 error is specific to disk usage, not TLS. (indexer.log)
**Rule out:** Cert is not yet expired.

## Next Check
Run the following read-only commands to confirm disk usage and index duplication:
`GET _cat/allocation?v` and `GET _cat/indices/records-2026*?v&h=index,store.size`
