#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import errno
from subprocess import call, Popen, PIPE
from functools import partial

class AlsaMixer:

    def __init__(self,  parent=None):

        super(AlsaMixer, self).__init__()
        self.cards = self.get_cards()

    def get_inputs(self) -> dict:
        inputs = dict()

        for key, value in self.cards.items():
            inputs['alsa/' + key] = value

            if value['recording'] != False:
                inputs['alsa/' + key + '/recording'] = value['recording']
                del inputs['alsa/' + key]['recording']

            for subvalue in value['controls']:
                inputs['alsa/' + key + '/control_' + str(subvalue['id'])] = subvalue
            del inputs['alsa/' + key]['controls']

        return inputs

    @staticmethod
    def get_channel_name(desc, name, i):
        for control in desc:
            lines = control.decode().split("\n")
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


    def get_cards(self):
        system_cards = []
        try:
            with open("/proc/asound/cards", 'rt') as f:
                for line in f.readlines():
                    if ']:' in line:
                        system_cards.append(line.strip())
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise e

        cards = {}

        for i in system_cards:
            pos1 = i.find(']:', 0, 30)
            pos0 = i.find('[', 0, 25)
            if pos0 > 0  and pos1 > 0 and pos0 < pos1: 
                card_name = i[pos0+1:pos1].strip()
                card_number = i.split(" [")[0].strip()
                card_desc = i[pos1+2:].strip()
                cards[card_name] = {'id':card_number,
                                    'description':card_desc + ' on/off',
                                    'name':card_name,
                                    'value': False,
                                    'interval': -1,
                                    'type': 'bool',
                                    'recording': self.get_recording(card_name),
                                    'controls': self.get_controls(card_name)}
             #card_detail = Popen(["amixer", "-D", "hw:" + card_name, "info"], stdout=PIPE).communicate()[0]

        return cards


    @staticmethod
    def get_recording(card_name):
        record_details = Popen(["arecord", "-D", "hw:" + card_name,'-c','99', "--dump-hw-params"], stderr=PIPE).communicate()[1]
        record_details = record_details.split(b'\n')
        card_rates = card_formats = card_rchannel = 0
        for x in record_details:
            if x.startswith(b'FORMAT:'):
                card_formats = x[7:].strip()
                if b'[' in card_formats and b']' in card_formats:
                    card_formats = card_formats[1:-1].split(' ')
                else:
                    card_formats = [card_formats]

            elif x.startswith(b'CHANNELS:'):
                card_rchannel = int(x[9:].strip())

            elif x.startswith(b'RATE:'):
                card_rates = x[5:].strip()
                if b'[' in card_rates and b']' in card_rates:
                    card_rates = card_rates[1:-1].split()
                else:
                    card_rates = [card_rates]
                break
        if card_rchannel > 0:
            return {'lastupdate':0,
                    'type': 'percent',
                    'interval' : -1,
                    'description': 'recording volume',
                    'value':0, 'running': False,
                    'rates':card_rates,
                    'channel': card_rchannel,
                    'format':card_formats}

        else: return False


    @staticmethod
    def get_controls(card_name):
        try:
            amixer = Popen(['amixer','-D','hw:'+str(card_name)], stdout=PIPE)
            amixer_channels = Popen(["grep", "-e", "control", "-e", "channels"], stdin=amixer.stdout, stdout=PIPE)
            amixer_chandesc = (amixer_channels.communicate()[0]).split(b"Simple mixer control ")[1:]
            amixer_contents = Popen(['amixer','-D','hw:'+str(card_name), "contents"], stdout=PIPE).communicate()[0]
        except OSError:
            return []

        interfaces = []
        for i in amixer_contents.split(b"numid=")[1:]:
            lines = i.split(b"\n")

            interface = {
                "id": int(lines[0].split(b",")[0]),
                "interval": -1,
                "lastupdate": 0,
                "iface": lines[0].split(b",")[1].replace(b"iface=", b""),
                "description": lines[0].split(b",")[2].replace(b"name=", b'').replace(b"'", b"").decode(),
                "type": lines[1].split(b",")[0].replace(b"  ; type=", b""),
                "access": lines[1].split(b",")[1].replace(b"access=", b""),
            }

            if interface["type"] == b"ENUMERATED":
                interface["type"] = "enum"
                items = {}
                for line in lines[2:-2]:
                    pcs = line.split(b" '")
                    id = pcs[0].replace(b"  ; Item #", b"")
                    name = pcs[1][:-1]
                    items[id] = name.decode()
                interface["items"] = items
                interface["value"] = []
                for value in lines[-2].replace(b"  : values=", b"").split(b","):
                    interface["value"].append(int(value))

            elif interface["type"] == b"BOOLEAN":
                interface['type'] = 'bool_list'
                interface["value"] = []
                for value in lines[-2].replace(b"  : values=", b"").split(b","):
                    interface["value"].append(True if value == b"on" else False)

            elif interface["type"] == b"INTEGER":
                interface['type'] = 'integer_list'
                interface["min"] = int(lines[1].split(b",")[3].replace(b"min=", b""))
                interface["max"] = int(lines[1].split(b",")[4].replace(b"max=", b""))
                interface["step"] = int(lines[1].split(b",")[5].replace(b"step=", b""))
                line = ""
                for j in reversed(lines):
                    if b"  : values=" in j:
                        line = j
                        break
                interface["value"] = []
                interface["channels"] = []
                i = 0
                for value in line.replace(b"  : values=", b"").split(b","):
                    interface["value"].append(value.decode())
                    channel_desc = AlsaMixer.get_channel_name(amixer_chandesc, interface["description"], i)
                    if channel_desc is not None:
                        interface["channels"].append(channel_desc)
                    i += 1
                if len(interface["channels"]) != len(interface["value"]):
                    interface.pop("channels", None)
                else:
                    interface["description"] += ': ' + ', '.join(interface["channels"])

            else:
                break

            if b'w' in interface['access']:
             if interface['iface'] == b'MIXER':
              del interface['iface']
              del interface['access']
              interface['set'] = partial(AlsaMixer.change_control, card_name, interface['id'], interface['type'])
              interfaces.append(interface)

        return interfaces

    @staticmethod
    def change_control(card_name, num_id, type, settings):
        print(card_name, num_id, type, settings)
        if type == 'integer_list':
            command = ['amixer','-D', 'hw:' + str(card_name), "cset", "numid=%s" % num_id, "--", ','.join(str(x) for x in settings)]
        elif type == 'bool_list':
            command = ['amixer','-D', 'hw:' + str(card_name), "cset", "numid=%s" % num_id, "--", ','.join(('on' if x == True else 'off') for x in settings)]
        elif type == 'enum':
            command = ['amixer','-D', 'hw:' + str(card_name), "cset", "numid=%s" % num_id, "--", str(settings)]
        call(command)
        if os.geteuid() == 0:
           call(["alsactl", "store"])
        print(command)


