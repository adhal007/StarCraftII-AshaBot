import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
 CYBERNETICSCORE, STALKER, STARGATE, VOIDRAY
import random
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
# other baseless to have more than 3 patch of workers for each
# mineral or we will exhaust our resources of workers

#### Tutorial III #### Geysers and Expanding
# When to expand ? to 2 or 3 nexus areas

#### Tutorial IV #### Building an Army
## build a gateway for stalker
## build dynamic units with the stalker

#### Tutorial V ####
#### commanding your army strategy
#### send if more than 3 stalkers
#### attack to worker ratio
#### DPS/health - build more attacker units

#### Tutorial VI ####
## Major things going wrong with out BOT:
#1. No notion of time
## Has 3 nexuses - primary objective before building military unit
#2. Do we want to build 3 gateways right away ? Defensive strategy
## 3 is good for the start of the game but not as the game progresses
## Also we can use the resources somewhere else instead of using it for
## gateways unnnecessarily.
## Is 3 gateways enough for a long match ?
## fixed number doesn't make sense
## needs to be a variable based on resource rate, no of workers, nexuses or time
#3. How many units to attack?
## 15 is not a good amount with time
#4. New units running to enemy?
## one by one sending without clustering

class SentdeBot(sc2.BotAI):
    def __init__(self):
        self.ITERATIONS_PER_MINUTE > 165
        self.MAX_WORKERS = 69
        ## constant for iterations per minute

    async def on_step(self, iteration):
        self.iteration = iteration
        ## where we are currently: accessing current state iteration
        ## define an ansynchronous method
        ## every step we get, what will we do
        await self.distribute_workers()
        ## already defined
        await self.builder_workers()
        ## doesnt exist yet
        await self.build_pylons()
        await self.build_assimilators()
        await self.expand()
        await self.offensive_force_buildings()
        await self.build_offensive_force()
        await self.attack()

    async def builder_workers(self):
        ## maximum workers per nexus
        if len(self.units(NEXUS))*16 > len(self.units(PROBE))  and len(self.units(PROBE)) < self.MAX_WORKERS:
            for nexus in self.units(NEXUS).ready.noqueue:
            ## Nexus must be ready
            ## no queue - nothing else in the queue
                if self.can_afford(PROBE):
            ## inherited probe
                    await self.do(nexus.train(PROBE))

    async def build_pylons(self):
        ## create some logic for resource management
        ## if no supplies build pylons - simple logic
        ## can add more intelligence
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
        if self.units(NEXUS).amount < (self.iteration / self.ITERATIONS_PER_MINUTE):
            await self.expand_now()

    ## best situation will be to detect a soldier's rush or knight's rush
    ## by the enemy and then decide how many nexuses to expand
    ## Goal of resource areas = 2

    async def offensive_force_buildings(self):
        #print(self.iteration/self.ITERATIONS_PER_MINUTE)
        if self.units(PYLON).ready.exists:
            pylon = self.units(PYLON).ready.random
            ## only grab the pylon, build cyberneticscore as soon as you have gateway
            if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
                # either build a stalker or cyberneticscore
                if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):

                    await self.build(CYBERNETICSCORE, near=pylon)

            elif len(self.units(GATEWAY)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
                ## if game goes longer, we want upgrade of stalker
                if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                    await self.build(GATEWAY, near=pylon)

            if self.units(CYBERNETICSCORE).ready.exists:
                if len(self.units(STARGATE)) < ((self.iteration / self.ITERATIONS_PER_MINUTE)/2):
                    if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
                        await self.build(STARGATE, near=pylon)

    async def build_offensive_force(self):
        # build stalkers and not too many units
        # workers might get in the way
        # once a min we need a gateway
        # we don't want too many workers - have limitation
        for gw in  self.units(GATEWAY).ready.noqueue:
            if not self.units(STALKER).amount > self.units(VOIDRAY).amount:
                if self.can_afford(STALKER) and self.supply_left > 0:
                    await self.do(gw.train(STALKER))

        for sg in self.units(STARGATE).ready.noqueue:
            if self.can_afford(VOIDRAY) and self.supply_left > 0:
                await self.do(sg.train(STARGATE))

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            return self.enemy_start_location[0]

    async def attack(self):
        # {UNIT: [n to fight , n to defend]}

        aggressive_units = {STALKER: [15, 5], VOIDRAY: [8, 3]}

        for UNIT in aggressive_units:
            if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units[UNIT].amount > aggressive_units[UNIT][1]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))

            elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
                if len(self.known_enemy_units) > 0:
                    for s in self.units(UNIT).idle:
                        await self.do(s.attack(random.choice(self.known_enemy_units)))

    ## we dont need to attack with every stalker.
    ## start with 5 stalkers and send to battle
    ## choose what to attack
    ## choose random enemy to attack
    ## build cybernetics core for defensive strategies

run_game(maps.get("AbyssalReefLE"), [Bot(Race.Protoss, SentdeBot()), Computer(Race.Terran, Difficulty.Medium)], realtime=False)

## error message not enough psi Construct additional pylons when  NEXUS amount < 3
