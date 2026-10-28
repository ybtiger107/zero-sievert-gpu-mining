# Compatibility Audit

Static audit updated for Compatibility Restoration Phase 1 on 2026-10-06 and re-audited on 2026-10-28. No Windows runtime result is claimed.

## Game Baseline

- Last statically inspected build: `25269476` (`_game-baseline/steamapps/appmanifest_1782120.acf`, installed 2026-10-06), with its bundled Modding Documentation and Catspeak 3 runtime.
- Released after that baseline: "Completely New Enemy AI Is Here" (2026-10-16) and "New Update: Improved Enemy AI" (2026-10-27), per the Steam news feed. The fetched announcement excerpts mention no modding API change; that is not proof the API is unchanged. Builds `25883465` and `26249078` are recorded by SteamDB but were not installed locally.
- Refreshing requires an owned-account SteamCMD download into a new directory (the current baseline must be kept), then diffing `Modding Documentation/`, `exposed_values.txt`, and `ZS_vanilla/gamedata/`.

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
| GM-1 | P0 (likely) | `mod/init.script` constants/helpers | Top-level `let` values and helpers were read inside event/object callbacks. The embedded Catspeak 3 runtime has local/global expression nodes but no closure support, so callbacks would read undefined globals: state keys, threshold, and NPC lookup would all fail. | Restoration (`8f49357`) | Fixed: converted to globals; `tools/static_check.py` guards it |
| GM-2 | P1 | `mod/init.script` initialization | Canonical state was initialized and the BTC price applied only from `init`, which runs when the mod loads, not per save. Saves loaded later were never migrated or normalized, and switching saves in one session kept the wrong price. | Restoration (`8f49357`) | Fixed: per-save initialization on `enter_hub` plus a worker fallback |
| GM-3 | P2 | `btc_obj` create/step | `btc_inst` was unset when the first NPC lookup failed (an unset instance read), and the lookup was never retried, which stalled reward delivery (known issue 10). | Published | Fixed: explicit init and per-step retry |
| GM-4 | P3 | `gpu_mining_sync_rig_state` | Restoration dropped the published reset of the superseded tier's sprite, so a stale BTC-ready sprite could persist for that tier. | Restoration | Fixed |
| GM-5 | P1 | `enter_hub` pending clearing | Pending BTC is cleared by the next Hub entry with incomplete progress, including save load. Uncollected BTC can therefore be lost. This is the published anti-duplication behavior. | Published | Open: needs a collection acknowledgement (issue #2) |
| GM-6 | P2 | worker / `player_spawn` | Worker duplication and lifetime are unverified; a duplicate would multiply mining speed. | Restoration | Open: issue #1 |
| GM-7 | P2 | NPC lookup / kill | Depends on the undocumented `npc_name` and `hp` instance variables. The October AI rewrite is the main risk. | Published | Open: issues #2 and #3 |
| GM-8 | P2 | `InventoryItemExists` | Stash coverage is undocumented, so mining uses the historical maximum and continues after the Rig is lost. | Intentional compromise | Open: issue #4 |
| GM-9 | P3 | `bitcoin_npc` | `NpcCopy` is used without `NpcCreate`. | Published | Documented, unchanged |
| GM-10 | P3 | `FileDataRead` docs | The documentation says a missing key returns an empty struct, but its example checks for `undefined`. | Documentation | Runtime check in issue #3 |
| GM-11 | P3 | `mod/sprite/rig_chest_6_btc (1).png` | Unreferenced duplicate asset. | Published | Left unchanged (Workshop payload parity) |

Release readiness: not ready. Issues #1–#4 must pass on Windows on the current build first, with GM-1/GM-2 confirmed by a fresh-save test and a legacy-save test.
