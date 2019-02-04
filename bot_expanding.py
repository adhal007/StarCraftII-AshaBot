import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR
## producing more workers
## We just need a nexus for producing workers
## reference a nexus
#####  Tutorial II #####
# specify where - which map
# player list
# run-speed -T - nomral speed, F = ultra fast
# each pylon - increase your supplies
# each pylon builds the scionic tree
# building pylons and simulators
# each pylon adds to the scionic matrix
# scionic matrix helps to build more buildings
# need to optimise the pylon to not build one next to the
# other
# baseless to have more than 3 patch of workers for each
# mineral or we will exhaust our resources of workers
#### Tutorial III ##### Geysers and Expanding
# When to expand ? to 2 or 3 nexus areas


class SentdeBot(sc2.BotAI):
    async def on_step(self, iteration):
        # define an ansynchronous method
        # every step we get, what will we do
        await self.distribute_workers()
        #already defined
        await self.builder_workers()
        #doesnt exist yet
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()


    async def builder_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            # Nexus must be ready
            # no queue - nothing else in the queue
            if self.can_afford(PROBE):
                ## inherited probe
                await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        ## create some logic for resource management
        if self.supply_left < 5 and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    # specify build and where - location
                    await self.build(PYLON, near=nexuses.first)

    async def build_assimilators(self):
        for nexus in self.units(NEXUS).ready:
            ## find the vespian geysers
            vaspenes = self.state.vespene_geyser.closer_thann(25.0, nexus)
            for vaspene in vaspenes:
                if not self.can_afford(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(ASSIMILATOR, vaspene))

    async def expand(self):
        if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
            await self.expand_now()
        ## best situation will be to detect a soldier's rush or knight's rush
        ## by the enemy and then decide how many nexuses to expand

run_game(maps.get("AbyssalReefLE"), [Bot(Race.Protoss, SentdeBot()), Computer(Race.Terran, Difficulty.Easy)], realtime=False)
