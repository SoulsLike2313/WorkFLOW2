# FACTORY_SCREEN_ARCHETYPES_V1

Статус:
- version: `v1`
- layer_type: `screen_archetypes`
- labels_used: `ACTIVE | RECOMMENDED | FUTURE | NOT YET IMPLEMENTED | STYLE-LAYER ONLY`

## 1) Factory Overview

Role:
- first-glance command state.

Required panels:
1. products in work;
2. department status summary;
3. owner gates waiting;
4. critical blockers;
5. active waves.

Trust exposure:
- source-backed summaries only.

## 2) Department Floor

Role:
- see all departments including non-active.

Required panels:
1. department cards with status;
2. activation condition;
3. load state;
4. emitted starter artifacts.

Trust exposure:
- status card + source linkage.

## 3) Product Lane Board

Role:
- pipeline routing visibility by product.

Required panels:
1. lane stage;
2. current department;
3. next step;
4. blockers.

## 4) Product Detail View

Role:
- deep state for one product.

Required panels:
1. technical map snapshot;
2. defect/noise board;
3. owner gates;
4. recommended path;
5. evidence links.

## 5) Owner Gate Console

Role:
- decision workspace for owner gates.

Required panels:
1. pending gate list;
2. option comparisons;
3. decision consequences;
4. required evidence links.

## 6) Contradiction Ledger

Role:
- show open/closed contradictions.

Required panels:
1. contradiction cards;
2. severity;
3. closure owner;
4. trace links.

## 7) Change Feed

Role:
- timeline of meaningful changes.

Required panels:
1. change items;
2. affected artifact;
3. impact class;
4. before/after reference.

## 8) Before/After Viewer

Role:
- visual and functional delta inspection.

Required panels:
1. baseline snapshot;
2. new snapshot;
3. diff highlights;
4. trust delta.

## 9) Force Map

Role:
- Emperor/Primarch/Astartes attachment and load view.

Required panels:
1. role nodes;
2. department attachments;
3. idle/active/blocked state;
4. load bars.

## 10) Queue Monitor

Role:
- operational queue pressure board.

Required panels:
1. intake;
2. assignment;
3. execution;
4. review;
5. blocker;
6. release queues.

## Tone rule

Все archetypes держат command-board tone: calm, dense, high-trust, no decorative noise.
