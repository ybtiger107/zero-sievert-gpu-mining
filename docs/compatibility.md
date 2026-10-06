# Compatibility Audit

Static audit snapshot: 2026-10-06. No Windows runtime result is claimed.

## Verified Compatible (Static)

- Repository `mod/` matches the captured installed Workshop payload.
- Referenced vanilla containers, bosses, trader, NPC template, ingredients, and core objects are present in captured current game data.
- All referenced PNG assets exist in the published payload.

## Verified Incompatible

None established by static evidence alone.

## Suspicious / Needs Investigation

- A user reported “Crash with new version” on 2026-09-16; no stack trace or author response was visible.
- Replacing `obj_player.step_normal_event` is a high-risk compatibility surface.
- `btc_price` scope/restoration, spawn-flag transitions, ready-output clearing, and NPC-kill chest handoff need runtime validation.
- Users reported rigs becoming unpickable when dropped and mining not completing after the stated time.
- Global custom IDs and persistence keys can collide with other mods.

## Windows Runtime Test Required

- Clean load on the current game build and reproduction of the September 2026 crash report.
- Fresh save and existing save initialization, including re-entering the hub after first rig acquisition.
- All ten upgrades, stash/inventory detection, save/reload, raid time, bunker time, and exact cycle duration.
- BTC-ready sprite, output count by level, collection, repeated cycles, and price persistence.
- BTC USB conversion and fixed value.
- Dropped-rig recovery and safe failure behavior.
- Mixed-mod tests with mods that alter `obj_player`, items, crafting, loot, traders, or bunker spawns.

## Cross-Mod Compatibility Risks

- Player step script replacement is the largest risk.
- Non-namespaced item, object, NPC, chest, sprite, and file-data identifiers.
- Shared loot tables and Bar trader stock.
- Fixed bunker coordinates and copied NPC template.

## Content / Update Debt

- Decide whether mining should remain frame-based active play or use in-game days; a user requested the latter.
- Preserve the historical 45-minute nominal behavior until a deliberate balance decision is made.
- Replace the dropped-NPC chest workaround only if collection semantics and output persistence remain intact.
- Record the tested ZERO Sievert build after Windows validation.
