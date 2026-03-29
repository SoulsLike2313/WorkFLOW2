# PRODUCT_PROMOTION_FILE_SPEC_V1

Статус:
- spec_version: `v1`
- role: `machine-readable promotion instruction file for TikTok Agent / future growth console`
- labels_used: `ACTIVE | RECOMMENDED | FUTURE | NOT YET IMPLEMENTED`

## 1) File purpose

Единый файл, который говорит:
1. what to post;
2. where to post;
3. when to post;
4. why this content exists.

## 2) Required fields

1. product_id
2. product_state_match
3. target_audience
4. channel_lane
5. content_unit_id
6. content_type
7. posting_window
8. message_goal
9. evidence_reference
10. allowed_claims
11. prohibited_claims
12. cta_type
13. owner_gate_reference
14. safety_flags

## 3) Product state match

Каждая промо-единица должна указывать:
1. под какой продуктовый статус она валидна;
2. запрещено ли использовать ее после смены продуктового состояния.

## 4) Evidence support

Каждый message должен иметь:
1. evidence source path;
2. допустимую формулировку claim;
3. запрет на расширение claim без новой валидации.

## 5) Prohibited content

1. claims without evidence;
2. claims that contradict known product limits;
3. promises of outcomes that product cannot deliver.

## 6) Example structure (JSON-like)

1. `promotion_items[]`
2. each item contains all required fields from section 2.

## 7) Seed-stage boundary

Spec задает контракт;
full automated campaign engine remains `NOT YET IMPLEMENTED`.
