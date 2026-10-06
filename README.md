# GPU Mining System

## Concept

Add a long-term, risk-based cryptocurrency economy built around finding a rare mining rig, upgrading it with GPUs, waiting through active play, and choosing when to sell or lock in Bitcoin value.

## Sales Points

- Adds a passive progression loop alongside raids and ordinary bunker activity.
- Turns rare electronics into a ten-level upgrade path.
- Combines uncertain BTC prices with a fixed-value USB conversion choice.
- Provides visible rig states and a bunker collection point.

## Intended Player Experience

The player searches for scarce hardware, commits money and materials to upgrades, lets the rig progress during normal play, and periodically collects BTC. The reward is intentionally slow and uncertain: higher rig levels increase output, while price volatility and the fixed-value USB create a risk decision.

## Gameplay / Functional Loop

1. Loot a Mining Rig from an electronics chest and keep it in inventory or stash.
2. Find, buy, or craft GPUs.
3. Upgrade `miner_0` through ten sequential rig levels at the crafting table.
4. Accumulate a mining cycle during active gameplay.
5. Re-enter the hub to finalize the cycle, then collect BTC from the bunker rig/chest interaction.
6. Sell BTC at its current variable value or craft one BTC plus one USB into a fixed-value BTC USB.

## Core Features

- Mining Rig items from level 0 through 10.
- GPU, BTC, and BTC USB items, recipes, loot, values, and sprites.
- Persistent mining time, rig level, ready output, spawn flags, and BTC price.
- Dynamic BTC price between 100,000₽ and 400,000₽ after a completed cycle.
- BTC USB fixed at 250,000₽.
- Bunker visual and loot feedback when BTC is ready.

## Core Invariants

- The Mining Rig is an inventory/stash item, not a hideout module.
- Progress requires an active upgraded rig and accumulated active play; offline real time is not promised.
- Higher rig level yields more BTC per completed cycle.
- BTC price changes only at cycle completion and remains stable until the next cycle.
- BTC USB trades upside for a fixed value; it is a risk-control choice, not always the most profitable choice.
- Hardware and direct BTC drops remain rare enough to support a long-term progression loop.
- Dropping the rig on the ground is unsupported until its pick-up behavior is made safe.

## Balance and Progression

The published implementation uses ten GPU upgrades, a nominal 45-minute cycle, output equal to rig level, rare loot chances, a 2,000,000₽ GPU value, variable BTC, and a 250,000₽ BTC USB. These numbers are balance choices and may be tuned after compatibility is restored.

## Current Implementation Summary

The mod creates its items, recipes, loot entries, rig tiers, sprites, and a special BTC chest. File-backed state is updated through `enter_hub` and a custom player step script; a temporary NPC is killed to materialize the loot chest. See [docs/implementation.md](docs/implementation.md).

## Known Limitations

- The rig can become unpickable or be lost if dropped; keep it in inventory/stash.
- Newly obtained rigs may require leaving and re-entering the hub before interaction initializes.
- BTC should be collected before another status transition; the historical page warns it may disappear.
- The system uses frame/step counting and a complex NPC/object workaround rather than a dedicated timer and persistent container.
- A public “Crash with new version” report dated 2026-09-16 remains unreproduced.

## Compatibility

The published payload matches this repository. Static dependencies and vanilla loot/trader IDs are present in the captured current game data, but the player-step override, global custom IDs, persistence transitions, and current crash report require Windows testing. See [docs/compatibility.md](docs/compatibility.md).

## Current Milestone

**Compatibility Restoration** — restore the intended published behavior on the current ZERO Sievert version before redesigning or expanding features.

## Future Direction

- **Compatibility Hardening:** stabilize load, persistence, timing, collection, dropped-item behavior, and coexistence with other player/item script mods.
- **Feature Evolution:** consider in-game-day timing, safer rig representation, and balance tuning only after the published loop works reliably.

## Steam Workshop

- Workshop ID: `3485717804`
- [Steam Workshop page](https://steamcommunity.com/sharedfiles/filedetails/?id=3485717804)
- [Immutable Workshop snapshot](docs/reference/workshop/2026-10-06/metadata.md)
- [Workshop documentation index](WORKSHOP.md)
