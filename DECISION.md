# Decision note — worthwhile automation

## Scope and recommendation

I chose **missing-information follow-up** rather than quote approval. The coordinator says photos/serial numbers are commonly needed, the current process uses a shared inbox, spreadsheet and saved replies, and duplicate reminders happen. The data supports a small reconciliation problem, but not the owner's claim of eight hours lost per week: the sample is only two weeks, quick calls are not fully logged, and logged active minutes are coordinator effort rather than customer waiting time.

I recommend **a process change first, not two engineering weeks of AI development**. Add a deterministic, reviewable follow-up queue to the existing spreadsheet/inbox process. It should reconcile case status, request status, received timestamps, opt-out, contact/timing completeness and the 48-hour rule. Automatic customer contact should remain a later pilot, after measuring real coordinator time and false/duplicate reminders.

## What the supplied data says

| Measure | Result | Treatment |
|---|---:|---|
| Cases | 24 | all supplied cases retained |
| Requests | 30 | all retained; 8 pending in-scope rows are evaluated |
| Event deliveries | 128 | 4 repeated `event_id`s treated as duplicate deliveries |
| Unique events | 124 | stable `event_id` used for effort/count metrics |
| Known coordinator effort | 400 min | duplicate deliveries removed; missing effort remains unknown |
| Logged reminder effort | 9 min | unique reminder events only |
| Baseline actions | 7 | pending + `waiting_info` + follow-up allowed |
| Proposed actions | 4 | eligible after reconciliation |
| Proposed reviews | 3 | ambiguous/unsafe to auto-contact |

The proposed queue therefore reduces proposed contacts from 7 to 4 (43%) on this snapshot, but this is **not** a measured 43% time saving. C018 has `received_at` populated despite `pending`, C022 has no request timestamp, and C016 is below the 48-hour threshold at the snapshot. C012 is explicitly opted out and is excluded. C024 is eligible at 69 hours and has two outstanding items, which can be combined into one reviewable action.

The strongest data-quality finding is that duplicate event deliveries would increase known effort from 400 to 412 minutes if counted naively. I therefore deduplicate by stable `event_id` before calculating effort.

## Alternatives and technical claim

**Process-only change:** retain the spreadsheet and inbox, but make the reconciliation fields mandatory and use the queue rules. Cost assumption: no new recurring tool cost. This is my preferred next step because the evidence is too small to justify engineering effort.

**Existing file-collection tool:** Microsoft OneDrive/SharePoint file requests allow recipients to upload through a link without needing OneDrive and prevent them from browsing the destination folder. That could simplify photo collection, but it does not by itself reconcile stale spreadsheet state or decide when a reminder is safe. citeturn0search0

**Existing approval automation:** Power Automate supports approval actions and can combine approvals with workflows, but Microsoft documents licensing and Dataverse prerequisites for some approval setups. That makes it more relevant to quote approval than the narrow missing-information problem selected here. citeturn0search1turn0search5

The technical claim I tested is: **a deterministic eligibility gate can reduce unsafe/duplicate follow-up proposals without an LLM, while routing ambiguous records to humans.** The local experiment supports the claim on this synthetic snapshot: 7 baseline actions become 4 actions and 3 reviews, with explicit reasons. It does not demonstrate production accuracy, customer adoption, or messaging reliability.

## Net value and next experiment

A transparent two-week estimate uses only directly observed reminder effort plus explicit assumptions. The data records **9 reminder minutes**. Two reminder records are clearly associated with conditions the proposed gate would catch at snapshot review (C012 opt-out: 2 min; C018 received-but-still-pending: 2 min), so I use **4 minutes as observed avoidable effort**, not a forecast of all future savings. Assume the coordinator spends 1 minute reviewing each of the 3 ambiguous rows and 2 minutes per two-week period operating/reconciling the queue. Estimated net = **4 − 3 − 2 = −1 minute per two weeks**. At this sample size, the economic case is therefore unproven and slightly negative under these assumptions. No tool cost is added because the recommendation is process-only.

The next real-world experiment should measure every missing-information request for four weeks: coordinator active minutes, duplicate/incorrect reminders, requests resolved after each contact, and cases requiring manual reconciliation. Continue only if the queue saves at least **30 coordinator minutes per four weeks** without increasing incorrect/duplicate contact; otherwise stop or keep the process manual.
