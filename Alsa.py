#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import sys
import os
import errno
from subprocess import call, Popen, PIPE
import json




def get_channel_name(desc, name, i):
        for control in desc:
            lines = control.split("\n")
            pos = (lines[0][1:]).find("',")
            if pos > -1:
                control_name = (lines[0][1:pos+1])
            if control_name not in name:
                continue

            for line in lines[1:]:
                if name.split(" ")[-2] in line:
                    names = line.split(": ")[1].split(" - ")
                    return names[i]

        return None

def get_cards():
        system_cards = []
        try:
            with open("/proc/asound/cards", 'rt') as f:
                for l in f.readlines():
                    if ']:' in l:
                        system_cards.append(l.strip())
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise e

        cards = {}
        for i in system_cards:
            pos1 = i.find(']:',0,30)
            pos0 = i.find('[',0,25)
            if pos0 > 0  and pos1 > 0 and pos0 < pos1: 
                card_name = i[pos0+1:pos1].strip()
                card_number = i.split(" [")[0].strip()
                card_desc = i[pos1+2:].strip()
                record_details = Popen(["arecord", "-D", "hw:" + card_name,'-c','99', "--dump-hw-params"], stderr=PIPE).communicate()[1]
                card_rates = card_formats = card_rchannel = 0
                for x in (record_details).decode().split('\n'):
                    if x.startswith('FORMAT:'):
                        x = x[7:].strip()
                        if '[' in x and ']' in x:
                         x = x[1:-1].split(' ')
                        else:
                         x = [x]
                        card_formats = x
                    elif x.startswith('CHANNELS:'):
                        x = x[9:].strip()
                        card_rchannel = int(x)
                    elif x.startswith('RATE:'):
                        x = x[5:].strip()
                        if '[' in x and ']' in x:
                         x = x[1:-1].split()
                        else:
                             x = [x]
                        card_rates = x
                        break
                cards[card_name] = {'id':card_number, 
                                    'description':card_desc + ' on/off',
                                    'name':card_name,
                                    'value': False,
                                    'type': 'bool',
                                    'rates':card_rates, 
                                    'rchannel':card_rchannel,
                                    'formats':card_formats,
                                    'controls': get_controls(card_name)}
                if card_rchannel > 0:
                    cards[card_name]['recording'] = {'description':'microphone level', 'value':0, 'type':'percent', 'lastupdate':0, 'running':False} 
                #card_detail = Popen(["amixer", "-D", "hw:" + card_name, "info"], stdout=PIPE).communicate()[0]

        return cards

def get_controls(card_name):
        try:
            amixer = Popen(['amixer','-D','hw:'+str(card_name)], stdout=PIPE)
            amixer_channels = Popen(["grep", "-e", "control", "-e", "channels"], stdin=amixer.stdout, stdout=PIPE)
            amixer_chandesc = (amixer_channels.communicate()[0]).decode().split("Simple mixer control ")[1:]
            amixer_contents = Popen(['amixer','-D','hw:'+str(card_name), "contents"], stdout=PIPE).communicate()[0].decode()
        except OSError:
            return []

        interfaces = []
        for i in amixer_contents.split("numid=")[1:]:
            lines = i.split("\n")

            interface = {
                "id": int(lines[0].split(",")[0]),
                "iface": lines[0].split(",")[1].replace("iface=", ""),
                "name": lines[0].split(",")[2].replace("name=", '').replace("'", ""),
                "type": lines[1].split(",")[0].replace("  ; type=", ""),
                "access": lines[1].split(",")[1].replace("access=", ""),
            }

            if interface["type"] == "ENUMERATED":
                interface["type"] = "enum"
                items = {}
                for line in lines[2:-2]:
                    pcs = line.split(" '")
                    id = pcs[0].replace("  ; Item #", "")
                    name = pcs[1][:-1]
                    items[id] = name
                interface["items"] = items
                interface["values"] = []
                for value in lines[-2].replace("  : values=", "").split(","):
                    interface["values"].append(int(value))

            elif interface["type"] == "BOOLEAN":
                interface['type'] = 'bool_list'
                interface["values"] = []
                for value in lines[-2].replace("  : values=", "").split(","):
                    interface["values"].append(True if value == "on" else False)

            elif interface["type"] == "INTEGER":
                interface['type'] = 'integer_list'
                interface["min"] = int(lines[1].split(",")[3].replace("min=", ""))
                interface["max"] = int(lines[1].split(",")[4].replace("max=", ""))
                interface["step"] = int(lines[1].split(",")[5].replace("step=", ""))
                line = ""
                for j in reversed(lines):
                    if "  : values=" in j:
                        line = j
                        break
                interface["values"] = []
                interface["channels"] = []
                i = 0
                for value in line.replace("  : values=", "").split(","):
                    interface["values"].append(value)
                    channel_desc = get_channel_name(amixer_chandesc, interface["name"], i)
                    if channel_desc is not None:
                        interface["channels"].append(channel_desc)
                    i += 1
                if len(interface["channels"]) != len(interface["values"]):
                    interface.pop("channels", None)

            if 'w' in interface['access']:
             if interface['iface'] == 'MIXER':
              del interface['iface']
              del interface['access']
              interfaces.append(interface)

        return interfaces


def change_control(card_name, num_id, type, settings):
        if type == 'integer_list':
            command = ['amixer','-D', 'hw:' + str(card_name), "cset", "numid=%s" % num_id, "--", ','.join(str(x) for x in settings)]
        elif type == 'bool_list':
            command = ['amixer','-D', 'hw:' + str(card_name), "cset", "numid=%s" % num_id, "--", ','.join(('on' if x == True else 'off') for x in settings)]
        elif type == 'enum':
            command = ['amixer','-D', 'hw:' + str(card_name), "cset", "numid=%s" % num_id, "--", str(settings)]
        #if os.geteuid() == 0:
        #   call(["alsactl", "store"])
        print(command)




print(json.dumps(get_cards(), sort_keys=True, indent=4))


