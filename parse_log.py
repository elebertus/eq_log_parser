#!/usr/bin/env python
import re
import pprint
import time
from calendar import timegm
from sys import argv

# TODO(elebertus) Build this into a proper project with functions
# this will also fix the pylint const naming warnings.

"""
    parser schema
    {
        "fight_name": {
            "player": [
                "hit": {
                    "target": "target_name",
                    "attack_type": "attack_type_name",
                    "attack_damage": "attack_damage_value",
                    "time_stamp": "time_stamp_value"
                    }
            ],
            [
                "miss": {
                    "target": "target_name",
                    "attack_type": "attack_type_name",
                    "attack_damage": "attack_damage_value",
                    "time_stamp": "time_stamp_value"
                    }
            ]
        }
    }
"""

def to_epoch(time_to_convert):
    """
    to_epoch takes an eq log formatted time stamp
    and returns the unix epoch time
    """
    epoch = time.strptime(time_to_convert, "%a-%b-%d-%H:%M:%S-%Y")
    return timegm(epoch)


# TODO(elebertus) Parse damage taken, heals, and try to associate pets.
# the player dict will require a pet dict that mirror's the 
# player's.

# Build the regular expressions to find the time stamp,
# detect a hit or a miss, the target, and the damage value
fight_name = re.sub(r'\.', '_', argv[1].split('/', 1)[-1].lower())
one_time_stamp = r"\[([A-z]{3}\s[A-z]{3}\s[0-31]{2}\s[0-9]{2}:[0-9]{2}:[0-9]{2}\s[0-9]{4})\]"
two_three_action_success = one_time_stamp + r"\s([A-z]+)\s(slashes|pierces|kicks|punches|hit|strikes)"
# TODO(elebertus) put misses into the player dict
# action_fail = one_time_stamp + r"\s([A-z]+)\stries|try\sto\s(slash$|pierce$|kick$|punch$|hit$|strike$)"
four_target = two_three_action_success + r"\s(Magi\s|.+)\sfor"
# TODO(elebertus) Split melee damage and non-melee damage into their own
# values. Overwrite `attack_type` from "hit" to
# non_melee_damage.

five_damage = four_target + r"\s([0-9]+)"
# TODO(elebertus) Catch the exception when the file can't be opened or found
with open(argv[1]) as log:
    log_lines = log.readlines()

log_dict = {fight_name: {}}
log_lines = [x.strip().lower() for x in log_lines]
for hit in log_lines:
    m = re.search(five_damage, hit)
    if m:
        target = re.sub(r'\`|\s', '_', m.group(4))
        time_stamp = to_epoch(re.sub(r'\s', '-', m.group(1)))
        # TODO(elebertus) There's probably an IndexError littered in here.
        # the `if m:` block doesn't validate if the tuple
        # returned from m.group(i) is None
        if m.group(2) in log_dict[fight_name].keys():
            log_dict[fight_name][m.group(2)].append({"hit": {\
            "target": target, \
            "attack_type": m.group(3), \
            "attack_damage": m.group(5), \
            "time_stamp": time_stamp}}
                                                   )
        else:
            log_dict[fight_name].update({m.group(2): []})
            log_dict[fight_name][m.group(2)].append({"hit": {\
            "target": target, \
            "attack_type": m.group(3), \
            "attack_damage": m.group(5), \
            "time_stamp": time_stamp}}
                                                   )

pp = pprint.PrettyPrinter(indent=2)
pp.pprint(log_dict)
