# Package 05 — State Representation Reconciliation

## 1. Conflicting Specifications

The architecture specification (`docs/recovery_state_machine.md`) demands a highly granular, robust state machine to enforce the lifecycle of a `RecoveryCase`. It requires the system to distinguish fine-grained phases such as `DETECTED`, `ENRICHING`, `ASSESSED`, `PLANNING`, `POLICY_REVIEW`, `WAITING_APPROVAL`, `EXECUTING`, and `VERIFYING`.

However, the frozen P02/P03 domain model deliberately deferred workflow tracking. `RecoveryCase` simply records `status` (OPEN/CLOSED) and an eventual `outcome_type` (RECOVERED, NOT_RECOVERED, etc.). As a result, there is a fundamental conflict between the architectural need for durable, granular workflow states and the available persistence model.

## 2. Frozen P02/P03 State Representation

P02/P03 relies entirely on the presence of related entities and specific enums:
- **RecoveryCase:** `status` (OPEN/CLOSED) and `outcome_type` (RECOVERED, NOT_RECOVERED, SUPPRESSED, ESCALATED, EXPIRED, UNKNOWN).
- **RecoveryAction:** `status` (PROPOSED, AUTHORIZED, EXECUTING, EXECUTION_UNKNOWN, VERIFICATION_PENDING, VERIFIED_SUCCESS, VERIFIED_FAILURE, CANCELLED, ESCALATED).
- **Other Entities:** `RiskAssessment`, `InterventionPlan`, `PolicyDecision`, `VerificationRecord`.

| `WAITING_APPROVAL`| Needs human authorization. | No explicit representation. | NO (Looks like PROPOSED/ESCALATED) | NO |
| `EXECUTING` | `RecoveryAction` is `EXECUTING`. | Yes | Yes | Yes |
| `VERIFYING` | `RecoveryAction` is `VERIFICATION_PENDING`. | Yes | Yes | Yes |
| `RECOVERED` | Case `CLOSED`, `outcome=RECOVERED`. | Yes | Yes | Yes |
| `NOT_RECOVERED`| Case `CLOSED`, `outcome=NOT_RECOVERED`. | Yes | Yes | Yes |
| `UNKNOWN` | Case `CLOSED`, `outcome=UNKNOWN`. | Yes | Yes | Yes |
| `SUPPRESSED` | Case `CLOSED`, `outcome=SUPPRESSED`. | Yes | Yes | Yes |
| `ESCALATED` | Case `CLOSED`, `outcome=ESCALATED`. | Yes | Yes | Yes |
| `EXPIRED` | Case `CLOSED`, `outcome=EXPIRED`. | Yes | Yes | Yes |
| `CLOSED` | Case `CLOSED`. | Yes | Yes | Yes |

## 5. Ambiguous States

The following workflow states cannot be uniquely derived from P02/P03 facts alone:
1. **DETECTED vs. ENRICHING:** Since P03 records no enrichment status, a process crash during enrichment looks identical to a newly created case upon restart.
2. **ASSESSED vs. PLANNING:** Planning relies on external AI/policy processing. If this crashes before an `InterventionPlan` is persisted, the system sees an `ASSESSED` case. The failure is invisible.
3. **POLICY_REVIEW vs. WAITING_APPROVAL:** P02 `ActionStatus` provides `PROPOSED`, but there is no mechanism to track if an action is awaiting human approval vs. a fast-path algorithmic policy review.

## 6. Restartability Analysis

A financial state machine must precisely resume execution upon restart.
Because states like `ENRICHING`, `PLANNING`, and `WAITING_APPROVAL` are ephemeral to the process memory in P02/P03:
- If a worker crashes during enrichment, the restarted system will assume the case was just `DETECTED` and re-run enrichment blindly (violating idempotency if enrichment mutates external state).
- If the system is `WAITING_APPROVAL`, a restart might lose the "waiting" context entirely, leaving the case stuck as `PROPOSED` with no notification to human operators.

**Restartability is NOT guaranteed for intermediate pre-execution workflow stages.**

## 7. Failure-Recovery Analysis

