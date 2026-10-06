# Current Implementation

This describes the currently published Workshop payload, which matches `mod/` in this repository.

## Important Source Files

- `mod/init.script`: state initialization, mining timer, hub finalization, player-step override, rig NPC/object spawning, and collection handoff.
- `mod/scripts/item.script`: GPU, BTC, and BTC USB definitions; loot tables; trader stock; recipes.
- `mod/scripts/rig.script`: `miner_0` through `miner_10`, sprites, values, weights, and sequential recipes.
- `mod/scripts/chest.script`: `bitcoin_chest` and bunker/ready sprites.
- `mod/sprite/`: item, rig, ready-rig, and chest artwork.
- `mod/meta.ini`: version `v1.0.1`, Workshop ID, and author ID.

## Important Flows and Event Hooks

### Initialization

Creates a fallback `global`, defines NPC-instance lookup helpers, executes the item/rig/chest scripts, registers `enter_hub`, overrides `obj_player`'s `step_normal_event`, then creates the rig NPC and `btc_obj`.

### Rig discovery and upgrading

`miner_0` can drop from `electronic_box`. Each next tier consumes the previous rig and one `gpu`; tiers 1–3, 4–6, and 7–10 use progressively higher crafting categories. The player-step loop scans inventory from level 1 to 10 and persists the highest detected level.

### Mining and price update

While persisted rig level is above zero, `Time BTC` increments once per player normal step. On `enter_hub`, a value of at least `60 * 60 * 45` marks output equal to rig level, resets the timer, randomizes BTC price from 100,000 to 400,000, and applies it. A lower timer clears ready output.

### Collection workaround

Spawn flags cause a `bitcoin_npc` copied from `trader_faction1` and then `btc_obj` to appear at `(320, 900)`. The object updates ready sprites. After a short step counter, it configures `bitcoin_chest`, kills the NPC, and relies on its dropped chest to expose mined BTC.

### BTC risk choice

BTC uses the persisted dynamic value. The recipe `1 btc + 1 usb -> 1 btc_usb` converts it to a fixed 250,000₽ item.

## Intent / Invariant Mapping

| Intent or invariant | Implementation mechanism |
| --- | --- |
| Inventory/stash rig | Rig tiers are barter items, not base modules |
| Active-play progress | Player `step_normal_event` increments `Time BTC` |
| Higher tier yields more | `Rig has` is assigned `Rig level`; chest count uses that value |
| Cycle-based volatile price | `RandomRange(100000, 400000)` on hub finalization |
| Fixed-value risk control | BTC USB recipe and 250,000₽ item value |
| Visible ready state | Separate `rig ... btc` and `rig chest ... btc` sprites |

## State and Persistence

`FileDataRead`/`FileDataWrite` keys:

- `Time BTC`
- `Rig level`
- `Rig made`
- `Rig has`
- `btc price`
- `Time BTC kill`
- `Bitcoin NPC spawned`
- `Bitcoin OBJ spawned`
- `btc log` (cleared, otherwise unused in captured code)

## Vanilla Dependencies

- Objects/templates: `obj_player`, `obj_npc_human_parent`, `trader_faction1`
- Loot containers/enemies: `electronic_box`, `cabinet`, `bag`, `safe`, `bandit_boss_valentin`, `killa`
- Trader: `bar`
- Recipe ingredients and crafting categories listed in `item.script`/`rig.script`
- Item, chest, NPC, object, sprite, inventory, event, file-data, crafting, and trader APIs

## Custom IDs

- Items: `gpu`, `btc`, `btc_usb`, `miner_0` … `miner_10`
- Chest: `bitcoin_chest`
- NPC/object: `bitcoin_npc`, `btc_obj`
- Numerous sprite names such as `gpu sprite`, `rig 10 btc`, and `rig chest 10 btc`
- Persistence keys listed above

## Cross-Mod Collision Surfaces

- Generic global IDs (`gpu`, `btc`, `btc_obj`) and persistence keys are not namespaced.
- `ObjectSetScript("obj_player", "step_normal_event", ...)` can replace or be replaced by another mod's player-step script.
- Loot tables, Barman stock, item prices, and crafting lists are shared surfaces.
- The bunker coordinates and copied faction trader NPC may conflict with other spawned content.

## Legacy / Workaround Mechanisms

- `_ObjectGetAllInstances`/`FindNpcInstance` is credited in source as derived from a vending-machine mod.
- Mining output is exposed by spawning and killing an NPC so its configured chest drops.
- Sprite and spawn flags bridge transitions between inventory state and the bunker representation.

## Known Implementation Debt

- Frame/step counting assumes a stable update cadence and is harder to reason about than elapsed game time.
- `btc_price` is local in the hub callback but referenced in the player-step callback without a local read; verify Catspeak scoping and price restoration.
- Hub logic sets existing spawn flags to `true`, a non-obvious state transition that needs runtime coverage.
- `Rig made` is set by seeing `miner_0`; behavior when an upgraded rig exists without the base tier needs verification.
- Ready output is cleared on hub entry when the threshold is not met, matching the historical disappearance warning but creating loss risk.
- Source contains an unused/cleared `btc log` key and duplicate semicolon.
