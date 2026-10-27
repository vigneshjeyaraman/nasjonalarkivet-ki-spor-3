# Incident report: new documents missing from search

## Symptom

At 09:05 UTC on 2026-09-15, the reading room reported that documents published after about 08:30 were missing from search. Older documents remained searchable, and search was not slow (`ticket.md:3-10`).

## Timeline (all times UTC, 2026-09-15)

| Time | Event and source |
| --- | --- |
| 01:00 | The nightly reindex created `records-2026-v2`, allocated its shard to `search-2`, and began copying `records-2026` (`changes.log:5`; `logs/search.log:3-5`). |
| 06:02 | Reindex finished without failures. The alias switch was skipped because `--switch-alias` was not set (`logs/search.log:9`; `changes.log:6`). |
| 06:13 | `search-2` passed the 85% low disk watermark (`logs/search.log:10`; `metrics.csv:76-77`). |
| 07:23 | `search-2` passed the 90% high watermark; the old index's shard could not be relocated to `search-1` (`logs/search.log:11-12`). |
| 07:40-07:50 | The frontend rollout briefly coincided with 14 HTTP 5xx responses per minute. That rate returned to zero by 07:50, while indexing still ran (`changes.log:7-8`; `metrics.csv:94-96,104`). |
| 08:30-08:35 | `search-2` crossed the 95% flood stage at 08:31:04. The cluster marked `records-2026` and `records-2026-v2` read-only. Bulk writes then failed with `429 cluster_block_exception`; after five retries, the indexer returned the batch to its queue. Indexed documents per minute fell from 35 to 0 and queue depth rose from 4 to 124 (`logs/search.log:14-15`; `logs/indexer.log:10-16`; `metrics.csv:104-105`). |
| 09:05 | The reading room reported the missing documents; the queue had reached 1,024 (`ticket.md:3-10`; `metrics.csv:111`). |
| 10:00 | Indexing remained at zero and queue depth reached 2,674 (`metrics.csv:122`). |

## Hypotheses

### 1. Reindex filled `search-2`, causing a write block (strongest)

- **For:** The new index was allocated to `search-2`; the alias switch was skipped; its disk usage rose from 71% to 95.3%; and the flood-stage block immediately preceded the `429` errors (`logs/search.log:2-5,14-15`; `changes.log:6`; `metrics.csv:2,105`; `logs/indexer.log:11`).
- **Against / uncertainty:** The saved logs do not show the live sizes of both indices. They establish the block but do not by themselves measure how much space the reindex consumed.
- **Rule out:** If the live index list shows that `records-2026-v2` is absent or too small to account for the disk growth, investigate other disk consumers.

### 2. Frontend rollout disrupted search

- **For:** The rollout began at 07:40, near a brief 5xx increase (`changes.log:7-8`; `metrics.csv:94-95`).
- **Against:** 5xx returned to zero by 07:50, indexing succeeded at 08:30, and the later write failure explicitly names the disk block (`metrics.csv:96,104-105`; `logs/indexer.log:10-11`).
- **Rule out:** Confirm that the frontend error burst ended before the first failed bulk write; the saved metrics and logs already support this.

### 3. TLS certificate warning stopped indexing

- **For:** The indexer logged a certificate warning at 08:12 (`logs/indexer.log:9`).
- **Against:** The certificate had 29 days remaining, a bulk write succeeded at 08:30, and the 08:31 failure was a disk-related `429`, not a TLS error (`logs/indexer.log:9-11`).
- **Rule out:** Check for TLS handshake failures near 08:31; none appear in the supplied indexer excerpt.

## Next check

Run one read-only query against the live cluster: `GET _cat/indices/records-2026*?v&h=index,store.size`. Confirm that both indices still exist and compare their sizes before deciding how to recover space. The supplied logs already establish the write block; this query tests whether the duplicate index explains the disk growth.