- **Case Workflow Crash (Pre-Execution):** Fails silently. Ambiguous rollback to previous logical checkpoint (`DETECTED` or `ASSESSED`).
- **Action Execution Crash:** Supported cleanly. `ActionStatus.EXECUTING` persists. The system can confidently move to `EXECUTION_UNKNOWN` or `VERIFICATION_PENDING`.
- **Approval Crash:** Not supported. State is lost.
- **Verification Crash:** Supported cleanly via `ActionStatus.VERIFICATION_PENDING`.

## 8. Concurrency Analysis

If Worker A reads an `OPEN` case with no actions, it derives the state as `DETECTED`/`ASSESSED`. Worker B simultaneously processes the case and persists an `InterventionPlan` (state = `POLICY_REVIEW`). Worker A, running on a stale projection, might attempt to generate a duplicate `InterventionPlan`. P03's DB schema does not have a comprehensive workflow-level concurrency token (like a state version number) on `RecoveryCase` to prevent stale transitions during the early workflow phases.

## 9. Options

### Option A — Computed State
Derive state from related entities (e.g., `if action.status == EXECUTING then case is EXECUTING`).
- **Correctness:** Low. Fails to distinguish pre-execution states (Enrichment, Planning, Approval).
- **Persistence Implications:** Zero. No DB changes.
- **Migration Implications:** None.
- **Complexity:** High cognitive load mapping missing states.
- **Failure Behavior:** Silent retries, lost approval requests, non-deterministic restarts.
- **Auditability:** Poor. We cannot log transitions like `DETECTED -> ENRICHING` safely.

### Option B — Persisted Workflow State
Modify P02 `RecoveryCase` to include a dedicated `workflow_state` enum column mapping directly to `docs/recovery_state_machine.md`, and a `version` column for optimistic locking.
- **Correctness:** High. Guaranteed authoritative state.
- **Persistence Implications:** Requires a DB schema migration (adding `workflow_state` to `recovery_cases`).
- **Migration Implications:** Minimal but real (updating P02 `RecoveryCase` and P03 mappers/schema).
- **Complexity:** Simple. Explicit state machine transitions `state = next_state`.
- **Failure Behavior:** Perfectly restartable. Resumes from exact state.
- **Auditability:** Complete. Every granular transition is verifiable.

### Option C — Hybrid / Projection
Store workflow tracking in an independent `WorkflowStateRecord` table without touching P02/P03's core `RecoveryCase`.
- **Correctness:** Moderate. The system now has two sources of truth (`RecoveryCase.status` vs `WorkflowStateRecord`).
- **Persistence Implications:** New P05 table/repo.
- **Migration Implications:** Additive only.
- **Complexity:** High. Requires syncing P03 `RecoveryCase` terminal states with the new workflow record atomically.
- **Failure Behavior:** Good, provided transactions span both records.
- **Auditability:** High.

## Final Decision

**Decision:** OPTION B — Persisted Workflow State
**Status:** APPROVED ARCHITECTURE AMENDMENT REQUIRED

## Why Computed State Was Rejected
Computed state cannot satisfy the restartability and idempotency guarantees required by a financial state machine. Because early workflow phases (like `ENRICHING` or `WAITING_APPROVAL`) leave no durable artifacts in P02/P03, a process crash causes the system to forget the current stage, leading to non-deterministic restarts and potential duplicate API actions.

## Why Separate WorkflowStateRecord Was Rejected
Introducing a secondary table for workflow state creates a dual-source-of-truth anti-pattern. Maintaining absolute consistency between `RecoveryCase.status` and `WorkflowStateRecord.state` would require complex coordination and invite corruption.

## New Authoritative State Model
The `RecoveryCase` aggregate acts as the sole authoritative owner of its state, utilizing four distinct, non-overlapping fields:
- `status`: Business lifecycle (`OPEN` / `CLOSED`)
- `workflow_state`: Granular workflow phase (e.g., `DETECTED`, `EXECUTING`)
- `outcome_type`: Terminal business outcome (e.g., `RECOVERED`)
- `version`: Optimistic concurrency token (integer)

