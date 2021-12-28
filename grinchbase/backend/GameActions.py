# This file contains game actions, their actual definitions start lower in this file.
# The first section contains boilerplate

import datetime
import logging
import re
import string
import time

GameActions = []


def GameAction(location=None, facing=None, cmd=None):
    def decorator(fn):
        global GameActions

        def wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            return result

        GameActions += [(location, facing, cmd, wrapper)]
        return wrapper

    return decorator


def checkGameActions(game, line):
    location = game.location
    facing = game.facing

    def __smartMatcher(item, spec):
        # if spec is None, always match
        if spec is None:
            return True

        # if item is identical to spec, match
        if item == spec:
            return True

        # if spec is a list, check if item is listed
        if type(spec) == list:
            return item in spec

        # if spec is a function, call function with item as parameter
        if callable(spec):
            return spec(item)

        # Otherwise, no match
        return False

    for ga in GameActions:
        (loc, fac, cmd, fn) = ga
        locmatch = __smartMatcher(location, loc)
        facmatch = __smartMatcher(facing, fac)
        cmdmatch = __smartMatcher(line, cmd)

        # logging.debug(f"GameAction results for line '{line}': {ga}: {locmatch} {facmatch} {cmdmatch}")

        if locmatch and facmatch and cmdmatch:
            ret = fn(game, line)

            if ret is not None:
                return ret


##############################################################
##############################################################
##
# Game actions start below this line
##
##############################################################
##############################################################

# Getting the visitor badge at the gate
@GameAction(location=["gate", "start"],
            facing="guard",
            cmd=lambda l: None is not re.match(
                r'^\s*my\s+name\s+is\s+(.*)\s*$', l, flags=re.IGNORECASE))
def setname(game, line):
    oldname = game.getProperty("name")

    m = re.match(r'^\s*my\s+name\s+is\s+(.*)\s*$', line, flags=re.IGNORECASE)
    name = m.group(1).strip()
    logging.debug(f"Setting name to '{name}'")
    game.setProperty("name", name)
    game.updateInventory("badge", f"A visitor badge with your name: {name}")

    if oldname is None:
        return f"""
The guard prints out a visitor badge with your name and hands it to you.
The guard says: 
    'You can now enter the gate with [use badge]. Have a nice evening!'
"""
    else:
        return f"""
The guard prints out a new visitor badge with your name and hands it to you.
The guard says: 
    'You know the drill, you can enter the gate with [use badge].'
"""


@GameAction(location=["gate", "start"],
            cmd=lambda l: None is not re.match(
                r'^\s*use\s+badge\s*$', l, flags=re.IGNORECASE))
def usebadge(game, line):
    if None is game.getInventory("badge"):
        return "You do not have a visitor badge. Talk to the guard at the gate."

    return game.teleport("entrance",
                         text="""You use your badge and go through the gate.""")


@GameAction(location="design2",
            cmd=lambda l: None is not re.match(
                r'^\s*(l|look)\s+desk\s*$', l, flags=re.IGNORECASE))
def lookdesk(game, line):
    if None is game.getInventory("accesscard"):
        return game.currentRoom().itemDescription(
            "desk",
            append="""... You look below the desk and notice someone stuck an access
card against the bottom of the desk with a piece of gum.
Use [take accesscard] to take it.""")


@GameAction(location="design2",
            cmd=lambda l: None is not re.match(
                r'^\s*take\s+accesscard\s*$', l, flags=re.IGNORECASE))
def takeaccesscard(game, line):
    if None is game.getInventory("accesscard"):
        game.updateInventory(
            "accesscard",
            "A standard accesscard with pincode written on the back.")
        return """You look left and right to make sure noone sees you. 
Then you quickly "borrow" the accesscard. There's a pincode written on the back.
The accesscard is now in your inventory."""
    else:
        return "You already took the accesscard, remember? It's in your inventory."


