import sc2, random
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, CYBERNETICSCORE, STALKER
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
#### Tutorial IV ##### Building an Army
## build a gateway for stalker
## build dynamic units with the stalker
#### Tutorial V ####
#### commanding your army strategy
#### send if more than 3 stalkers
#### attack to worker ratio
#### DPS/health - build more attacker units

#### Tutorial VI ####

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
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()

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
            ## find the vespian geysers 15.0 is  a good distance than 25
            vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
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
        ## Goal of resource areas = 2

    async def offensive_force_buildings(self):
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            ## only grab the pylon, build cyberneticscore as soon as you have gateway
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                # either build a stalker or cyberneticscore
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                    await self.build(CYBERNETICSCORE, near=pylon)
            elif len(self.units(GATEWAY)) < 3:
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)

    async def build_offensive_force(self):
        # build stalkers and not too many units
        # workers might get in the way
        for gw in  self.units(GATEWAY).ready.noqueue:
            if self.can_afford(STALKER) and self.supply_left > 0:
                await self.do(gw.train(STALKER))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_location[0]

    async def attack(self):
        if self.units(STALKER).amount > 15:
            for s in self.units(STALKER).idle:
                await self.do(s.attack(self.find_target(self.state)))

        elif self.units(STALKER).amount > 3:
            if len(self.known_enemy_units) > 0:
                for s in self.units(STALKER).idle:
                    await self.do(s.attack(random.choice(self.known_enemy_units)))

    ## we dont need to attack with every stalker.
    ## start with 5 stalkers and send to battle
    ## choose what to attack
    ## choose random enemy to attack
    ## build cybernetics core for defensive strategies

run_game(maps.get("AbyssalReefLE"), [Bot(Race.Protoss, SentdeBot()), Computer(Race.Terran, Difficulty.Medium)], realtime=False)

## error message not enough psi Construct additional pylons when  NEXUS amount < 3
