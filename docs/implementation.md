# Current Implementation

This describes the repository implementation after Compatibility Restoration Phase 1. The immutable Workshop snapshot describes the previously published payload.

## Important Source Files

- `mod/init.script`: canonical-state migration, BTC price restoration, mining worker, hub finalization, rig NPC/object spawning, and collection handoff.
- `mod/scripts/item.script`: GPU, BTC, and BTC USB definitions; loot tables; trader stock; recipes.
- `mod/scripts/rig.script`: `miner_0` through `miner_10`, sprites, values, weights, and sequential recipes.
- `mod/scripts/chest.script`: `bitcoin_chest` and bunker/ready sprites.
- `mod/sprite/`: item, rig, ready-rig, and chest artwork.
- `mod/meta.ini`: version `v1.0.1`, Workshop ID, and author ID.

## Important Flows and Event Hooks

### Initialization and migration

Executes the item/rig/chest scripts and registers objects and hooks. It does not touch FileData: the official documentation says `init` runs when the mod first loads, while FileData belongs to the save that is loaded later.

Every `enter_hub` (documented to fire on new game, save load, and raid return) first runs `gpu_mining_initialize_state()` and reapplies the saved BTC price. The worker step also initializes state if the version key is still missing, in case it runs before `enter_hub`. On the first canonical initialization of a save only, compatible values are migrated from the published legacy keys; later calls only normalize canonical values. Legacy keys are retained but are not used by new runtime behavior.

Shared constants and helper functions are assigned as Catspeak globals (no top-level `let`). The game embeds Catspeak 3, whose callbacks have their own local scope and no closure support was found in the runtime, so a top-level `let` read inside an event or object callback would not resolve to the script value. The published implementation used the same global-function pattern for its NPC lookup. `tools/static_check.py` guards this rule and the core invariants.

The mod registers `player_spawn` to create `gpu_mining_3485717804_worker`, a mod-owned, non-solid worker object spawned at `(0, 0)`. Its `step_normal_event` owns mining progress and has no player-position dependency. The published implementation previously assigned `obj_player.step_normal_event`; the restored implementation no longer does.

### Rig discovery and upgrading

`miner_0` can drop from `electronic_box`. Each next tier consumes the previous rig and one `gpu`; tiers 1–3, 4–6, and 7–10 use progressively higher crafting categories. The worker scans `miner_10` down through `miner_0`, records that a Rig has been seen, and only raises the historical maximum level. When the maximum rises, the superseded tier's item sprites are reset to normal, as the published upgrade check did.

The detected physical level and active mining level are deliberately distinct. During Phase 1, active mining continues to use the historical maximum to preserve published-save and possible stash behavior. Losing or selling the physical Rig can therefore leave mining active, matching the old effective state model.

### Mining and price update

While the historical maximum Rig level is above zero, the worker increments canonical progress once per worker normal step, capped at 162,000. On `enter_hub`, 162,000 steps marks output equal to the active level, resets progress, randomizes BTC price from 100,000 to 400,000, saves it, and applies it immediately. To avoid inventing an unsupported collection transition, the published lower-progress Hub behavior still clears ready output.

### Collection workaround

On Hub entry, a `bitcoin_npc` copied from `trader_faction1` and `btc_obj` appear at `(320, 900)` when a Rig has been seen. The object updates ready sprites. After a short instance-local step counter, it configures `bitcoin_chest`, kills the NPC, and relies on its dropped chest to expose mined BTC. `btc_inst` is explicitly initialized, and if the NPC is not visible when the object is created the lookup is retried each step until found instead of stalling permanently. Spawn status and kill delay are no longer persisted. The chest is configured even when pending BTC is `0`, as in the published payload, so a Hub visit without a completed cycle produces an empty "Mined Bitcoin" chest.

### BTC risk choice

BTC uses the persisted dynamic value, which is restored explicitly after item creation on every load. The recipe `1 btc + 1 usb -> 1 btc_usb` converts it to a fixed 250,000₽ item.

## Intent / Invariant Mapping

