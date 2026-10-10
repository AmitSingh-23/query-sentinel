# DATA_CONTRACTS

## Existing (never modified)
- public.tenants, public.orders, public.order_items (scripts/init_db.sql)
- optimizer_meta.optimization_runs, query_history, audit_events, migrations
- models/gnn_bottleneck.pt (PlanGCN, 32 node features, 4 classes), models/rl_policy.json (tabular Q-table)

## New (added per phase below)

### P1 migration 001_qs_meta.sql
- schemas qs_meta, qs_dynamic; tables qs_meta.data_sources, datasets, dataset_tables, dataset_columns, schema_versions, ingestion_runs, audit_log, query_runs (columns: see file)
- optimizer_meta.query_history.data_source_id text NOT NULL DEFAULT 'demo' (backfills existing rows)
- role qs_nlq_reader NOLOGIN (SELECT on demo tables + qs_dynamic; default privileges); qs_app is member; qs_app CRUD on qs_meta
- seed row data_sources('demo')

### P2 dynamic datasets
- table `qs_dynamic.<dataset>__<entity>`; all inferred columns nullable; hidden `_qs_ingest_id text` = ingestion run id (rollback handle)
- dataset_columns.stats jsonb: null_ratio, distinct_estimate, distinct_capped, min, max, sample_values (low-cardinality text only, PII-filtered)

### P8 models/gnn_gatv2.pt
- payload {meta: {architecture: PlanGATv2, feature_schema_version 1, edge_feature_version 1, checkpoint_version 1, feature_dim 32, edge_dim 8, num_classes 4, training_dataset synthetic_plan_generator_v1, metrics}, state_dict}