# Access lab1
@GameAction(location="factory2",
            facing="keypad",
            cmd=lambda l: None is not re.match(
                r'^\s*use\s+accesscard\s*$', l, flags=re.IGNORECASE))
def useaccesscard(game, line):
    if None is game.getInventory("accesscard"):
        return "You remember that you didn't bring your access card. The door remains closed."

    if not game.roomHasPower("lab1"):
        return """The keypad doesn't respond when you swipe the accesscard.
The power must be out in that room.
Maybe you can switch on the power somehow?"""

    return game.teleport("lab1",
                         text="""You use the accesscard.
The keypad asks for a pincode.
Luckily, the owner of the accesscard was foolish enough to write it on the back of the accesscard.
The keypad beeps green and the door opens.""")


# Access lab2
@GameAction(location="factory3",
            facing="keypad",
            cmd=lambda l: None is not re.match(
                r'^\s*use\s+accesscard\s*$', l, flags=re.IGNORECASE))
def useaccesscard2(game, line):
    if None is game.getInventory("accesscard"):
        return "You remember that you didn't bring your access card. The door remains closed."

    if not game.roomHasPower("lab2"):
        return """The keypad doesn't respond when you swipe the accesscard.
The power must be out in that room.
Maybe you can switch on the power somehow?"""

    return game.teleport("lab2",
                         text="""You use the accesscard.
The keypad asks for a pincode.
Luckily, the owner of the accesscard was foolish enough to write it on the back of the accesscard.
The keypad beeps green and the door opens.""")


# Access server room
@GameAction(location="radarroom",
            facing="keypad",
            cmd=lambda l: None is not re.match(
                r'^\s*keypad\s+(\S+)\s*$', l, flags=re.IGNORECASE))
def keypadpin(game, line):
    m = re.match(r'^\s*keypad\s+(\S+)\s*$', line, flags=re.IGNORECASE)
    pincode = m.group(1)
    realpincode = game.getProperty("pincode")

    if None is game.getInventory("special accesscard"):
        return f"""You punch {pincode} into the keypad, but it doesn't do anything.
You remember that you need to swipe a special accesscard first, which you don't have.
The door remains closed."""

    if not game.roomHasPower("serverroom"):
        return """The keypad doesn't respond when you swipe the special accesscard.
The power must be out in that room.
Maybe you can switch on the power somehow?"""

    if len(pincode) != 4 or any([c not in string.digits for c in pincode]):
        return f"""That is not a valid 4-digit pincode.
The keypad beeps red. The door remains closed.
Maybe someone was foolish enough to write down the pincode somewhere?"""

    if pincode == realpincode:
        return game.teleport("serverroom",
                             text=f"""You swipe the special accesscard.
The keypad asks for a pincode and you punch in {pincode}.
The keypad beeps green and the door opens.""")

    return f"""You swipe the special accesscard.
The keypad asks for a pincode and you punch in {pincode}.
The keypad beeps red. The door remains closed.
Maybe someone was foolish enough to write down the pincode somewhere?"""


# Switchboard with power breakers implementation
def niceswitchboard(game):
    #       1   2   3   4
    #     +---+---+---+---+
    #   A |  #|#  |   |   |

    switches = game.getProperty("switches")
    i = 0
    out = []
    out += ["    1   2   3   4"]
    out += ["  +---+---+---+---+"]

    for row in "ABCD":
        line = f"{row} |"
        for col in "1234":
            n, v = switches[i]
            i += 1
            if v:
                line += "#  |"
            else:
                line += "  #|"

        out += [line]
        out += ["  +---+---+---+---+"]

    return "\n".join(out)


@GameAction(location="grinchoffice",
            cmd=lambda l: None is not re.match(
                r'^\s*(l|look)\s+(sw|switchboard)\s*$', l, flags=re.IGNORECASE)
            )
def showswitchboard(game, line):
    appended = niceswitchboard(game)
    return game.currentRoom().itemDescription("switchboard", append=appended)


