#!/usr/bin/env python3
import sys
import os
import time
from subprocess import check_output, call, Popen, PIPE, DEVNULL
from PySide2.QtCore import QSettings, Qt, QModelIndex, QAbstractListModel, Property, Signal, Slot, QObject
from core.DataTypes import DataType
import logging

from core.Property import EntityProperty, ThreadProperty


class Git(QObject):

    version = "1.0"
    required_packages = None
    allow_instances = False
    allow_maininstance = True
    description = "Git module for managing sofware updates"

    def __init__(self, settings):

        super().__init__()
        self.settings = settings
        self.properties = dict()
        self.properties['module'] = EntityProperty(parent=self,
                                                   category='module',
                                                   entity='core',
                                                   name='git',
                                                   value='NOT_INITIALIZED',
                                                   description='Git update module',
                                                   type=DataType.MODULE,
                                                   call=self.update,
                                                   interval=6000)

        self._git_path = settings.value('git/remote_path', 'https://github.com/shpi/qmlui')
        self._updates_remote = 0
        self._updates_local = 0
        self._update_hex = ''
        self._update_shex = ''
        self._update_timestamp = 0
        self._update_description = ''




        # git path
        # git remote path

        # git rev-list --left-right --count origin/main...main
        # git branch --show-current
        # git branch -r
        #
        # git log -3 --pretty=format:"%H;%h;%at;%s"
        # git log -1 --pretty=format:"%H;%h;%at;%s" HEAD...origin/main

        # git show -s --format=%ct -> date

        # git revert -m 1 hASH

    @Signal
    def gitChanged(self):
            pass
    @Slot()
    def update(self):
         #git fetch --all
         try:
          a = check_output(['git', 'fetch', '--all'],stderr=PIPE).decode()
          logging.info(str(a))
         except Exception as e:
             logging.error(str(e))
         self.check_updates()
         self.latest_update()
         self.gitChanged.emit()


    def get_inputs(self):
             return self.properties.values()


    def check_updates(self):
        output = check_output(['git','rev-list', '--left-right', '--count', 'origin/main...main']).strip(b'\n').split(b'\t')
        self._updates_remote = int(output[0])
        self._updates_local = int(output[1])

    def latest_update(self):
        if self._updates_remote > 0:
            output = check_output(['git','log', '-1', '--pretty=format:"%H;%h;%at;%s"', 'HEAD...origin/main']).decode().strip('\n').split(';')
            self._update_hex = output[0]
            self._update_shex = output[1]
            self._update_timestamp = int(output[2])
            self._update_description = output[3]


    @Property(str, notify=gitChanged)
    def update_hex(self):
        return self._update_hex

    @Property(str, notify=gitChanged)
    def update_shex(self):
        return self._update_shex

    @Property(int, notify=gitChanged)
    def update_timestamp(self):
        return self._update_timestamp

    @Property(str, notify=gitChanged)
    def update_description(self):
        return self._update_description

    @Property(str, notify=gitChanged)
    def actual_branch(self):
        return check_output(['git','branch', '--show-current']).decode().strip()

    @Property('QVariantList', notify=gitChanged)
    def available_branches(self):
        return check_output(['git','branch', '-r']).decode().strip().split('\n')

    @Property(int, notify=gitChanged)
    def actual_version(self):
        return int(check_output(['git','show', '-s','--format=%ct']).decode().strip())

    @Slot()
    def reboot(self):
        os.system('reboot')
        os.system('sudo reboot')

    @Slot(result=str)
    def merge(self):
            return check_output(['git','merge']).decode().strip()

    @Property(int, notify=gitChanged)
    def updates_remote(self):
        return self._updates_remote


    @Property(int, notify=gitChanged)
    def updates_local(self):
        return self._updates_local

