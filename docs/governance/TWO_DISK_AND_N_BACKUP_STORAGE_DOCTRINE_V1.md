# TWO_DISK_AND_N_BACKUP_STORAGE_DOCTRINE_V1

Status:
- class: `foundation_storage_doctrine`
- mutability: `immutable_by_default`
- change_authority: `EMPEROR_ONLY`
- implementation_state: `doctrine_vector_no_physical_migration_tests`

## Base layout

1. `disk-1` (live primary):
- active repo/runtime/control working surfaces.
2. `disk-2` (history/recovery):
- logs/history/backups/recovery support artifacts.

## N-backup extension

1. backup surfaces may scale to `N` disks,
2. each backup target must preserve canonical step metadata,
3. restore must be able to identify latest valid canonical checkpoint.

## Read/write role discipline

1. live-write path prioritizes disk-1,
2. history/backup write path prioritizes disk-2..N,
3. restore read path must prefer latest valid canonical evidence chain.

## Boundary

No physical disk migration tests are performed in this doctrine tranche.