@GameAction(
    location="grinchoffice",
    cmd=lambda l: None is not re.match(
        r'^\s*(t|toggle)\s+((A|B|C|D)(1|2|3|4))\s*$', l, flags=re.IGNORECASE))
def toggleswitchboard(game, line):
    m = re.match(r'^\s*(t|toggle)\s+((A|B|C|D)(1|2|3|4))\s*$',
                 line,
                 flags=re.IGNORECASE)

    rows = "ABCD"
    cols = "1234"

    switchname = m.group(2).upper()
    row = rows.index(m.group(3).upper())
    col = cols.index(m.group(4))

    idx = row * len(cols) + col

    switches = game.getProperty("switches")
    roomid = switches[idx][0]

    game.roomTogglePower(roomid)
    v = "ON" if game.roomHasPower(roomid) else "OFF"
    logging.warning(f"Switched power for {roomid} to {v}")

    return f"You toggled switch {switchname}.\nThe switchboard now looks like this:\n\n" + niceswitchboard(
        game)


# Radio transmitter activation
@GameAction(location="rnd",
            cmd=lambda l: None is not re.match(
                r'^\s*(l|look)\s+device\s*$', l, flags=re.IGNORECASE))
def showdevice(game, line):
    if not game.roomHasPower():
        return "It's pitch black in here and you don't see a thing."

    txon = game.getProperty("txon")

    if txon:
        appended = """There's a slight humming coming from the device
and from time, a light flickers. You're not sure what it's doing, but
it seems to be powered on.
You can deactivate the device with [deactivate device].
"""
    else:
        appended = """The device feels cold to the touch and doesn't seem
to even be powered on. There is a small switch on the back.
You can activate the device with [activate device].
"""

    return game.currentRoom().itemDescription("device", append=appended)


@GameAction(
    location="rnd",
    cmd=lambda l: None is not re.match(
        r'^\s*(activate|deactivate)\s+device\s*$', l, flags=re.IGNORECASE))
def activatedevice(game, line):
    if not game.roomHasPower():
        return "It's pitch black in here and you don't see a thing."

    m = re.match(r'^\s*(activate|deactivate)\s+device\s*$',
                 line,
                 flags=re.IGNORECASE)
    cmd = m.group(1)
    txon = game.getProperty("txon")

    if cmd.lower() == "activate":
        if txon:
            return "The device is already active."
        else:
            game.setProperty("txon", True)
            return "You switch on the device. It starts humming."
    else:
        if txon:
            game.setProperty("txon", False)
            return "You switch off the device. The humming stops."
        else:
            return "The device was not activated."


# Radio receiver
def morse(m):
    alphabet = "abcdefghijklmnopqrstuvwxyz1234567890."
    morsecode = " ".join([
        ".- -... -.-. -.. . ..-. --. .... .. .---",
        "-.- .-.. -- -. --- .--. --.- .-. ... -",
        "..- ...- .-- -..- -.-- --..", ".---- ..--- ...-- ....- .....",
        "-.... --... ---.. ----. -----", ".-.-.-"
    ]).split(" ")

    tr = dict(zip(alphabet, morsecode))
    out = []
    line = ""

    for x in m.lower():
        if x == " ":
            enc = "   "
        else:
            enc = tr[x]

        # don't start a line with spaces, that's silly
        if not (len(line) == 0 and x == " "):
            line += f"{enc} "
        if len(line) > 60:
            out += [line]
            line = ""

    if len(line) > 0:
        out += [line]

    return "\n".join(out)


