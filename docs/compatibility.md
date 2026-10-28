# Compatibility Audit

Static audit updated for Compatibility Restoration Phase 1 on 2026-10-06 and re-audited on 2026-10-28. No Windows runtime result is claimed.

## Game Baseline

- Latest statically inspected baseline: Game 1.4.6, Mod API 3, Steam build `26249078` (`_game-baseline-2026-10-28/steamapps/appmanifest_1782120.acf`, installed 2026-10-28 01:48 UTC; `data.win` compiled 2026-10-27 16:46 UTC, matching the 2026-10-27 "Improved Enemy AI" update).
- Previous baseline, kept unchanged: build `25269476` (`_game-baseline/`, installed 2026-10-06; `data.win` compiled 2026-09-12). It predates the 2026-10-16 AI rewrite.
- Between the two builds, `exposed_values.txt` removed no API used here. Item, weapon, and trader data is unchanged; `npc.json`, `npc_preset.json`, and `chest.json` changed. The vanilla templates, containers, trader, and recipe ingredients this mod uses are still present.
- Mod API 3 documents that event, object, and timer callbacks cannot rely on variables defined outside themselves (Examples 31, 35, 40), that `ScriptGet` should be called inside the function that uses a helper (Example 40), that FileData is a per-mod store isolated by mod name, that `NpcCopy` creates its destination ID, and that `EventAssignFunction` keeps one callback per event per mod.

## Verified Compatible (Static)

- Referenced vanilla containers, bosses, trader, NPC template, ingredients, and core objects are present in captured current game data.
- All referenced PNG assets exist in the published payload.
- Current documentation supports the Phase 1 APIs used for custom objects, object scripts, `player_spawn`, inventory checks, file data, and NPC/chest configuration.

## Verified Incompatible

- The published implementation wrote Boolean values through `FileDataWrite`, whose documented value types are Real, String, Array, and Struct. Phase 1 replaces persisted flags with numeric `0/1` and moves runtime flags to instance state.
- The published player-step callback referenced `btc_price` outside the callback where it was declared. Phase 1 reads, validates, saves, and explicitly applies canonical price state.

## Suspicious / Needs Investigation

- A user reported “Crash with new version” on 2026-09-16; no stack trace or author response was visible.
- `player_spawn` callback composition and worker lifetime/duplication need runtime validation. The direct `obj_player.step_normal_event` assignment is removed.
- Ready-output clearing and the NPC-kill chest handoff still need runtime validation because collection acknowledgement is not documented.
- Users reported rigs becoming unpickable when dropped and mining not completing after the stated time.
- Published custom content IDs remain global for save/content compatibility; canonical persistence and the new worker are namespaced.

## Windows Runtime Test Required

- Clean load on the current game build and reproduction of the September 2026 crash report.
- Fresh save and existing-save migration, including numeric interpretation of legacy Boolean `Rig made` values.
- Worker count and lifecycle through hub, raids, room changes, death, reload, pause, and menus.
- Whether `InventoryItemExists` includes the stash.
- All ten upgrades, stash/inventory detection, save/reload, raid time, bunker time, and exact cycle duration.
- BTC-ready sprite, output count by level, collection, repeated cycles, and price persistence.
- Whether changing the item definition price updates already-owned BTC instances.
- BTC USB conversion and fixed value.
- Dropped-rig recovery and safe failure behavior.
- Mixed-mod tests with mods that alter `obj_player`, items, crafting, loot, traders, or bunker spawns.

## Cross-Mod Compatibility Risks

- The direct player-step replacement risk is removed.
- `player_spawn` is still a shared hook and its multi-mod registration semantics are undocumented.
- Non-namespaced published item, object, NPC, chest, and sprite identifiers; legacy FileData keys may remain in existing saves but are no longer written.
- New canonical FileData keys and worker ID are namespaced; published content IDs are intentionally unchanged in Phase 1.
- Shared loot tables and Bar trader stock.
- Fixed bunker coordinates and copied NPC template.

## Content / Update Debt

