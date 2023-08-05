
# -*- coding: utf-8 -*-
import os
import datetime
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *

logger = logging.getLogger(__name__)

@parameters([Property.Number(label="HeatingRate", description="Simulated: maximal heating rate when heating for a long time"), 
             Property.Number(label="CoolingRate", description="Simulated: maximal cooling rate when heating is off for a long time"),
             Property.Kettle(label="SimulatedKettle", description="the kettle which temperature should be simulated"),
             Property.Select(label="LogSimulatedSensor",options=["Yes","No"], description="on the setting (Yes) the simulated sensor will be logged as well. On the setting (No) there wont be any logging for this simulated sensor.")])
class SimulatedSensor(CBPiSensor):
    
    def __init__(self, cbpi, id, props):
        super(SimulatedSensor, self).__init__(cbpi, id, props)
        self.value = 0
        self.running = True
        logger.info("Kettle ID:" + str(self.props))

    async def run(self):
        HeaterID = self.props.SimulatedHeater
        while self.running == True:
        #while True:
            HeaterID = self.cbpi.kettle.find_by_id(self.props.SimulatedKettle).heater
            Heater = self.cbpi.actor.find_by_id(HeaterID)
            HeaterState = self.cbpi.actor.find_by_id(HeaterID).instance.state
            potentialNewValue = self.value
            if HeaterState :
                potentialNewValue = round(self.value + float(self.props.HeatingRate), 2)
            else:
                potentialNewValue = round(self.value - float(self.props.CoolingRate), 2)
            clampedValue = clamp(potentialNewValue,-20,120)
            if clampedValue != self.value :
                self.value = clampedValue
                #print(self.value)
                self.push_update(self.value)
            if self.props.get("LogSimulatedSensor", "Yes") == "Yes":
                self.log_data(self.value)
            await asyncio.sleep(1)
    
    def get_state(self):
        return dict(value=self.value)

def setup(cbpi):
    cbpi.plugin.register("SimulatedSensor", SimulatedSensor)
    pass

def clamp(n, minn, maxn):
    if n < minn:
        return minn
    elif n > maxn:
        return maxn
    else:
        return n