def radiosound(game, f):
    #           88.3 FM "Whoville FM"
    #           91.7 FM "North Pole Sounds"
    #          101.1 FM "Metal XMAS"
    #           94.9 FM "Elf Rock"
    #          107.5 FM "Come Sing Along"
    active = game.getProperty("txon")
    frequency = game.getProperty("frequency")
    username = game.getProperty("username")
    freqmap = {
        "88.3":
        "A radio reporter is reading the latest news from Whoville. Apparently, Holly Sassy-snew-Who has won the cookie-baking competition.",
        "91.7":
        "Sounds of ice cracking under the heavy feet of a polar bear growling.",
        "101.1":
        "A saxophone gently improvizes some sounds against a backdrop of a cacophony from an apparent fight between a drum and an electric guitar.",
        "94.9":
        "A soft rock band sings about their love for candy.",
        "107.5":
        "A crowd appears to be singing a christmas carol you recognize. You resist the urge to sing along.",
        frequency:
        "A series of short and long beeps:\n" + morse(
            f"This is the inhouse resistance against our boss the Grinch. "
            f"We hope you will find the following information useful. "
            f"If you want to shutdown the missile system "
            f"you should login to the server using the all lowercase username {username}. "
        ),
    }

    if not active:
        del freqmap[frequency]

    if f in freqmap:
        return freqmap[f]

    if any(f.split(".")[0] == mf.split(".")[0] for mf in freqmap.keys()):
        return """Static noise gives way to some more defined sounds, but
you can't clearly define yet what kind of sound this is. You surmize that
this frequency is close to the frequency of a radio station."""

    return "It's just static noise."


@GameAction(location="lab1",
            cmd=lambda l: None is not re.match(
                r'^\s*(l|look)\s+radio\s*$', l, flags=re.IGNORECASE))
def showradio(game, line):
    if not game.roomHasPower():
        return "It's pitch black in here and you don't see a thing."

    freq = game.getRadioFrequency()
    sound = radiosound(game, freq)
    appended = f"""The display reads: "{freq} FM".
You hear some sound coming from the radio.
{sound}
"""

    return game.currentRoom().itemDescription("radio", append=appended)


@GameAction(location="lab1",
            cmd=lambda l: None is not re.match(
                r'^\s*tune\s+(\S+)\s*$', l, flags=re.IGNORECASE))
def tuneradio(game, line):
    if not game.roomHasPower():
        return "It's pitch black in here and you don't see a thing."

    m = re.match(r'^\s*tune\s+(\S+)\s*$', line, flags=re.IGNORECASE)
    newfreq = m.group(1)

    m = re.match(r'^((\d+)|(\d+\.\d+))$', newfreq, flags=re.IGNORECASE)
    if not m:
        return "That doesn't look like a valid frequency."

    freq = float(m.group(1))
    if freq < 88.0 or freq > 108.0:
        return "That doesn't look like a valid FM radio frequency."

    freq = f"{freq:.1f}"

    game.setRadioFrequency(freq)
    freq = game.getRadioFrequency()
    sound = radiosound(game, freq)
    return f"""The display now reads: "{freq} FM".
You hear some sound coming from the radio.
{sound}
"""


# Submit sudoku
@GameAction(location="office2",
            facing="website",
            cmd=lambda l: None is not re.match(
                r'^\s*submit\s+(\d+)\s*$', l, flags=re.IGNORECASE))
def submitsudoku(game, line):
    pincode = game.getProperty("pincode")
    if not game.roomHasPower():
        return "It's pitch black in here and you don't see a thing."

    m = re.match(r'^\s*submit\s+(\d+)\s*$', line, flags=re.IGNORECASE)
    solution = m.group(1)
    sudokusolution = game.getProperty("sudokusolution")

    if len(solution) != len(sudokusolution):
        return """The website responds:

    "Your submitted solution should contain 9 digits.
    Remember, we want you to submit the _middle_ row.
    Please try again"."""

    if solution != sudokusolution:
        return """The website responds:

    "Unfortunately, your solution is not correct.
    Please try again"."""

    return f"""The website responds:

    "Congratulations! A winner is you!
    Unfortunately, all {pincode} prizes have already
    been claimed by other sudoku solvers who were
    slightly faster than you. Better luck next time!"

You sigh and exclaim:

    "What kind of a number is {pincode}?"

A voice assistant application on the computer starts up and replies:

    "The number {pincode} is the pincode to access the server room!"
"""