| Intent or invariant | Implementation mechanism |
| --- | --- |
| Inventory/stash rig | Rig tiers are barter items, not base modules |
| Active-play progress | Mod-owned worker increments namespaced progress |
| Higher tier yields more | Pending BTC is assigned the historical maximum Rig level; chest count uses that value |
| Cycle-based volatile price | `RandomRange(100000, 400000)` on hub finalization |
| Fixed-value risk control | BTC USB recipe and 250,000₽ item value |
| Visible ready state | Separate `rig ... btc` and `rig chest ... btc` sprites |

## State and Persistence

Canonical `FileDataRead`/`FileDataWrite` keys use Real values:

- `gpu_mining_3485717804_state_version`
- `gpu_mining_3485717804_progress_steps` (`0..162000`)
- `gpu_mining_3485717804_rig_seen` (`0` or `1`)
- `gpu_mining_3485717804_max_rig_level` (`0..10`)
- `gpu_mining_3485717804_pending_btc` (`0..10`)
- `gpu_mining_3485717804_btc_price` (`100000..400000`)

On first initialization, defined `Time BTC`, `Rig level`, and `Rig has` values are rounded and clamped to their supported ranges. `Rig made` sets the canonical flag only when it equals `true` or `1`, and a positive migrated Rig level also sets that flag. An in-range `btc price` is rounded; otherwise the minimum default remains. This is key-specific normalization, not general type validation. Canonical state wins after the version key exists. On later canonical loads, `rig_seen` is normalized to numeric `0` or `1`, and a positive normalized `max_rig_level` forces it to `1` without fabricating a Rig level. The migration cannot recover pending BTC already erased by the published implementation. `Time BTC kill`, `Bitcoin NPC spawned`, `Bitcoin OBJ spawned`, and `btc log` are not migrated or used.

## Vanilla Dependencies

- Objects/templates: `obj_npc_human_parent`, `trader_faction1`
- Loot containers/enemies: `electronic_box`, `cabinet`, `bag`, `safe`, `bandit_boss_valentin`, `killa`
- Trader: `bar`
- Recipe ingredients and crafting categories listed in `item.script`/`rig.script`
- Item, chest, NPC, object, sprite, inventory, event, file-data, crafting, and trader APIs

## Custom IDs

- Items: `gpu`, `btc`, `btc_usb`, `miner_0` … `miner_10`
- Chest: `bitcoin_chest`
- NPC/object: `bitcoin_npc`, `btc_obj`, `gpu_mining_3485717804_worker`
- Numerous sprite names such as `gpu sprite`, `rig 10 btc`, and `rig chest 10 btc`
- Persistence keys listed above

## Cross-Mod Collision Surfaces

- Published item/object IDs such as `gpu`, `btc`, and `btc_obj` remain non-namespaced for compatibility.
- Persistent state and the mining worker are namespaced with Workshop ID `3485717804`.
- The direct `obj_player.step_normal_event` collision has been removed; `player_spawn` remains a shared event-hook surface whose composition semantics require runtime verification.
- Loot tables, Barman stock, item prices, and crafting lists are shared surfaces.
- The bunker coordinates and copied faction trader NPC may conflict with other spawned content.

## Legacy / Workaround Mechanisms

- Mining output is exposed by spawning and killing an NPC so its configured chest drops.
- Sprites and the temporary `btc_obj` bridge inventory state and the bunker representation.

## Known Implementation Debt

- The lookup reads the undocumented `npc_name` instance variable and kills via undocumented `hp`; the October 2026 AI rewrite could change either.
- `bitcoin_npc` is copied from `trader_faction1` without a preceding `NpcCreate`, unlike the documented sequence and the Legendary Merchant restoration; this is published behavior and is left unchanged pending runtime evidence.
- `FileDataRead` documentation says a missing key returns "an empty struct" while its own example tests for `undefined`; the code follows the example and the published implementation.

- Frame/step counting assumes a stable update cadence and remains intentionally unchanged at 162,000 steps.
- Worker lifetime and duplicate behavior across room/player lifecycles require Windows verification.
- The inventory API's stash coverage is undocumented, so historical maximum remains the active level.
- Pending BTC can still be lost on a later Hub entry/load with incomplete progress because reliable chest-collection acknowledgement remains unresolved. This is the main remaining runtime blocker.
- The NPC-kill chest handoff remains technical debt because the current API documents chest configuration but no direct chest spawn or collection callback.
