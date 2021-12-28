#!/usr/bin/env python3

import json
import logging
import os
import random
import string
import yaml


from GameActions import *
from flag import FLAG

# TBAG stands for Text Based Adventure Game
# This is not intended to be reusable for now

CHEATS = not True
ROOMSDIR = "rooms"


def makeRandomPassword():
    pwconf = {
        string.ascii_uppercase: 2,
        string.ascii_lowercase: 3,
        string.digits: 2,
        "!@#$%": 1,
    }

    pwchars = []

    for k, v in pwconf.items():
        pwchars += [random.choice(k) for _ in range(v)]

    random.shuffle(pwchars)
    pw = "".join([c for c in pwchars])
    return pw


class Room():
    def __init__(self, roomid):
        fn = os.path.join(ROOMSDIR, f"{roomid}.yaml")
        self._roomid = roomid
        self._data = yaml.full_load(open(fn).read())

    @staticmethod
    def exists(room):
        try:
            r = Room(room)
            return True
        except:
            pass
        return False

    @property
    def roomid(self):
        return self._roomid

    @property
    def name(self):
        return self._data["name"]

    def directionsText(self):
        upperdirections = ["n", "s", "e", "w", "ne", "se", "nw", "sw"]
        directions = [(x.upper() if x in upperdirections else x)
                      for x in self.directions]
        directions = sorted(directions)
        directions = ", ".join(directions)
        return directions

    def description(self, show_name=True, show_directions=True, append=None):
        name = self.name

        directions = self.directionsText()
        description = self._data["description"]

        out = []

        if show_name:
            out += [f">>> Your location: {name}"]

        out += [description]

        if append is not None:
            out += [append]

        if show_directions and directions != "":
            out += [f"From here you can go: {directions}"]

        return "\n\n".join([x.strip("\n") for x in out])

    @property
    def directions(self):
        if "directions" not in self._data:
            return []
        return [x.lower() for x in self._data["directions"].keys()]

    @property
    def items(self):
        if "items" not in self._data:
            return []

        return [x.lower() for x in self._data["items"].keys()]

    def itemDescription(self, item, append=None):
        out = [self._data["items"][item]]
        if append is not None:
            out += [append]

        return "\n\n".join([x.strip("\n") for x in out])

    def nextRoom(self, direction):
        return self._data["directions"][direction]


