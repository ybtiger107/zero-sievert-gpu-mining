# Compatibility Audit

Static audit updated for Compatibility Restoration Phase 1 on 2026-10-06. No Windows runtime result is claimed.

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
