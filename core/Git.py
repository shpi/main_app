#!/usr/bin/env python3
import logging
import os
from subprocess import check_output, PIPE
from pathlib import Path

from PySide2.QtCore import Property, Signal, Slot, QObject

from interfaces.DataTypes import DataType
from core.Property import EntityProperty
from core.Settings import settings
from core.Constants import GIT_CLONE_PATH


class Git(QObject):
    allow_instances = False
    allow_maininstance = True
    description = "Git module for managing sofware updates"

    def __init__(self, app_path: Path):
        super().__init__()
        self.app_path = app_path
        self.git_dir = app_path / '.git'
        self.properties = {}
        self.properties['module'] = EntityProperty(parent=self,
                                                   category='module',
                                                   entity='core',
                                                   name='git',
                                                   value='NOT_INITIALIZED',
                                                   description='Git update module',
                                                   type=DataType.EXECUTE_ONLY,
                                                   call=self.update,
                                                   interval=6000)

        self._git_path = settings.str('git/remote_path', GIT_CLONE_PATH)
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

    def is_git(self) -> bool:
        return self.git_dir.is_dir()

    @Signal
    def gitChanged(self):
        pass

    @Slot()
    def update(self):
        if not self.is_git():
            logging.info('Skipping update() because of ".git" directory missing.')
            return

        # git fetch --all
        try:
            a = check_output(['git', 'fetch', '--all'], stderr=PIPE).decode()
            logging.info(str(a))
        except Exception as e:
            logging.error(str(e))
        self.check_updates()
        self.latest_update()
        self.gitChanged.emit()

    def get_inputs(self):
        return self.properties.values()

    def check_updates(self):
        if not self.is_git():
            logging.info('Skipping check_updates() because of ".git" directory missing.')
            return

        output = check_output(['git', 'rev-list', '--left-right', '--count', 'origin/main...main']).strip(b'\n').split(
            b'\t')
        self._updates_remote = int(output[0])
        self._updates_local = int(output[1])

    def latest_update(self):
        if not self.is_git():
            logging.info('Skipping latest_update() because of ".git" directory missing.')
            return

        if self._updates_remote > 0:
            output = check_output(
                ['git', 'log', '-1', '--pretty=format:"%H;%h;%at;%s"', 'HEAD...origin/main']).decode().strip(
                '\n').split(';')
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
        if self.is_git():
            return check_output(['git', 'branch', '--show-current']).decode().strip()
        return ""

    @Property('QVariantList', notify=gitChanged)
    def available_branches(self):
        if self.is_git():
            return check_output(['git', 'branch', '-r']).decode().strip().split('\n')
        return ""

    @Property(int, notify=gitChanged)
    def current_version_date(self):
        if self.is_git():
            return int(check_output(['git', 'show', '-s', '--format=%ct']).decode().strip())
        return 0

    @Property(str, notify=gitChanged)
    def current_version_hex(self):
        if self.is_git():
            return check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()
        return ""

    @Slot()
    def reboot(self):
        os.system('reboot')
        os.system('sudo reboot')

    @Slot(result=str)
    def merge(self):
        if self.is_git():
            return check_output(['git', 'merge']).decode().strip()

    @Property(int, notify=gitChanged)
    def updates_remote(self):
        return self._updates_remote

    @Property(int, notify=gitChanged)
    def updates_local(self):
        return self._updates_local