## Required Changes to P02
`RecoveryCase` will be updated to include `workflow_state` and `version`. A new `CaseWorkflowState` Enum will be created reflecting the exact vocabulary in `docs/recovery_state_machine.md`.

## Required Changes to P03
The `recovery_cases` schema must be migrated to include `workflow_state` (TEXT) and `version` (INTEGER). Database mappers and repositories will be updated to persist these fields and enforce optimistic locking on updates.

## Required Changes to P05
The state machine engine will be built around these persistent, authoritative fields instead of attempting to compute the state heuristically.

## Migration Requirements
A formal migration script must be executed. Existing `OPEN` cases must be carefully mapped to their corresponding `workflow_state` based on related facts. If a case is ambiguous, the migration must fail rather than invent data. `CLOSED` cases will map to their terminal counterpart based on their `outcome_type`.

## Concurrency Requirements
Updates to `RecoveryCase` will enforce optimistic concurrency checking (`WHERE version = ?`). This guarantees that a stale worker reading an `OPEN` case will fail to overwrite the database if another worker has already advanced the workflow state.

## Testing Requirements
The implementation will require tests proving that:
- Optimistic locking successfully blocks stale transitions.
- The DB schema migration runs flawlessly and handles ambiguous legacy state securely.
- All legal and illegal state transitions respect the new persisted `workflow_state` field.
# #   F i n a l   P r e - I m p l e m e n t a t i o n   C o n s i s t e n c y   C h e c k  
  
 # # #   1 .   S t a t e   O w n e r s h i p   M o d e l  
 T h e   a r c h i t e c t u r e   s u c c e s s f u l l y   s e p a r a t e s   c o n c e r n s   i n t o   f o u r   n o n - o v e r l a p p i n g   f i e l d s   o n   ` R e c o v e r y C a s e ` :  
 -   ` s t a t u s ` :   H i g h - l e v e l   b u s i n e s s   c o n t a i n e r   l i f e c y c l e   ( ` O P E N `   /   ` C L O S E D ` ) .  
 -   ` w o r k f l o w _ s t a t e ` :   A u t h o r i t a t i v e   g r a n u l a r   w o r k f l o w   s t a t e   ( e . g . ,   ` D E T E C T E D ` ,   ` E X E C U T I N G ` ) .  
 -   ` o u t c o m e _ t y p e ` :   T e r m i n a l   b u s i n e s s   o u t c o m e   ( e . g . ,   ` R E C O V E R E D ` ) .  
 -   ` v e r s i o n ` :   O p t i m i s t i c   c o n c u r r e n c y   t o k e n   ( ` i n t ` ) .  
 T h e r e   i s   n o   a m b i g u i t y .   T h e s e   f i e l d s   w o r k   i n   t a n d e m   w i t h o u t   r e d u n d a n c y .  
  
 # # #   2 .   U N K N O W N   S e m a n t i c s  
 T h e   t e r m   ` U N K N O W N `   a p p e a r s   i n   t h r e e   d i s t i n c t   c o n t e x t s ,   e a c h   w i t h   p r e c i s e   s e m a n t i c   b o u n d a r i e s   a n d   d i s t i n c t   o w n e r s :  
 |   C o n c e p t   |   M e a n i n g   |   O w n e r   |   W h e n   U s e d   |  
 |   - - -   |   - - -   |   - - -   |   - - -   |  
 |   * * W o r k f l o w   S t a t e   U n k n o w n * *   ( ` C a s e W o r k f l o w S t a t e . U N K N O W N ` )   |   T h e   s y s t e m   i s   a c t i v e l y   t r a c k i n g   a n   a m b i g u o u s   e x t e r n a l   s i t u a t i o n   ( e . g . ,   w a i t i n g   o u t   a   w e b h o o k   d e l a y   a f t e r   e x e c u t i o n ) .   T h e   w o r k f l o w   i s   a l i v e   a n d   w a i t i n g .   |   ` R e c o v e r y C a s e . w o r k f l o w _ s t a t e `   |   C a s e   i s   ` O P E N ` .   A c t i v e   r e c o v e r y   w o r k f l o w   i s   b l o c k e d   o n   a m b i g u i t y .   |  
 |   * * E x t e r n a l   V e r i f i c a t i o n   U n k n o w n * *   ( ` V e r i f i e d S t a t e . U N K N O W N ` )   |   A   s p e c i f i c   v e r i f i c a t i o n   c h e c k   a g a i n s t   a n   e x t e r n a l   p r o v i d e r   ( e . g . ,   R a z o r p a y )   r e s u l t e d   i n   a   t i m e o u t   o r   a m b i g u o u s   r e s p o n s e .   |   ` V e r i f i c a t i o n R e c o r d . v e r i f i e d _ s t a t e `   |   W h e n   a   v e r i f i c a t i o n   p o l l i n g   a t t e m p t   f a i l s   t o   p r o v e   s u c c e s s   o r   f a i l u r e .   |  
 |   * * F i n a l   R e c o v e r y   O u t c o m e   U n k n o w n * *   ( ` R e c o v e r y O u t c o m e V a l u e . U N K N O W N ` )   |   T h e   b u s i n e s s   d e f i n i t i v e l y   a b a n d o n e d   t h e   c a s e   w i t h o u t   e v e r   c o n f i r m i n g   t h e   f i n a n c i a l   o u t c o m e .   |   ` R e c o v e r y C a s e . o u t c o m e _ t y p e `   |   C a s e   i s   ` C L O S E D ` .   T h e   t e r m i n a l   c o n c l u s i o n   i s   t h a t   t h e   o u t c o m e   w i l l   p e r m a n e n t l y   r e m a i n   a   m y s t e r y .   |  
  
 # # #   3 .   T e r m i n a l   S t a t e   S e m a n t i c s  
 W o r k f l o w   s t a t e s   a r e   e x p l i c i t l y   c l a s s i f i e d :  
 -   * * N o n - T e r m i n a l   W o r k f l o w   S t a t e s : * *   ` D E T E C T E D ` ,   ` E N R I C H I N G ` ,   ` A S S E S S E D ` ,   ` P L A N N I N G ` ,   ` P O L I C Y _ R E V I E W ` ,   ` W A I T I N G _ A P P R O V A L ` ,   ` E X E C U T I N G ` ,   ` V E R I F Y I N G ` ,   ` U N K N O W N ` .  
 -   * * T e r m i n a l   W o r k f l o w   S t a t e : * *   ` C L O S E D ` .  
  
 W h e n   a   c a s e   r e a c h e s   a   t e r m i n a l   c o n c l u s i o n ,   t h e   r e l a t i o n s h i p   i s   e x a c t l y :  
 ` w o r k f l o w _ s t a t e = C L O S E D `   +   ` s t a t u s = C L O S E D `   +   ` o u t c o m e _ t y p e = ( T e r m i n a l   O u t c o m e ) `  
  
 E x a m p l e s   o f   l e g a l   t e r m i n a l   c o m b i n a t i o n s :  
 -   ` C L O S E D `   ( W o r k f l o w )   +   ` C L O S E D `   ( S t a t u s )   +   ` R E C O V E R E D `   ( O u t c o m e )  
 -   ` C L O S E D `   ( W o r k f l o w )   +   ` C L O S E D `   ( S t a t u s )   +   ` N O T _ R E C O V E R E D `   ( O u t c o m e )  
 -   ` C L O S E D `   ( W o r k f l o w )   +   ` C L O S E D `   ( S t a t u s )   +   ` S U P P R E S S E D `   ( O u t c o m e )  
 -   ` C L O S E D `   ( W o r k f l o w )   +   ` C L O S E D `   ( S t a t u s )   +   ` E S C A L A T E D `   ( O u t c o m e )  
 -   ` C L O S E D `   ( W o r k f l o w )   +   ` C L O S E D `   ( S t a t u s )   +   ` E X P I R E D `   ( O u t c o m e )  
 -   ` C L O S E D `   ( W o r k f l o w )   +   ` C L O S E D `   ( S t a t u s )   +   ` U N K N O W N `   ( O u t c o m e )  
  
 * ( N o t e :   T o   p e r f e c t l y   s a t i s f y   t h i s   m o d e l ,   t h e   ` C L O S E D `   s t a t e   i s   c o n s i d e r e d   t h e   t e r m i n a l   m e m b e r   o f   ` C a s e W o r k f l o w S t a t e ` ,   e n s u r i n g   t h e   w o r k f l o w   s t a t e   m a c h i n e   g r a c e f u l l y   p a r k s   i t s e l f   w h e n   t h e   b u s i n e s s   c o n t a i n e r   c l o s e s ) . *  
  
 # # #   4 .   M i g r a t i o n   M a p p i n g  
 E x i s t i n g   c a s e s   i n   P 0 2 / P 0 3   w i l l   b e   m a p p e d   d e t e r m i n i s t i c a l l y .   S i n c e   P 0 2 / P 0 3   d i d   n o t   p e r s i s t   p r e - e x e c u t i o n   s t a t e s   ( ` E N R I C H I N G ` ,   ` P L A N N I N G ` ,   ` W A I T I N G _ A P P R O V A L ` ) ,   n o   e x i s t i n g   c a s e s   c a n   p o s s i b l y   o c c u p y   t h e m .   T h e y   w i l l   s a f e l y   s n a p   t o   t h e   c l o s e s t   d u r a b l e   b o u n d a r y .  
  
 |   E x i s t i n g   C a s e   F a c t s   |   ` w o r k f l o w _ s t a t e `   a f t e r   m i g r a t i o n   |   ` o u t c o m e _ t y p e `   |   ` s t a t u s `   |  
 |   - - -   |   - - -   |   - - -   |   - - -   |  
 |   ` s t a t u s = C L O S E D ` ,   ` o u t c o m e _ t y p e = R E C O V E R E D `   |   ` C L O S E D `   |   ` R E C O V E R E D `   |   ` C L O S E D `   |  
 |   ` s t a t u s = C L O S E D ` ,   ` o u t c o m e _ t y p e = S U P P R E S S E D `   |   ` C L O S E D `   |   ` S U P P R E S S E D `   |   ` C L O S E D `   |  
 |   ` s t a t u s = O P E N ` ,   ` A c t i o n `   i s   ` V E R I F I C A T I O N _ P E N D I N G `   |   ` V E R I F Y I N G `   |   ` N o n e `   |   ` O P E N `   |  
 |   ` s t a t u s = O P E N ` ,   ` A c t i o n `   i s   ` E X E C U T I O N _ U N K N O W N `   |   ` U N K N O W N `   |   ` N o n e `   |   ` O P E N `   |  
 |   ` s t a t u s = O P E N ` ,   ` A c t i o n `   i s   ` E X E C U T I N G `   |   ` E X E C U T I N G `   |   ` N o n e `   |   ` O P E N `   |  
 |   ` s t a t u s = O P E N ` ,   ` A c t i o n `   i s   ` P R O P O S E D `   |   ` P O L I C Y _ R E V I E W `   |   ` N o n e `   |   ` O P E N `   |  
 |   ` s t a t u s = O P E N ` ,   ` I n t e r v e n t i o n P l a n `   e x i s t s   |   ` P O L I C Y _ R E V I E W `   |   ` N o n e `   |   ` O P E N `   |  
 |   ` s t a t u s = O P E N ` ,   ` R i s k A s s e s s m e n t `   e x i s t s   |   ` A S S E S S E D `   |   ` N o n e `   |   ` O P E N `   |  
 |   ` s t a t u s = O P E N ` ,   O n l y   ` R e v e n u e E v e n t `   e x i s t s   |   ` D E T E C T E D `   |   ` N o n e `   |   ` O P E N `   |  
  
 * * A m b i g u i t y : * *   N o n e .   T h i s   i s   a   s t r i c t l y   d e t e r m i n i s t i c   h i e r a r c h y   b a s e d   o n   t h e   h i g h e s t - o r d e r   a r t i f a c t   p r e s e n t .  
  
 # # #   5 .   C o n c u r r e n c y   S e m a n t i c s  
 T h e   ` R e c o v e r y C a s e . v e r s i o n `   t o k e n   p r o v i d e s   o p t i m i s t i c   c o n c u r r e n c y :  
 -   * * I n i t i a l   v a l u e : * *   ` 0 `   ( a s s i g n e d   u p o n   c a s e   c r e a t i o n ) .  
 -   * * I n c r e m e n t   b e h a v i o r : * *   ` v e r s i o n   =   v e r s i o n   +   1 `   a t o m i c a l l y   o n   e v e r y   ` R e c o v e r y C a s e `   u p d a t e .  
 -   * * S t a l e - w r i t e   b e h a v i o r : * *   ` U P D A T E   r e c o v e r y _ c a s e s   S E T   . . . ,   v e r s i o n   =   v e r s i o n   +   1   W H E R E   c a s e _ i d   =   ?   A N D   v e r s i o n   =   ? ` .   I f   r o w s   a f f e c t e d   = =   0 ,   t h e   w r i t e   i s   s t a l e .  
 -   * * C o n f l i c t   b e h a v i o r : * *   A n   e x p l i c i t   d o m a i n   e x c e p t i o n   ( e . g . ,   ` S t a l e S t a t e T r a n s i t i o n E r r o r ` )   i s   r a i s e d .   T h e   c u r r e n t   P 0 3   t r a n s a c t i o n   i s   a b o r t e d   a n d   r o l l e d   b a c k .   T h e   w o r k e r / w e b h o o k   s a f e l y   d i s c a r d s   i t s   w o r k   a n d   c a n   r e t r y   b y   f e t c h i n g   t h e   l a t e s t   s t a t e .  
 -   * * T r a n s a c t i o n   b o u n d a r y : * *   T h e   v e r s i o n   i n c r e m e n t   a n d   a l l   r e l a t e d   s t a t e   t r a n s i t i o n s   ( e . g . ,   u p d a t i n g   ` R e c o v e r y A c t i o n . s t a t u s ` )   m u s t   o c c u r   s t r i c t l y   w i t h i n   t h e   s a m e   P 0 3   ` T r a n s a c t i o n M a n a g e r `   t r a n s a c t i o n .  
  
 # # #   6 .   D o m a i n   O w n e r s h i p  
 -   ` C a s e W o r k f l o w S t a t e `   b e l o n g s   s t r i c t l y   t o   * * P 0 2   ( D o m a i n   M o d e l ) * * .   I t   d e f i n e s   t h e   v o c a b u l a r y   o f   t h e   b u s i n e s s   p r o c e s s .  
 -   I t   d o e s   N O T   b e l o n g   t o   p e r s i s t e n c e   ( w h i c h   m e r e l y   m a p s   i t   t o   T E X T )   o r   t h e   s t a t e - m a c h i n e   a p p l i c a t i o n   s e r v i c e   ( w h i c h   e n f o r c e s   t h e   r u l e s   b u t   d o e s   n o t   o w n   t h e   v o c a b u l a r y ) .  
  
 # # #   7 .   P a c k a g e   B o u n d a r i e s  
 -   * * P 0 2   ( D o m a i n ) : * *   O w n s   t h e   ` C a s e W o r k f l o w S t a t e `   e n u m ,   ` R e c o v e r y C a s e . w o r k f l o w _ s t a t e ` ,   a n d   ` R e c o v e r y C a s e . v e r s i o n `   f i e l d s .   V a l i d a t e s   i n t r i n s i c   t y p e s .  
 -   * * P 0 3   ( P e r s i s t e n c e ) : * *   O w n s   t h e   ` 0 0 2 _ a d d _ w o r k f l o w _ s t a t e . s q l `   s c h e m a   m i g r a t i o n ,   S Q L i t e   ` U P D A T E `   c o n c u r r e n c y   l o g i c ,   a n d   d a t a   m a p p e r s .  
 -   * * P 0 5   ( S t a t e   M a c h i n e ) : * *   O w n s   t h e   t r a n s i t i o n   l o g i c   ( ` e n g i n e . p y ` ) .   E v a l u a t e s   t h e   l e g a l   g r a p h ,   o r c h e s t r a t e s   t h e   P 0 3   t r a n s a c t i o n ,   a n d   h a n d l e s   ` S t a l e S t a t e T r a n s i t i o n E r r o r `   a p p r o p r i a t e l y .  
 