class TBAG():
    ROOMSWITCHES = {
        "design1": True,
        "design2": False,
        "storage1": True,
        "factory1": False,
        "factory2": False,
        "factory3": True,
        "kitchen": False,
        "office2": True,
        "office3": True,
        "lab1": False,
        "lab2": True,
        "recroom": True,
        "rnd": False,
        "radarroom": False,
        "storage2": True,
        "serverroom": False,
    }

    def __init__(self, statefn):
        self._statefn = statefn
        self._logger = logging.getLogger("TBAG")
        self.loadState()

        self.setName = False

    # State management
    def loadState(self):
        try:
            self._state = json.load(open(self._statefn))
            # self._logger.info(f"Loading state from {self._statefn}")
        except Exception as e:
            self._logger.warning(
                f"Loading state failed because: {e}, reverting to default state"
            )
            self._state = {}

            # The switches are an array
            switchnames = list(self.ROOMSWITCHES.keys())
            random.shuffle(switchnames)
            self._state["switches"] = [(k, random.choice([True, False]))
                                       for k in switchnames]

            # ensure some rooms are powered off
            for r in ["serverroom"]:
                if self.roomHasPower(r):
                    self.roomTogglePower(r)

            pc = random.randint(1000, 9999)
            self.setProperty("pincode", f"{pc}")
            self.setProperty("frequency", "105.3")  # FIXME
            self.setProperty("password", makeRandomPassword())
            self.setProperty("username", "greenmeanmachine")  # FIXME
            self.setProperty("sudokusolution", "514897623")  # FIXME
            self.setProperty("flag", FLAG)
            # Tune to a random frequency
            self.setRadioFrequency()

    def saveState(self):
        try:
            # create directories
            dn = os.path.dirname(self._statefn)
            if dn != "":
                os.makedirs(dn, exist_ok=True)
            json.dump(self._state,
                      open(self._statefn, "w"),
                      sort_keys=True,
                      indent=4)
            # self._logger.info(f"Saved state to {self._statefn}")
        except Exception as e:
            self._logger.error(f"Saving state failed because: {e}")

    def getProperty(self, name, default=None):
        if name in self._state:
            return self._state[name]
        return default

    def setProperty(self, name, value):
        self._state[name] = value
        self.saveState()

    # Location
    def setLocation(self, loc):
        self.setProperty("location", loc)

    def teleport(self, loc, text=None):
        self.setLocation(loc)
        newdesc = self.currentRoom().description()
        desc = ""
        if text is not None:
            desc += text
            desc += "\n\n"
        desc += newdesc

        return desc

    @property
    def location(self):
        return self.getProperty("location", default="start")

    def currentRoom(self):
        return Room(self.location)

    # Power switches
    def roomHasPower(self, roomid=None):
        if roomid is None:
            roomid = self.currentRoom().roomid

        switches = dict(self.getProperty("switches"))

        if roomid in switches:
            return switches[roomid] ^ self.ROOMSWITCHES[roomid]

        return True

    def roomTogglePower(self, roomid=None):
        if roomid is None:
            roomid = self.currentRoom().roomid

        switches = self.getProperty("switches")
        newswitches = []
        for k, v in switches:
            if k == roomid:
                val = not v
            else:
                val = v
            newswitches += [(k, val)]

        self.setProperty("switches", newswitches)

    def cheatLights(self):
        for room in self.ROOMSWITCHES:
            if not self.roomHasPower(room):
                self.roomTogglePower(room)

    # Facing
    def setFacing(self, target):
        self.setProperty("facing", target)

    @property
    def facing(self):
        return self.getProperty("facing", default=None)

    # Inventory
    def getInventory(self, item):
        iv = self.inventory
        if item in iv:
            return iv[item]
        else:
            return None

    def updateInventory(self, item, name):
        iv = self.inventory
        iv[item] = name
        self.setProperty("inventory", iv)

    def removeInventory(self, item):
        iv = self.inventory
        if item in iv:
            del iv[item]
        self.setProperty("inventory", iv)

    @property
    def inventory(self):
        return self.getProperty("inventory", default={})

    # Radio frequency
    def getRadioFrequency(self):
        return self.getProperty("currentfrequency", "100.0")

    def setRadioFrequency(self, freq=None):
        # if None, set a random frequency that is not the ninjas radio
        if freq is None:
            v = self.getProperty("frequency")
            while v == self.getProperty("frequency"):
                v = random.randrange(880, 1080) / 10.0
            freq = f"{v:.1f}"

        self.setProperty("currentfrequency", freq)
        return self.getRadioFrequency()

    # Indent output
    def indent(self, txt):
        """
        Indent lines of text to output.
        """

        indent = " " * 2
        lines = txt.strip("\n").split("\n")

        out = [f"{indent}{x}" for x in lines]
        out = [""] + out + [""]

        return "\n".join(out)

    # Command handling
    def handle(self, line):
        """
        Handle a command sent by the player. We are case sensitive, but not space sensitive
        Default commands we want to handle:
            help
            g <direction>, go <direction>
                n e s w ne se nw sw up down are shortcuts for "go"
            l <direction>, look <target>

        """
        self._logger.debug(f"Handling line: {line}")

        ret = checkGameActions(self, line)
        if ret is not None:
            return self.indent(ret)

        parts = line.split()

        # if just pressing enter, they want to clear the screen, allow that
        if len(parts) == 0:
            return ""

        # Handle help
        if parts[0].lower() == "help":
            return self.indent(self.handleHelp())

        # Handle move
        if parts[0].lower() in ["g", "go"] and len(parts) == 2:
            return self.indent(self.handleMove(parts[1]))

        if parts[0].lower() in [
                "n", "e", "s", "w", "ne", "se", "nw", "sw", "up", "down"
        ] and len(parts) == 1:
            return self.indent(self.handleMove(parts[0]))

        # Handle look
        if parts[0].lower() in ["l", "look"]:
            if len(parts) == 1:
                return self.indent(self.handleLook())

            if len(parts) == 2:
                return self.indent(self.handleLook(parts[1]))

        if parts[0].lower() in ["i", "inventory"] and len(parts) == 1:
            return self.indent(self.handleInventory())

        if CHEATS:
            if parts[0].lower() in ["lights"] and len(parts) == 1:
                self.cheatLights()
                return self.indent("CHEAT lights on")

            if parts[0].lower() in ["tp", "teleport"] and len(parts) == 2:
                roomname = parts[1]
                if Room.exists(roomname):
                    return self.indent(self.teleport(parts[1], text="*** Teleporting via Cheat ***"))
                else:
                    return self.indent(f"*** Failed to teleport: {roomname} is not an existing room ***")

        return self.indent(
            "I did not understand that. Type 'help' if you don't know what to do here."
        )

    def handleHelp(self):
        return """You are playing the OverTheWire Advent CTF 2021 'Grinch Base' challenge.
To interact with the virtual world, you can use these commands:

    look [<target>]
        Look at a certain target. Targets are identified in texts by enclosing asterisks.
        Omit the asterisks for this command.
        If target is omitted, you are shown a description of your location.
        You can abbreviate "look" with "l".

    go <direction>
        Move in a certain direction. Typical directions are N, S, E, W, NE, SE, NW, SW, up, down.
        You can use these directions without the "go" command.
        You can also abbreviate "go" with "g".

    inventory
        Show items in your inventory. You can abbreviate "inventory" with "i".

    <other commands>
        Other commands will be revealed to you while interacting with the world.
        They are enclosed in square brackets '[' and ']'.
        Pay close attention so you do not miss them.
"""

    def handleInventory(self):
        iv = self.inventory
        if iv == {}:
            return "Your inventory is empty."

        items = list(sorted(iv.keys()))
        maxlen = max([len(x) for x in items])

        if len(items) == 1:
            out = [f"You have 1 item in your inventory:"]
        else:
            out = [f"You have {len(items)} items in your inventory:"]

        for item in sorted(iv.keys()):
            spaces = " " * (maxlen - len(item))
            out += [f"    {item}{spaces} -- {iv[item]}"]

        return "\n".join(out)

    def handleMove(self, direction):
        self.setFacing(None)

        exits = self.currentRoom().directions
        if direction.lower() not in exits:
            return "You cannot go there."

        self.setLocation(self.currentRoom().nextRoom(direction.lower()))
        return self.handleLook()

    def handleLook(self, target=None):
        if not self.roomHasPower():
            return """It's pitch black in here, the power must be out.
Maybe you can switch on the power somehow?

From here you can go: """ + self.currentRoom().directionsText()

        if target is None:
            self.setFacing(None)
            ret = checkGameActions(self, "look")
            if ret is not None:
                return ret

            return self.currentRoom().description()

        items = self.currentRoom().items
        if target.lower() not in items:
            return "You cannot look there."

        self.setFacing(target.lower())
        return self.currentRoom().itemDescription(target.lower())


if __name__ == "__main__":
    import sys
    logging.basicConfig(level="DEBUG")
    fn = "states/mygame.json"
    if len(sys.argv) > 1:
        fn = sys.argv[1]

    game = TBAG(fn)

    print()
    print("You have found the Grinch Base".center(80))
    print("-- Type 'help' to start --".center(80))
    print()

    text = input("$ / > ")

    while text != "quit":
        print(game.handle(text))
        game = TBAG(fn)
        text = input("$ / > ")