@GameAction(location="lab2",
            facing="sign",
            cmd=lambda l: None is not re.match(
                r'^\s*touch\s+sign\s*$', l, flags=re.IGNORECASE))
def touchsign(game, line):
    if not game.roomHasPower():
        return "It's pitch black in here and you don't see a thing."

    return """!~~!!~ZAP!~!!!!~!!~
A jolt of electricity rushes through your body and shakes you to the core.
'Apparently, danger signs exist for a reason' you joke outloud to an absent audience.
You silently decide to heed warning signs from now on.
"""


# Reboot server
def analyze_password(pw, realpw):
    charsets = [
        ("uppercase letters", string.ascii_uppercase),
        ("lowercase letters", string.ascii_lowercase),
        ("digits", string.digits),
        ("special characters", "!@#$%"),
    ]

    allchars = "".join([l for (n, l) in charsets])

    if len(pw) != len(realpw):
        return "      - The length of your password doesn't match the expected password."

    if not all(c in allchars for c in pw):
        return "      - Your password contains illegal characters."

    out = []
    for charsetname, charset in charsets:
        pwchars = [c for c in pw if c in charset]
        realpwchars = [c for c in realpw if c in charset]

        if len(pwchars) != len(realpwchars):
            out += [
                f"      - The amount of {charsetname} in your password doesn't match the expected password."
            ]

        if set(pwchars) != set(realpwchars):
            out += [
                f"      - Some {charsetname} in your password are not in the expected password, or vice versa."
            ]

        correct = 0
        for i in range(len(pw)):
            a = pw[i]
            b = realpw[i]

            if a == b and a in charset:
                correct += 1

        if correct != len(pwchars):
            if correct == 0:
                out += [
                    f"      - None of the {charsetname} in your password are in the right place."
                ]
            else:
                out += [
                    f"      - Only {correct} of the {charsetname} in your password are in the right place."
                ]

    return "\n".join(out)


@GameAction(location="serverroom",
            facing="server",
            cmd=lambda l: None is not re.match(
                r'^\s*login\s+(\S+)\s+(\S+)\s*$', l, flags=re.IGNORECASE))
def tuneradio(game, line):
    if not game.roomHasPower():
        return "It's pitch black in here and you don't see a thing."

    m = re.match(r'^\s*login\s+(\S+)\s+(\S+)\s*$', line, flags=re.IGNORECASE)

    username = m.group(1).lower()
    password = m.group(2)
    realpassword = game.getProperty("password")
    realusername = game.getProperty("username")

    if username != realusername.lower():
        return f"""A dialog box pops up. It reads:

     Invalid username '{username}'. Login failed."""

    if password != realpassword:
        reason = analyze_password(password, realpassword)
        return f"""A dialog box pops up. It reads:

     Invalid password '{password}'. Login failed.
{reason}"""

    return winfunction(game)


InterrogationQuestions = [
    {
        "problem":  """What gifts should children receive for Christmas?""",
        "options": {
            "1": (-1, """Lots of toys and candy"""),
            "2": (0, """More homework"""),
            "3": (1, """Nothing! We hate children!"""),
        }
    },
    {
        "problem":  """Why was it so hard to miss the Grinch on Christmas morning?""",
        "options": {
            "1": (0, """Because we all have to work on that day"""),
            "2": (1, """Because he has has all the presence"""),
            "3": (-1, """I don't know"""),
        }
    },
    {
        "problem":  """Which Christmas carol is the most annoying?""",
        "options": {
            "1": (1, """All of them!"""),
            "2": (-1, """Jingle bells"""),
            "3": (0, """You're a mean one, mister Grinch"""),
        }
    },
    {
        "problem":  """Why is the Grinch afraid of Santa Claus?""",
        "options": {
            "1": (0, """He is not!"""),
            "2": (-1, """Because he has so much love in his heart"""),
            "3": (1, """Because he is Claustrophobic"""),
        }
    },
    {
        "problem":  """Who is the best boss in the whole world?""",
        "options": {
            "1": (0, """Max"""),
            "2": (-1, """Santa"""),
            "3": (1, """Grinch"""),
        }
    },
    {
        "problem":  """Why doesn't the Grinch like knock knock jokes?""",
        "options": {
            "1": (0, """Because it reveals our secret base!"""),
            "2": (1, """Because there’s always Who's there!"""),
            "3": (-1, """He does!"""),
        }
    },
    {
        "problem":  """What secret did the Grinch sobbingly confide in us during last month's meeting?""",
        "options": {
            "1": (-1, """His heart has grown a size"""),
            "2": (1, """He secretly wants to be Santa"""),
            "3": (0, """He is proud of us"""),
        }
    },
]


