#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import errno
from subprocess import call, Popen, PIPE, DEVNULL
from functools import partial
from hardware.AlsaRecord import AlsaRecord
from core.DataTypes import DataType


class AlsaMixer:

    def __init__(self, inputs,
                 settings):

        super(AlsaMixer, self).__init__()
        self.settings = settings
        self.inputs = inputs
        self.recorder = dict()
        self.system_cards = []
        self.cards = self.get_cards()
        self.inputs.add(self.get_inputs())

    def get_inputs(self) -> dict:
        return self.cards

    def delete_inputs(self):
        for key in self.cards:
            if key in self.inputs.entries:
                del self.inputs.entries[key]

    def play(self, file='/usr/share/sounds/alsa/Front_Center.wav'):
        for key in self.system_cards:
            if self.cards[key]['value'] is True:
                call(["aplay", "-D", "plughw:" + self.cards[key]['name'], file])

    @staticmethod
    def get_channel_name(desc, name, i):
        for control in desc:
            lines = control.decode().split("\n")
            pos = (lines[0][1:]).find("',")
            if pos > -1:
                control_name = (lines[0][1:pos + 1])

                if control_name not in name:
                    continue

            for line in lines[1:]:
                if name.split(" ")[-2] in line:
                    names = line.split(": ")[1].split(" - ")
                    return names[i]

        return None

    def get_cards(self):
        self.system_cards = []
        try:
            with open("/proc/asound/cards", 'r') as f:
                line = True
                while line:
                    line = f.readline()
                    if ']:' in line:
                        self.system_cards.append(line.strip())
        except IOError as e:
            logging.error(str(e))
            if e.errno != errno.ENOENT:
                raise e

        cards = {}

        for i in self.system_cards:
            pos1 = i.find(']:', 0, 30)
            pos0 = i.find('[', 0, 25)
            if 0 < pos0 < pos1 and pos1 > 0:
                card_name = i[pos0 + 1:pos1].strip()
                card_number = i.split(" [")[0].strip()
                card_desc = i[pos1 + 2:].strip()
                cards['alsa/' + card_name] = {  # 'id': card_number,
                    'description': card_desc + ' on/off',
                    # 'name': card_name,
                    'value': self.settings.value("alsa/" + card_name, 1),
                    'interval': -1,
                    'set': partial(self.power_device, card_name),
                    'type': DataType.BOOL}
                cards.update(self.get_recording(card_name))
                cards.update(self.get_controls(card_name))

        return cards

    def power_device(self, card_name, value):

        if 'alsa/' + card_name in self.cards:
            self.cards['alsa/' + card_name]['value'] = int(value)
            self.settings.setValue("alsa/" + card_name, value)

    def get_recording(self, card_name):
        record_details = Popen(["arecord", "-D", "hw:" + card_name,
                                '-c', '99', "--dump-hw-params"], stderr=PIPE).communicate()[1]
        record_details = record_details.split(b'\n')
        card_rates = card_formats = card_rchannel = 0

        for x in record_details:
            if x.startswith(b'FORMAT:'):
                card_formats = x[7:].strip()
                if b'[' in card_formats and b']' in card_formats:
                    card_formats = card_formats[1:-1].split(b' ')
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

            self.recorder[card_name] = AlsaRecord(self.inputs, card_name)

            return self.recorder[card_name].get_inputs()

        else:
            return {}

    @staticmethod
    def get_controls(card_name):
        try:
            amixer = Popen(
                ['amixer', '-D', 'hw:' + str(card_name)], stdout=PIPE)
            amixer_channels = Popen(
                ["grep", "-e", "control", "-e", "channels"], stdin=amixer.stdout, stdout=PIPE)
            amixer_chandesc = (amixer_channels.communicate()[0]).split(
                b"Simple mixer control ")[1:]
            amixer_contents = Popen(
                ['amixer', '-D', 'hw:' + str(card_name), "contents"], stdout=PIPE).communicate()[0]
        except OSError as e:
            logging.error(str(e))
            return {}

        interfaces = dict()
        for a in amixer_contents.split(b"numid=")[1:]:
            lines = a.split(b"\n")

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
                interface["type"] = DataType.ENUM
                items = []
                for line in lines[2:-2]:
                    pcs = line.split(b" '")
                    # id = pcs[0].replace(b"  ; Item #", b"")
                    name = pcs[1][:-1]
                    items.append(name.decode())
                interface["available"] = items
                values = []
                channels = []
                i = 0
                for value in lines[-2].replace(b"  : values=", b"").split(b","):
                    values.append(int(value))
                    channel_desc = AlsaMixer.get_channel_name(
                        amixer_chandesc, interface["description"], i)
                    if channel_desc is not None:
                        channels.append(channel_desc)
                    i += 1

            elif interface["type"] == b"BOOLEAN":
                interface['type'] = DataType.BOOL
                values = []
                channels = []
                i = 0
                for value in lines[-2].replace(b"  : values=", b"").split(b","):
                    values.append(1 if value == b"on" else 0)
                    channel_desc = AlsaMixer.get_channel_name(
                        amixer_chandesc, interface["description"], i)
                    if channel_desc is not None:
                        channels.append(channel_desc)
                    i += 1

            elif interface["type"] == b"INTEGER":
                interface['type'] = DataType.INT
                interface["min"] = int(lines[1].split(
                    b",")[3].replace(b"min=", b""))
                interface["max"] = int(lines[1].split(
                    b",")[4].replace(b"max=", b""))
                interface["step"] = float(
                    lines[1].split(b",")[5].replace(b"step=", b""))
                line = ""
                for j in reversed(lines):
                    if b"  : values=" in j:
                        line = j
                        break
                values = []
                channels = []
                i = 0
                for value in line.replace(b"  : values=", b"").split(b","):
                    values.append(value.decode())
                    channel_desc = AlsaMixer.get_channel_name(
                        amixer_chandesc, interface["description"], i)
                    if channel_desc is not None:
                        channels.append(channel_desc)
                    i += 1

            else:
                break

            if b'w' in interface['access']:
                if interface['iface'] == b'MIXER':

                    del interface['iface']
                    del interface['access']
                    i = 0
                    description = interface['description']
                    for value in values:
                        interface['value'] = value
                        interface['description'] = description

                        if len(channels) > i:
                            interface['description']  +=  ' ' + channels[i]


                        interface['set'] = partial(
                            AlsaMixer.change_control, card_name, interface['id'], i, len(values))

                        interfaces[f"alsa/{card_name}/control/{interface['id']}/{i}"] = (
                            interface.copy())
                        del interfaces[f"alsa/{card_name}/control/{interface['id']}/{i}"]['id']
                        i += 1

        return interfaces

    @staticmethod
    def change_control(card_name, num_id, channel, channelcount, settings):
        logging.debug(f'{card_name},{num_id},{channel},{channelcount},{settings}')
        if channelcount != 1:
            settings = (channel * ',') + str(settings) + \
                       ((channelcount - channel - 1) * ',')

        command = ['amixer', '-D', 'hw:' +
                   str(card_name), "cset", "numid=%s" % num_id, "--", str(settings)]
        call(command, stdout=DEVNULL)
        if os.geteuid() == 0:
            call(["alsactl", "store"])
