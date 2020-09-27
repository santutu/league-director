import functools

from PySide2.QtCore import Qt
from PySide2.QtWidgets import QScrollArea, QWidget, QFormLayout

from leaguedirector.widgets import BooleanInput


class VisibleWindow(QScrollArea):
    options = [
        ('fogOfWar', 'show_fog_of_war', 'Show Fog Of War?'),
        ('outlineSelect', 'show_selected_outline', 'Show Selected Outline?'),
        ('outlineHover', 'show_hover_outline', 'Show Hover Outline?'),
        ('floatingText', 'show_floating_text', 'Show Floating Text?'),
        ('interfaceAll', 'show_interface_all', 'Show UI?'),
        ('interfaceReplay', 'show_interface_replay', 'Show UI Replay?'),
        ('interfaceScore', 'show_interface_score', 'Show UI Score?'),
        ('interfaceScoreboard', 'show_interface_scoreboard', 'Show UI Scoreboard?'),
        ('interfaceFrames', 'show_interface_frames', 'Show UI Frames?'),
        ('interfaceMinimap', 'show_interface_minimap', 'Show UI Minimap?'),
        ('interfaceTimeline', 'show_interface_timeline', 'Show UI Timeline?'),
        ('interfaceChat', 'show_interface_chat', 'Show UI Chat?'),
        ('interfaceTarget', 'show_interface_target', 'Show UI Target?'),
        ('interfaceQuests', 'show_interface_quests', 'Show UI Quests?'),
        ('interfaceAnnounce', 'show_interface_announce', 'Show UI Announcements?'),
        ('healthBarChampions', 'show_healthbar_champions', 'Show Health Champions?'),
        ('healthBarStructures', 'show_healthbar_structures', 'Show Health Structures?'),
        ('healthBarWards', 'show_healthbar_wards', 'Show Health Wards?'),
        ('healthBarPets', 'show_healthbar_pets', 'Show Health Pets?'),
        ('healthBarMinions', 'show_healthbar_minions', 'Show Health Minions?'),
        ('environment', 'show_environment', 'Show Environment?'),
        ('characters', 'show_characters', 'Show Characters?'),
        ('particles', 'show_particles', 'Show Particles?'),
    ]

    def __init__(self, api):
        QScrollArea.__init__(self)
        self.api = api
        self.api.render.updated.connect(self.update)
        self.api.connected.connect(self.connect)
        self.inputs = {}
        self.bindings = {}
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWindowTitle('Visibility')
        widget = QWidget()
        layout = QFormLayout()
        for name, binding, label in self.options:
            self.inputs[name] = BooleanInput()
            self.inputs[name].setValue(True)
            self.inputs[name].valueChanged.connect(functools.partial(self.api.render.set, name))
            self.bindings[binding] = name
            layout.addRow(label, self.inputs[name])
        widget.setLayout(layout)
        self.setWidget(widget)

    def connect(self):
        for name, field in self.inputs.items():
            self.api.render.set(name, field.value())

    def update(self):
        for name, field in self.inputs.items():
            field.setValue(self.api.render.get(name))

    def restoreSettings(self, data):
        for name, value in data.items():
            if name in self.inputs:
                self.inputs[name].update(value)
                self.api.render.set(name, value)

    def saveSettings(self):
        return {name: self.api.render.get(name) for name in self.inputs}

    def onKeybinding(self, name):
        if name in self.bindings:
            self.inputs[self.bindings[name]].toggle()