@GameAction(location="securityoffice",
            cmd=lambda l: None is not re.match(
                r'^\s*(l|look)\s*$', l, flags=re.IGNORECASE))
def looksecurityoffice(game, line):
    game.setFacing(None)
    interrogation = game.getProperty("interrogation")

    if interrogation is None:
        game.setProperty("interrogation", "started")
        return game.currentRoom().description()

    if interrogation == "started":
        return """The head of security on the *computer* screen notices you are
    looking around and calls you back to attention:

    "Hey buddy! Look at me while I question you!"
"""
    elif interrogation == "givecard":
        return """The head of security says:

    "Sorry for questioning you like this. I'm sure you understand,
    we don't get a lot of visitors up here and are under strict
    instructions not to trust anyone. 
    Coincidentally, my security guard found a special accesscard
    on the floor earlier and we're sure it belongs to you. Have a
    nice day!" 

Type [take accesscard] to receive the special accesscard.
"""
    else:
        return """The security guard is behind his desk again, about
to take a nap. He looks at you and asks:
    "Hey friend, you need anything else? I have a lot of work
    here."
You decide that getting questioned again is not a good idea
and that you should leave now.

Type [exit] to leave the room."""


@GameAction(location="securityoffice",
            cmd=lambda l: None is not re.match(
                r'^\s*(l|look)\s+computer\s*$', l, flags=re.IGNORECASE))
def lookinterrogationscreen(game, line):
    game.setFacing("computer")
    interrogation = game.getProperty("interrogation")

    if interrogation != "started":
        return "The computer's screen is locked. It doesn't look like it will be used again today..."

    interrogationquestion = game.getProperty("interrogationquestion", 0)

    problem = InterrogationQuestions[interrogationquestion]

    problemdesc = problem["problem"]

    out = f"""The head of security on the computer screen looks straight at you.
    He pauses for a moment to observe your reaction and then asks:

    {problemdesc}

You ponder what answer would convince him, knowing that the fate of Christmas hangs in the balance.
You can think of three possible answers:

"""
    for (k, rec) in problem["options"].items():
        (v, s) = rec
        out += f"    {k}.  {s}\n"

    out += "\nType [option <number>] to select your answer."

    return out


def interrogationscore(game):
    res = 0
    for i in range(len(InterrogationQuestions)):
        a = game.getProperty(f"interrogationanswer{i}")
        if a is not None:
            v, _ = InterrogationQuestions[i]["options"][a]
        else:
            v = 0

        logging.debug(f"Q{i}: {v}")
        res += v
    return res


@GameAction(location="securityoffice",
            facing="computer",
            cmd=lambda l: None is not re.match(
                r'^\s*option\s+(1|2|3)\s*$', l, flags=re.IGNORECASE))