- Decide whether mining should remain frame-based active play or use in-game days; a user requested the latter.
- Preserve the historical 45-minute nominal behavior until a deliberate balance decision is made.
- Define a reliable `PENDING -> COLLECTED` transition only after chest collection can be observed without inventory-delta heuristics.
- Replace the dropped-NPC chest workaround only if collection semantics and output persistence remain intact.
- Record the tested ZERO Sievert build after Windows validation.

## 2026-10-28 Audit Findings

| ID | Severity | Location | Finding | Origin | Status |
| --- | --- | --- | --- | --- | --- |
| GM-1 | P0 (likely) | `mod/init.script` constants/helpers | Top-level `let` values and helpers were read inside event/object callbacks. Mod API 3 states that such callbacks cannot rely on outside variables. The first correction (`e26de03`) used plain Catspeak globals, which the same documentation does not guarantee either. | Restoration (`8f49357`); incomplete fix `e26de03` | Corrected statically: keys and constants are literals inside each function; helpers use namespaced `ScriptExpose` and are fetched with `ScriptGet` inside callbacks. Runtime confirmation pending (issue #3) |
| GM-2 | P3 | `mod/init.script` initialization | State was initialized and the BTC price applied only from top-level `init` code. Mod API 3 examples do read and write FileData from `init`, so the earlier claim that FileData is unavailable there is withdrawn. Initializing on `enter_hub` with a worker fallback is kept because it is idempotent and also covers whatever save-slot semantics FileData has. | Restoration (`8f49357`) | Kept as hardening; save-slot semantics unverified |
| GM-3 | P2 | `btc_obj` create/step | `btc_inst` was unset when the first NPC lookup failed (an unset instance read), and the lookup was never retried, which stalled reward delivery (known issue 10). | Published | Fixed: explicit init and per-step retry |
| GM-4 | P3 | rig-state sync helper | Restoration dropped the published reset of the superseded tier's sprite, so a stale BTC-ready sprite could persist for that tier. | Restoration | Fixed |
| GM-5 | P1 | `enter_hub` pending clearing | Pending BTC is cleared by the next Hub entry with incomplete progress, including save load. Uncollected BTC can therefore be lost. This is the published anti-duplication behavior. | Published | Open: needs a collection acknowledgement (issue #2) |
| GM-6 | P2 | worker / `player_spawn` | Worker duplication and lifetime are unverified; a duplicate would multiply mining speed. | Restoration | Open: issue #1 |
| GM-7 | P2 | NPC lookup / kill | Depends on the undocumented `npc_name` and `hp` instance variables. The October AI rewrite is the main risk. | Published | Open: issues #2 and #3 |
| GM-8 | P2 | `InventoryItemExists` | Stash coverage is undocumented, so mining uses the historical maximum and continues after the Rig is lost. | Intentional compromise | Open: issue #4 |
| GM-9 | — | `bitcoin_npc` | `NpcCopy` without `NpcCreate` is the correct Mod API 3 usage: `NpcCopy` creates the destination ID, which must be new. | Published | No change needed |
| GM-10 | — | `FileDataRead` docs | Mod API 3 now states that a missing key returns `undefined` when no default is given, which matches the code. | Documentation | Resolved by documentation |
| GM-12 | P2 | FileData scope | Mod API 3 isolates FileData by mod name. Whether legacy keys written by the published mod under older builds are still visible, and whether the store is per save slot, is not documented. If they are not visible, legacy saves migrate to defaults. The `meta.ini` name `GPU Mining System` must not change. | External change | Open: legacy-save test (issue #3) |
| GM-11 | P3 | `mod/sprite/rig_chest_6_btc (1).png` | Unreferenced duplicate asset. | Published | Left unchanged (Workshop payload parity) |

Release readiness: not ready. The static corrections are complete and the payload is ready for Windows runtime testing on build `26249078`. Issues #1–#4 must pass first, including a fresh save, a save from the published `v1.0.1` (GM-1, GM-12), and two save slots in one session.

`python3 tools/static_check.py` rejects the original top-level `let` captures, the plain-global variant, `ScriptGet` names without a matching earlier `ScriptExpose`, `NpcCopy` onto an ID already created by `NpcCreate`, and drift in core invariants. It is a string-level check, not proof of Catspeak runtime behavior.
