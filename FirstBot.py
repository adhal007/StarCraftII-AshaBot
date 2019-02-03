import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE
## producing more workers
## We just need a nexus for producing workers
## reference a nexus

class SentdeBot(sc2.BotAI):
    async def on_step(self, iteration):
        # define an ansynchronous method
        # every step we get, what will we do
        await self.distribute_workers()
        #already defined
        await self.builder_workers()
        #doesnt exist yet

    async def builder_workers(self):
        for nexus in self.units(NEXUS).ready.noqueue:
            # Nexus must be ready
            # no queue - nothing else in the queue
            if self.can_afford(PROBE):
                ## inherited probe
                await self.do(nexus.train(PROBE))

                
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Protoss, SentdeBot()), Computer(Race.Terran, Difficulty.Easy)], realtime=True)
# specify where - which map
# player list
# run-speed -T - nomral speed, F = ultra fast