def sendsolution(game, line):
    m = re.match(r'^\s*option\s+(1|2|3)\s*$', line, flags=re.IGNORECASE)
    interrogationquestion = game.getProperty("interrogationquestion", 0)
    problem = InterrogationQuestions[interrogationquestion]
    sol = m.group(1)
    game.setProperty(f"interrogationanswer{interrogationquestion}", sol)

    (val, _) = problem["options"][sol]

    if val == 1:
        reaction = "pleased"
    elif val == 0:
        reaction = "unmoved"
    else:
        reaction = "annoyed"

    out = f"""You calmly give your answer and glance at the head of security.
They look {reaction}.\n\n"""

    interrogationquestion += 1
    game.setProperty("interrogationquestion", interrogationquestion)

    if interrogationquestion >= len(InterrogationQuestions):
        interrogationquestion = 0
        game.setProperty("interrogationquestion", interrogationquestion)

        if interrogationscore(game) == len(InterrogationQuestions):
            out += """
    "OK OK, it looks like you belong here after all" says the head of security.

"""
            game.setProperty("interrogation", "givecard")
            out += looksecurityoffice(game, "l")
        else:
            out += """
    "Hmm, we both know you can do better than this. Let's try this again" says the head of security."""
    else:
        out += lookinterrogationscreen(game, "look computer")

    return out


@GameAction(location="securityoffice",
            cmd=lambda l: None is not re.match(
                r'^\s*take\s+accesscard\s*$', l, flags=re.IGNORECASE))
def takecard(game, line):
    interrogation = game.getProperty("interrogation")

    if interrogation == "givecard":
        game.updateInventory(
            "special accesscard",
            "A special accesscard that can access the server room.")
        game.setProperty("interrogation", "done")
        return "You accept the special accesscard. It is now in your inventory."

    if interrogation == "done":
        return "You already took the card, remember?"

    return "Not yet, you have some questions to answer first!"


@GameAction(
    location="securityoffice",
    cmd=lambda l: None is not re.match(r'^\s*exit\s*$', l, flags=re.IGNORECASE)
)
def exitsecurityoffice(game, line):
    if game.getProperty("interrogation") == "done":
        return game.teleport(
            "office1",
            text="""You leave the security office feeling relieved that you were not caught.""")
    else:
        return "You can't leave yet."


def winfunction(game):
    game.setName = True
    if game.getProperty("wintime") == None:
        game.setProperty("wintime", time.time())
        game.setProperty("wintimestr", str(datetime.datetime.now()))

    flag = game.getProperty("flag")
    return f"""The login box makes way for another screen.
You navigate the software menus and locate the graceful shutdown button.
Your fingers tremble as you click shutdown. "Is this it? Did I miss anything?"
For a moment, time feels frozen as nothing seems to happen...

Then one by one, the lights on the servers in the room start going out.
In a panic, you run outside the window in Design office 2.
You hold your breath as your observe the missile launch system.

Oh no! The motors start spinning! You see how the launch system erects
itself on the launchpad and then...

...folds the missiles away and closes the launch hatches!
YES! You did it!!!! The missile system has shut down!
You send out "MISSION SUCCESS" on your comm-radio and moments later
you hear the sweetest sound you've ever heard...

It's the jingle bells on Sleigh One as it approaches your position.
Santa lands next to you, steps out and walks towards you.
With a warm embrace Santa whispers:

                     Well done my child!
                  You have saved Christmas!

     {flag}

Press the enter key to finish the game.
"""


# This is for debugging
# @GameAction(
# location="securityoffice",
# cmd=lambda l: None is not re.match(r'^\s*x\s*$', l, flags=re.IGNORECASE))
# def resetsecurityoffice(game, line):
####     interrogation = game.getProperty("interrogation")
# states = {
# "started": "givecard",
# "givecard": "done",
# "done": "started",
# }
####     newgame = states[interrogation]
####     game.setProperty("interrogation", newgame)
# return f"went from {interrogation} to {newgame}"
####
####
# @GameAction(cmd="cheat")
# def togglelight(game, line):
# game.roomTogglePower()
####     roomid = game.currentRoom().roomid
####     v = game.roomHasPower()
####     logging.warning(f"CHEAT Switched power for {roomid} to {v}")
# return game.currentRoom().description(append="Power toggled")
####
####
# @GameAction(cmd="win")
# def togglelight(game, line):
#    return winfunction(game)
