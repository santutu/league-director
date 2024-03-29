import sys
import json
import functools
import logging.handlers

import leaguedirector
from PySide2.QtNetwork import *

from leaguedirector.bindings.bindings import Bindings
from leaguedirector.bindings.keybindingsWindow import KeybindingsWindow
from leaguedirector.replayApiHostSingleton import ReplayApiHostSingleton
from leaguedirector.enable import *
from leaguedirector.api import Game, Playback, Render, Particles, Recording, Sequence
from leaguedirector.settings import Settings
from leaguedirector.visible.visibleWindow import VisibleWindow
from leaguedirector.widget.floatInput import FloatInput
from leaguedirector.widget.vectorInput import VectorInput
from leaguedirector.sequence.timelineWindow import TimelineWindow
from leaguedirector.widgets import *
from leaguedirector.utils import find_procs_by_name


class SkyboxCombo(QComboBox):
    def showPopup(self):
        appDir = respath('skyboxes')
        userDir = userpath('skyboxes')
        paths = ['']
        paths += [os.path.join(appDir, f) for f in os.listdir(appDir) if f.endswith('.dds')]
        paths += [os.path.join(userDir, f) for f in os.listdir(userDir) if f.endswith('.dds')]
        self.clear()
        for path in sorted(paths):
            self.addItem(os.path.basename(path), path)
        QComboBox.showPopup(self)


class RenderWindow(QScrollArea):
    def __init__(self, api):
        QScrollArea.__init__(self)
        self.api = api
        self.api.render.updated.connect(self.update)
        self.cameraMode = QLabel('')
        self.cameraLockX = BooleanInput('X')
        self.cameraLockY = BooleanInput('Y')
        self.cameraLockZ = BooleanInput('Z')
        self.cameraPosition = VectorInput()
        self.cameraPosition.setSingleStep(10)
        self.cameraRotation = VectorInput([0, -90, -90], [360, 90, 90])
        self.cameraAttached = BooleanInput()
        self.cameraMoveSpeed = FloatInput(0, 5000)
        self.cameraMoveSpeed.setRelativeStep(0.1)
        self.cameraLookSpeed = FloatInput(0.01, 5)
        self.cameraLookSpeed.setSingleStep(0.01)
        self.fieldOfView = FloatInput(0, 180)
        self.nearClip = FloatInput()
        self.nearClip.setRelativeStep(0.05)
        self.farClip = FloatInput()
        self.farClip.setRelativeStep(0.05)
        self.navGrid = FloatInput(-100, 100)
        self.skyboxes = SkyboxCombo()
        self.skyboxRotation = FloatInput(-180, 180)
        self.skyboxOffset = FloatInput(-10000000, 10000000)
        self.skyboxRadius = FloatInput(0, 10000000)
        self.skyboxRadius.setSingleStep(10)
        self.sunDirection = VectorInput()
        self.sunDirection.setSingleStep(0.1)
        self.depthFogEnabled = BooleanInput()
        self.depthFogStart = FloatInput(0, 100000)
        self.depthFogStart.setRelativeStep(0.05)
        self.depthFogEnd = FloatInput(0, 100000)
        self.depthFogEnd.setRelativeStep(0.05)
        self.depthFogIntensity = FloatInput(0, 1)
        self.depthFogIntensity.setSingleStep(0.05)
        self.depthFogColor = ColorInput()
        self.heightFogEnabled = BooleanInput()
        self.heightFogStart = FloatInput(-100000, 100000)
        self.heightFogStart.setSingleStep(100)
        self.heightFogEnd = FloatInput(-100000, 100000)
        self.heightFogEnd.setSingleStep(100)
        self.heightFogIntensity = FloatInput(0, 1)
        self.heightFogIntensity.setSingleStep(0.05)
        self.heightFogColor = ColorInput()
        self.depthOfFieldEnabled = BooleanInput()
        self.depthOfFieldDebug = BooleanInput()
        self.depthOfFieldCircle = FloatInput(0, 300)
        self.depthOfFieldWidth = FloatInput(0, 100000)
        self.depthOfFieldWidth.setSingleStep(100)
        self.depthOfFieldNear = FloatInput(0, 100000)
        self.depthOfFieldNear.setRelativeStep(0.05)
        self.depthOfFieldMid = FloatInput(0, 100000)
        self.depthOfFieldMid.setRelativeStep(0.05)
        self.depthOfFieldFar = FloatInput(0, 100000)
        self.depthOfFieldFar.setRelativeStep(0.05)

        self.cameraLockX.valueChanged.connect(self.api.render.toggleCameraLockX)
        self.cameraLockY.valueChanged.connect(self.api.render.toggleCameraLockY)
        self.cameraLockZ.valueChanged.connect(self.api.render.toggleCameraLockZ)
        self.cameraPosition.valueChanged.connect(functools.partial(self.api.render.set, 'cameraPosition'))
        self.cameraRotation.valueChanged.connect(functools.partial(self.api.render.set, 'cameraRotation'))
        self.cameraAttached.valueChanged.connect(functools.partial(self.api.render.set, 'cameraAttached'))
        self.cameraMoveSpeed.valueChanged.connect(functools.partial(self.api.render.set, 'cameraMoveSpeed'))
        self.cameraLookSpeed.valueChanged.connect(functools.partial(self.api.render.set, 'cameraLookSpeed'))
        self.fieldOfView.valueChanged.connect(functools.partial(self.api.render.set, 'fieldOfView'))
        self.nearClip.valueChanged.connect(functools.partial(self.api.render.set, 'nearClip'))
        self.farClip.valueChanged.connect(functools.partial(self.api.render.set, 'farClip'))
        self.navGrid.valueChanged.connect(functools.partial(self.api.render.set, 'navGridOffset'))
        self.skyboxes.activated.connect(lambda index: self.api.render.set('skyboxPath', self.skyboxes.itemData(index)))
        self.skyboxRotation.valueChanged.connect(functools.partial(self.api.render.set, 'skyboxRotation'))
        self.skyboxRadius.valueChanged.connect(functools.partial(self.api.render.set, 'skyboxRadius'))
        self.skyboxOffset.valueChanged.connect(functools.partial(self.api.render.set, 'skyboxOffset'))
        self.sunDirection.valueChanged.connect(functools.partial(self.api.render.set, 'sunDirection'))
        self.depthFogEnabled.valueChanged.connect(functools.partial(self.api.render.set, 'depthFogEnabled'))
        self.depthFogStart.valueChanged.connect(functools.partial(self.api.render.set, 'depthFogStart'))
        self.depthFogEnd.valueChanged.connect(functools.partial(self.api.render.set, 'depthFogEnd'))
        self.depthFogIntensity.valueChanged.connect(functools.partial(self.api.render.set, 'depthFogIntensity'))
        self.depthFogColor.valueChanged.connect(functools.partial(self.api.render.set, 'depthFogColor'))
        self.heightFogEnabled.valueChanged.connect(functools.partial(self.api.render.set, 'heightFogEnabled'))
        self.heightFogStart.valueChanged.connect(functools.partial(self.api.render.set, 'heightFogStart'))
        self.heightFogEnd.valueChanged.connect(functools.partial(self.api.render.set, 'heightFogEnd'))
        self.heightFogIntensity.valueChanged.connect(functools.partial(self.api.render.set, 'heightFogIntensity'))
        self.heightFogColor.valueChanged.connect(functools.partial(self.api.render.set, 'heightFogColor'))
        self.depthOfFieldEnabled.valueChanged.connect(functools.partial(self.api.render.set, 'depthOfFieldEnabled'))
        self.depthOfFieldDebug.valueChanged.connect(functools.partial(self.api.render.set, 'depthOfFieldDebug'))
        self.depthOfFieldCircle.valueChanged.connect(functools.partial(self.api.render.set, 'depthOfFieldCircle'))
        self.depthOfFieldWidth.valueChanged.connect(functools.partial(self.api.render.set, 'depthOfFieldWidth'))
        self.depthOfFieldNear.valueChanged.connect(functools.partial(self.api.render.set, 'depthOfFieldNear'))
        self.depthOfFieldMid.valueChanged.connect(functools.partial(self.api.render.set, 'depthOfFieldMid'))
        self.depthOfFieldFar.valueChanged.connect(functools.partial(self.api.render.set, 'depthOfFieldFar'))

        widget = QWidget()
        layout = QFormLayout()
        layout.addRow('Camera Mode', self.cameraMode)
        layout.addRow('Camera Lock', HBoxWidget(self.cameraLockX, self.cameraLockY, self.cameraLockZ))
        layout.addRow('Camera Position', self.cameraPosition)
        layout.addRow('Camera Rotation', self.cameraRotation)
        layout.addRow('Camera Attached', self.cameraAttached)
        layout.addRow('Camera Move Speed', self.cameraMoveSpeed)
        layout.addRow('Camera Look Speed', self.cameraLookSpeed)
        layout.addRow('Field of View', self.fieldOfView)
        layout.addRow('Near Clip', self.nearClip)
        layout.addRow('Far Clip', self.farClip)
        layout.addRow('Nav Grid Offset', self.navGrid)
        layout.addRow(Separator())
        layout.addRow('Skybox', self.skyboxes)
        layout.addRow('Skybox Rotation', self.skyboxRotation)
        layout.addRow('Skybox Offset', self.skyboxOffset)
        layout.addRow('Skybox Radius', self.skyboxRadius)
        layout.addRow('Sun Direction', self.sunDirection)
        layout.addRow(Separator())
        layout.addRow('Depth Fog', self.depthFogEnabled)
        layout.addRow('Depth Fog Start', self.depthFogStart)
        layout.addRow('Depth Fog End', self.depthFogEnd)
        layout.addRow('Depth Fog Intensity', self.depthFogIntensity)
        layout.addRow('Depth Fog Color', self.depthFogColor)
        layout.addRow(Separator())
        layout.addRow('Height Fog', self.heightFogEnabled)
        layout.addRow('Height Fog Start', self.heightFogStart)
        layout.addRow('Height Fog End', self.heightFogEnd)
        layout.addRow('Height Fog Intensity', self.heightFogIntensity)
        layout.addRow('Height Fog Color', self.heightFogColor)
        layout.addRow(Separator())
        layout.addRow('Depth of Field', self.depthOfFieldEnabled)
        layout.addRow('Depth of Field Debug', self.depthOfFieldDebug)
        layout.addRow('Depth of Field Circle', self.depthOfFieldCircle)
        layout.addRow('Depth of Field Width', self.depthOfFieldWidth)
        layout.addRow('Depth of Field Near', self.depthOfFieldNear)
        layout.addRow('Depth of Field Mid', self.depthOfFieldMid)
        layout.addRow('Depth of Field Far', self.depthOfFieldFar)
        widget.setLayout(layout)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(widget)
        self.setWindowTitle('Rendering')

    def update(self):
        self.cameraLockX.update(self.api.render.cameraLockX is not None)
        self.cameraLockY.update(self.api.render.cameraLockY is not None)
        self.cameraLockZ.update(self.api.render.cameraLockZ is not None)
        self.cameraLockX.setCheckboxText(
            '{0:.2f}'.format(self.api.render.cameraLockX) if self.api.render.cameraLockX else 'X')
        self.cameraLockY.setCheckboxText(
            '{0:.2f}'.format(self.api.render.cameraLockY) if self.api.render.cameraLockY else 'Y')
        self.cameraLockZ.setCheckboxText(
            '{0:.2f}'.format(self.api.render.cameraLockZ) if self.api.render.cameraLockZ else 'Z')
        self.cameraMode.setText(self.api.render.cameraMode)
        self.cameraPosition.update(self.api.render.cameraPosition)
        self.cameraRotation.update(self.api.render.cameraRotation)
        self.cameraAttached.update(self.api.render.cameraAttached)
        self.cameraMoveSpeed.update(self.api.render.cameraMoveSpeed)
        self.cameraLookSpeed.update(self.api.render.cameraLookSpeed)
        self.fieldOfView.update(self.api.render.fieldOfView)
        self.nearClip.update(self.api.render.nearClip)
        self.farClip.update(self.api.render.farClip)
        self.navGrid.update(self.api.render.navGridOffset)
        self.skyboxRotation.update(self.api.render.skyboxRotation)
        self.skyboxRadius.update(self.api.render.skyboxRadius)
        self.skyboxOffset.update(self.api.render.skyboxOffset)
        self.skyboxOffset.setRange(-self.api.render.skyboxRadius, self.api.render.skyboxRadius)
        self.skyboxOffset.setSingleStep(self.api.render.skyboxRadius / 1000)
        self.sunDirection.update(self.api.render.sunDirection)
        self.depthFogEnabled.update(self.api.render.depthFogEnabled)
        self.depthFogStart.update(self.api.render.depthFogStart)
        self.depthFogEnd.update(self.api.render.depthFogEnd)
        self.depthFogIntensity.update(self.api.render.depthFogIntensity)
        self.depthFogColor.update(self.api.render.depthFogColor)
        self.heightFogEnabled.update(self.api.render.heightFogEnabled)
        self.heightFogStart.update(self.api.render.heightFogStart)
        self.heightFogEnd.update(self.api.render.heightFogEnd)
        self.heightFogIntensity.update(self.api.render.heightFogIntensity)
        self.heightFogColor.update(self.api.render.heightFogColor)
        self.depthOfFieldEnabled.update(self.api.render.depthOfFieldEnabled)
        self.depthOfFieldDebug.update(self.api.render.depthOfFieldDebug)
        self.depthOfFieldCircle.update(self.api.render.depthOfFieldCircle)
        self.depthOfFieldWidth.update(self.api.render.depthOfFieldWidth)
        self.depthOfFieldNear.update(self.api.render.depthOfFieldNear)
        self.depthOfFieldMid.update(self.api.render.depthOfFieldMid)
        self.depthOfFieldFar.update(self.api.render.depthOfFieldFar)


class ParticlesWindow(VBoxWidget):
    def __init__(self, api):
        VBoxWidget.__init__(self)
        self.api = api
        self.api.particles.updated.connect(self.update)
        self.items = {}
        self.search = QLineEdit()
        self.search.setPlaceholderText('Search...')
        self.search.textEdited.connect(self.textEdited)
        self.list = QListWidget()
        self.list.setSortingEnabled(True)
        self.list.itemChanged.connect(self.itemChanged)
        self.addWidget(self.search)
        self.addWidget(self.list)
        self.setWindowTitle('Particles')

    def textEdited(self, text):
        search = text.lower()
        for particle, item in self.items.items():
            if len(search) == 0 or search in particle.lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def itemChanged(self, item):
        particle = item.text()
        enabled = item.checkState() == Qt.Checked
        if enabled != self.api.particles.getParticle(particle):
            self.api.particles.setParticle(particle, enabled)

    def update(self):
        for particle, enabled in self.api.particles.items():
            if particle not in self.items:
                item = QListWidgetItem(particle)
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setBackground(QApplication.palette().toolTipBase())
                self.list.addItem(item)
                self.items[particle] = item
            self.items[particle].setCheckState(Qt.Checked if enabled else Qt.Unchecked)
        for particle in self.items.keys():
            if not self.api.particles.hasParticle(particle):
                self.list.removeItemWidget(self.items.pop(particle))


class RecordingWindow(VBoxWidget):
    def __init__(self, api):
        VBoxWidget.__init__(self)
        self.api = api
        self.api.recording.updated.connect(self.update)
        self.recordings = set()

        self.codec = QComboBox()
        self.codec.addItem('webm')
        self.codec.addItem('png')
        self.startTime = FloatInput(0, 100)
        self.endTime = FloatInput(0, 100)
        self.fps = FloatInput(0, 400)
        self.fps.setValue(60)
        self.lossless = BooleanInput()

        self.outputPath = userpath('recordings')
        self.outputLabel = QLabel()
        self.outputLabel.setTextFormat(Qt.RichText)
        self.outputLabel.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.outputLabel.setOpenExternalLinks(True)

        self.outputButton = QPushButton()
        self.outputButton.setToolTip('Change Output Directory')
        self.outputButton.setFixedWidth(30)
        self.outputButton.setIcon(self.style().standardIcon(QStyle.SP_FileDialogStart))
        self.outputButton.clicked.connect(self.selectOutputDirectory)

        self.button = QPushButton('Record')
        self.button.clicked.connect(self.startRecording)
        self.button2 = QPushButton('Record Sequence')
        self.button2.clicked.connect(self.recordSequence)
        self.list = QListWidget()
        self.list.setSortingEnabled(True)
        self.list.itemDoubleClicked.connect(self.openRecording)

        self.form = QWidget(self)
        self.formLayout = QFormLayout(self.form)
        self.formLayout.addRow('Codec', self.codec)
        self.formLayout.addRow('Start Time', self.startTime)
        self.formLayout.addRow('End Time', self.endTime)
        self.formLayout.addRow('Frames Per Second', self.fps)
        self.formLayout.addRow('Lossless Encoding', self.lossless)
        self.formLayout.addRow('Output Directory', HBoxWidget(self.outputButton, self.outputLabel))
        self.formLayout.addRow(HBoxWidget(self.button, self.button2))
        self.formLayout.addRow(self.list)
        self.form.setLayout(self.formLayout)

        self.render = QWidget(self)
        self.progress = QProgressBar()
        self.cancel = QPushButton('Cancel Recording')
        self.cancel.clicked.connect(self.stopRecording)
        self.renderLayout = QFormLayout()
        self.renderLayout.addRow(QLabel('Rendering video...'))
        self.renderLayout.addRow(self.progress)
        self.renderLayout.addRow(self.cancel)
        self.render.setLayout(self.renderLayout)

        self.addWidget(self.form)
        self.addWidget(self.render)
        self.setWindowTitle('Recording')

    def update(self):
        self.startTime.setRange(0, self.api.playback.length)
        self.endTime.setRange(0, self.api.playback.length)
        self.render.setVisible(self.api.recording.recording)
        self.form.setVisible(not self.api.recording.recording)
        if self.api.recording.recording:
            self.progress.setMinimum(self.api.recording.startTime * 1000)
            self.progress.setMaximum(self.api.recording.endTime * 1000)
            self.progress.setValue(self.api.recording.currentTime * 1000)
            if self.api.recording.path not in self.recordings:
                self.list.addItem(self.api.recording.path)
                self.recordings.add(self.api.recording.path)

    def selectOutputDirectory(self):
        self.setOutputDirectory(QFileDialog.getExistingDirectory(self, 'Select Output Directory', self.outputPath))

    def openRecording(self, item):
        QDesktopServices.openUrl(QUrl('file:///{}'.format(item.text())))

    def stopRecording(self):
        self.api.recording.update({'recording': False})

    def startRecording(self):
        self.api.playback.play()
        self.api.recording.update({
            'recording': True,
            'codec': self.codec.currentText(),
            'startTime': self.startTime.value(),
            'endTime': self.endTime.value(),
            'framesPerSecond': self.fps.value(),
            'enforceFrameRate': True,
            'lossless': self.lossless.value(),
            'path': self.outputPath,
        })

    def setOutputDirectory(self, path):
        if os.path.exists(path):
            self.outputPath = path
            self.outputLabel.setText("<a href=\"file:///{}\">{}</a>".format(path, path))

    def recordSequence(self):
        self.api.sequence.setSequencing(True)
        self.startTime.setValue(self.api.sequence.startTime)
        self.endTime.setValue(self.api.sequence.endTime)
        self.startRecording()

    def saveSettings(self):
        return {'output': self.outputPath}

    def restoreSettings(self, data):
        self.setOutputDirectory(data.get('output', self.outputPath))


class Api(QObject):
    connected = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.wasConnected = False
        self.game = Game()
        self.render = Render()
        self.particles = Particles()
        self.playback = Playback()
        self.recording = Recording()
        self.sequence = Sequence(self.render, self.playback)
        self.game.updated.connect(self.updated)
        self.render.updated.connect(self.updated)
        self.particles.updated.connect(self.updated)
        self.playback.updated.connect(self.updated)
        self.recording.updated.connect(self.updated)

    def updated(self):
        if not self.wasConnected and self.game.connected:
            self.connected.emit()
        self.wasConnected = self.game.connected

    def update(self):
        self.game.update()
        self.render.update()
        self.particles.update()
        self.playback.update()
        self.recording.update()

    def onKeybinding(self, name):
        if name == 'camera_up':
            self.render.moveCamera(z=7)
        elif name == 'camera_down':
            self.render.moveCamera(z=-7)
        elif name == 'camera_move_speed_up':
            self.render.cameraMoveSpeed = self.render.cameraMoveSpeed * 1.2
        elif name == 'camera_move_speed_down':
            self.render.cameraMoveSpeed = self.render.cameraMoveSpeed * 0.8
        elif name == 'camera_look_speed_up':
            self.render.cameraLookSpeed = self.render.cameraLookSpeed * 1.1
        elif name == 'camera_look_speed_down':
            self.render.cameraLookSpeed = self.render.cameraLookSpeed * 0.9
        elif name == 'camera_yaw_left':
            self.render.rotateCamera(x=-1)
        elif name == 'camera_yaw_right':
            self.render.rotateCamera(x=1)
        elif name == 'camera_pitch_up':
            self.render.rotateCamera(y=-1)
        elif name == 'camera_pitch_down':
            self.render.rotateCamera(y=1)
        elif name == 'camera_roll_left':
            self.render.rotateCamera(z=1)
        elif name == 'camera_roll_right':
            self.render.rotateCamera(z=-1)
        elif name == 'camera_lock_x':
            self.render.toggleCameraLockX()
        elif name == 'camera_lock_y':
            self.render.toggleCameraLockY()
        elif name == 'camera_lock_z':
            self.render.toggleCameraLockZ()
        elif name == 'camera_attach':
            self.render.cameraAttached = not self.render.cameraAttached
        elif name == 'camera_fov_up':
            self.render.fieldOfView = self.render.fieldOfView * 1.05
        elif name == 'camera_fov_down':
            self.render.fieldOfView = self.render.fieldOfView * 0.95
        elif name == 'render_dof_near_up':
            self.render.depthOfFieldNear = self.render.depthOfFieldNear * 1.05
        elif name == 'render_dof_near_down':
            self.render.depthOfFieldNear = self.render.depthOfFieldNear * 0.95
        elif name == 'render_dof_mid_up':
            self.render.depthOfFieldMid = self.render.depthOfFieldMid * 1.05
        elif name == 'render_dof_mid_down':
            self.render.depthOfFieldMid = self.render.depthOfFieldMid * 0.95
        elif name == 'render_dof_far_up':
            self.render.depthOfFieldFar = self.render.depthOfFieldFar * 1.05
        elif name == 'render_dof_far_down':
            self.render.depthOfFieldFar = self.render.depthOfFieldFar * 0.95
        elif name == 'play_pause':
            self.playback.paused = not self.playback.paused
        elif name == 'time_minus_120':
            self.playback.adjustTime(-120)
        elif name == 'time_minus_60':
            self.playback.adjustTime(-60)
        elif name == 'time_minus_30':
            self.playback.adjustTime(-30)
        elif name == 'time_minus_10':
            self.playback.adjustTime(-10)
        elif name == 'time_minus_5':
            self.playback.adjustTime(-5)
        elif name == 'time_plus_5':
            self.playback.adjustTime(5)
        elif name == 'time_plus_10':
            self.playback.adjustTime(10)
        elif name == 'time_plus_30':
            self.playback.adjustTime(30)
        elif name == 'time_plus_60':
            self.playback.adjustTime(60)
        elif name == 'time_plus_120':
            self.playback.adjustTime(120)


class ConnectWindow(QDialog):
    def __init__(self, api):
        QDialog.__init__(self)
        self.api = api
        self.setWindowTitle('Ready To Connect')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowModality(Qt.WindowModal)
        self.welcome = QLabel()
        self.welcome.setText("""
            <h3>Welcome to League Director!</h3>
            <p><a href="https://github.com/riotgames/leaguedirector/">https://github.com/riotgames/leaguedirector/</a></p>
            <p>First ensure your game has enabled the <a href="https://developer.riotgames.com/replay-apis.html">Replay API</a> by checking the box next to your installation.</p>
            <p>Once enabled, start up a replay in the League of Legends client and League Director will automatically connect.<br/></p>
        """)
        self.welcome.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.welcome.setTextFormat(Qt.RichText)
        self.welcome.setOpenExternalLinks(True)
        self.layout.addWidget(self.welcome)
        self.list = QListWidget()
        self.list.itemChanged.connect(self.itemChanged)
        self.list.setSortingEnabled(False)
        self.layout.addWidget(self.list)

        self.reloadReplayApiButton = QPushButton("reload replay api")
        self.reloadReplayApiButton.clicked.connect(self.reloadReplayApi)
        self.layout.addWidget(self.reloadReplayApiButton)

        self.testReplayApiButton = QPushButton("test replay api")
        self.testReplayApiButton.clicked.connect(self.testReplayApi)
        self.layout.addWidget(self.testReplayApiButton)

        self.reload()

    def testReplayApi(self):
        time = self.api.playback.time

        msg = QMessageBox()
        msg.setText(f"getting time from replay api  : {time}")
        msg.exec_()

    def reloadReplayApi(self):
        try:
            if ReplayApiHostSingleton.get_instance().find_and_set_host():
                processes = find_procs_by_name("League of Legends.exe")
                msg = QMessageBox()
                msg.setText(
                    f"found host :{ReplayApiHostSingleton.get_instance().get_host()}, process length {len(processes)}")
                msg.exec_()
            else:
                msg = QMessageBox()
                msg.setText("No Found League of Legends on processes")
                msg.exec_()

        except Exception as e:
            msg = QMessageBox()
            msg.setText(f"{e}")
            msg.exec_()

    def sizeHint(self):
        return QSize(400, 100)

    def itemChanged(self, item):
        path = item.text()
        checked = item.checkState() == Qt.Checked
        if checked != isGameEnabled(path):
            setGameEnabled(path, checked)
            self.reload()

    def reload(self):
        self.list.clear()
        for path in findInstalledGames():
            enabled = isGameEnabled(path)
            item = QListWidgetItem(path)
            item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked if enabled else Qt.Unchecked)
            item.setBackground(QApplication.palette().alternateBase())
            item.setStatusTip('Sup!')
            font = item.font()
            font.setPointSize(14)
            font.setBold(enabled)
            item.setFont(font)
            self.list.addItem(item)


class UpdateWindow(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.setWindowTitle('Update Available!')
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setWindowModality(Qt.WindowModal)
        self.welcome = QLabel()
        self.welcome.setText("""
            <h3>A new version of League Director is available!</h3>
            <p><a href="https://github.com/riotgames/leaguedirector/releases/latest">https://github.com/riotgames/leaguedirector/releases/latest</a></p>
            <p>Download the latest version by clicking the link above.</p>
        """)
        self.welcome.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.welcome.setTextFormat(Qt.RichText)
        self.welcome.setOpenExternalLinks(True)
        self.layout.addWidget(self.welcome)


class LeagueDirector(object):
    def __init__(self):
        self.setupLogging()
        self.app = QApplication()
        self.setup()
        sys.exit(self.app.exec_())

    def setup(self):
        self.loadTheme()
        self.window = QMainWindow()
        self.mdi = QMdiArea()
        self.api = Api()
        self.windows = {}
        self.settings = Settings()
        self.bindings = self.setupBindings()
        self.addWindow(RenderWindow(self.api), 'render')
        self.addWindow(ParticlesWindow(self.api), 'particles')
        self.addWindow(VisibleWindow(self.api), 'visible')
        self.addWindow(TimelineWindow(self.api), 'timeline')
        self.addWindow(RecordingWindow(self.api), 'recording')
        self.addWindow(KeybindingsWindow(self.bindings), 'bindings')
        self.addWindow(ConnectWindow(self.api), 'connect')
        self.addWindow(UpdateWindow(), 'update')
        self.window.setCentralWidget(self.mdi)
        self.window.setWindowTitle('League Director')
        self.window.setWindowIcon(QIcon(respath('icon.ico')))
        self.window.closeEvent = self.closeEvent
        self.window.show()
        self.restoreSettings()
        self.checkUpdate()
        self.bindings.triggered.connect(self.api.onKeybinding)
        self.bindings.triggered.connect(self.windows['timeline'].onKeybinding)
        self.bindings.triggered.connect(self.windows['visible'].onKeybinding)
        self.timerUpdate = schedule(500, self.update)
        self.timerSave = schedule(5000, self.saveSettings)
        self.update()

    def closeEvent(self, event):
        self.saveSettings()
        QMainWindow.closeEvent(self.window, event)

    def setupLogging(self):
        logger = logging.getLogger()
        formatter = logging.Formatter('%(asctime)s [%(levelname)-8s] %(message)s')
        path = userpath('logs', 'leaguedirector.log')
        handler = logging.handlers.RotatingFileHandler(path, backupCount=20)
        try:
            handler.doRollover()
        except Exception:
            pass
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logging.info('Started League Director (%s)', leaguedirector.__version__)
        qInstallMessageHandler(self.handleMessage)

    def checkUpdate(self):
        self.updateAvailable = False
        request = QNetworkRequest(QUrl('https://api.github.com/repos/riotgames/leaguedirector/releases/latest'))
        response = self.api.game.manager().get(request)

        def callback():
            if response.error() == QNetworkReply.NoError:
                version = json.loads(response.readAll().data().decode()).get('tag_name')
                if version and version != 'v{}'.format(leaguedirector.__version__):
                    self.updateAvailable = True

        response.finished.connect(callback)

    def handleMessage(self, msgType, msgContext, msgString):
        if msgType == QtInfoMsg:
            logging.info('(QT) %s', msgString)
        elif msgType == QtDebugMsg:
            logging.debug('(QT) %s', msgString)
        elif msgType == QtWarningMsg:
            logging.warning('(QT) %s', msgString)
        elif msgType == QtCriticalMsg:
            logging.critical('(QT) %s', msgString)
        elif msgType == QtFatalMsg:
            logging.critical('(QT) %s', msgString)
        elif msgType == QtSystemMsg:
            logging.critical('(QT) %s', msgString)

    def setupBindings(self):
        return Bindings(self.window, self.settings.value('bindings', {}), [
            ('play_pause', 'Play / Pause', 'Space'),
            ('camera_up', 'Camera Up', ''),
            ('camera_down', 'Camera Down', ''),
            ('camera_yaw_left', 'Camera Yaw Left', ''),
            ('camera_yaw_right', 'Camera Yaw Right', ''),
            ('camera_pitch_up', 'Camera Pitch Up', ''),
            ('camera_pitch_down', 'Camera Pitch Down', ''),
            ('camera_roll_left', 'Camera Roll Left', ''),
            ('camera_roll_right', 'Camera Roll Right', ''),
            ('camera_move_speed_up', 'Camera Move Speed Up', 'Ctrl+='),
            ('camera_move_speed_down', 'Camera Move Speed Down', 'Ctrl+-'),
            ('camera_look_speed_up', 'Camera Look Speed Up', ''),
            ('camera_look_speed_down', 'Camera Look Speed Down', ''),
            ('camera_lock_x', 'Camera Lock X Axis', ''),
            ('camera_lock_y', 'Camera Lock Y Axis', ''),
            ('camera_lock_z', 'Camera Lock Z Axis', ''),
            ('camera_attach', 'Camera Attach', ''),
            ('camera_fov_up', 'Camera Increase Field of View', ''),
            ('camera_fov_down', 'Camera Decrease Field of View', ''),
            ('render_dof_near_up', 'Increase Depth of Field Near', ''),
            ('render_dof_near_down', 'Decrease Depth of Field Near', ''),
            ('render_dof_mid_up', 'Increase Depth of Field Mid', ''),
            ('render_dof_mid_down', 'Decrease Depth of Field Mid', ''),
            ('render_dof_far_up', 'Increase Depth of Field Far', ''),
            ('render_dof_far_down', 'Decrease Depth of Field Far', ''),
            ('show_fog_of_war', 'Show Fog of War', ''),
            ('show_selected_outline', 'Show Selected Outline', ''),
            ('show_hover_outline', 'Show Hover Outline', ''),
            ('show_floating_text', 'Show Floating Text', ''),
            ('show_interface_all', 'Show UI All', ''),
            ('show_interface_replay', 'Show UI Replay', ''),
            ('show_interface_score', 'Show UI Score', ''),
            ('show_interface_scoreboard', 'Show UI Scoreboard', ''),
            ('show_interface_frames', 'Show UI Frames', ''),
            ('show_interface_minimap', 'Show UI Minimap', ''),
            ('show_interface_timeline', 'Show UI Timeline', ''),
            ('show_interface_chat', 'Show UI Chat', ''),
            ('show_interface_target', 'Show UI Target', ''),
            ('show_interface_quests', 'Show UI Quests', ''),
            ('show_interface_announce', 'Show UI Announcements', ''),
            ('show_healthbar_champions', 'Show Health Champions', ''),
            ('show_healthbar_structures', 'Show Health Structures', ''),
            ('show_healthbar_wards', 'Show Health Wards', ''),
            ('show_healthbar_pets', 'Show Health Pets', ''),
            ('show_healthbar_minions', 'Show Health Minions', ''),
            ('show_environment', 'Show Environment', ''),
            ('show_characters', 'Show Characters', ''),
            ('show_particles', 'Show Particles', ''),
            ('sequence_play', 'Play Sequence', 'Ctrl+Space'),
            ('sequence_apply', 'Apply Sequence', '\\'),
            ('sequence_new', 'New Sequence', 'Ctrl+N'),
            ('sequence_copy', 'Copy Sequence', ''),
            ('sequence_clear', 'Clear Sequence', ''),
            ('sequence_del_kf', 'Delete Keyframe', 'Del'),
            ('sequence_next_kf', 'Select Next Keyframe', ''),
            ('sequence_prev_kf', 'Select Prev Keyframe', ''),
            ('sequence_adj_kf', 'Select Adjacent Keyframes', ''),
            ('sequence_all_kf', 'Select All Keyframes', 'Ctrl+A'),
            ('sequence_seek_kf', 'Seek To Keyframe', ''),
            ('sequence_undo', 'Sequence Undo', 'Ctrl+Z'),
            ('sequence_redo', 'Sequence Redo', 'Ctrl+Shift+Z'),
            ('time_minus_120', 'Time -120 Seconds', ''),
            ('time_minus_60', 'Time -60 Seconds', ''),
            ('time_minus_30', 'Time -30 Seconds', ''),
            ('time_minus_10', 'Time -10 Seconds', ''),
            ('time_minus_5', 'Time -5 Seconds', ''),
            ('time_plus_5', 'Time +5 Seconds', ''),
            ('time_plus_10', 'Time +10 Seconds', ''),
            ('time_plus_30', 'Time +30 Seconds', ''),
            ('time_plus_60', 'Time +60 Seconds', ''),
            ('time_plus_120', 'Time +120 Seconds', ''),
            ('kf_position', 'Keyframe Position', '+'),
            ('kf_rotation', 'Keyframe Rotation', '+'),
            ('kf_speed', 'Keyframe Speed', ''),
            ('kf_fov', 'Keyframe Field of View', ''),
            ('kf_near_clip', 'Keyframe Near Clip', ''),
            ('kf_far_clip', 'Keyframe Far Clip', ''),
            ('kf_nav_grid', 'Keyframe Nav Grid Offset', ''),
            ('kf_sky_rotation', 'Keyframe Skybox Rotation', ''),
            ('kf_sky_radius', 'Keyframe Skybox Radius', ''),
            ('kf_sky_offset', 'Keyframe Skybox Offset', ''),
            ('kf_sun_direction', 'Keyframe Sun Direction', ''),
            ('kf_depth_fog_enable', 'Keyframe Depth Fog Enable', ''),
            ('kf_depth_fog_start', 'Keyframe Depth Fog Start', ''),
            ('kf_depth_fog_end', 'Keyframe Depth Fog End', ''),
            ('kf_depth_fog_intensity', 'Keyframe Depth Fog Intensity', ''),
            ('kf_depth_fog_color', 'Keyframe Depth Fog Color', ''),
            ('kf_height_fog_enable', 'Keyframe Height Fog Enable', ''),
            ('kf_height_fog_start', 'Keyframe Height Fog Start', ''),
            ('kf_height_fog_end', 'Keyframe Height Fog End', ''),
            ('kf_height_fog_intensity', 'Keyframe Height Fog Intensity', ''),
            ('kf_height_fog_color', 'Keyframe Height Fog Color', ''),
            ('kf_dof_enabled', 'Keyframe DOF Enabled', ''),
            ('kf_dof_circle', 'Keyframe DOF Circle', ''),
            ('kf_dof_width', 'Keyframe DOF Width', ''),
            ('kf_dof_near', 'Keyframe DOF Near', ''),
            ('kf_dof_mid', 'Keyframe DOF Mid', ''),
            ('kf_dof_far', 'Keyframe DOF Far', ''),
            ('copy_key_frames', 'Copy Key Frames', 'Ctrl+c'),
            ('paste_key_frames', 'Paste Key Frames', 'Ctrl+v'),
        ])

    def addWindow(self, widget, name):
        self.windows[name] = widget
        flags = Qt.Window | Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint
        self.mdi.addSubWindow(widget, flags)
        widget.update()

    def update(self):
        self.api.update()
        self.bindings.setGamePid([self.app.applicationPid(), self.api.game.processID])
        for name, window in self.windows.items():
            if name == 'update':
                window.parent().setVisible(self.updateAvailable)
            elif name == 'connect':
                window.parent().setVisible(not self.api.game.connected)
            else:
                window.parent().setVisible(self.api.game.connected)

    def loadGeometry(self, widget, data):
        if data and len(data) == 4:
            widget.setGeometry(*data)

    def loadState(self, widget, data):
        if data is not None:
            widget.setWindowState(Qt.WindowStates(data))

    def restoreSettings(self):
        self.loadState(self.window, self.settings.value('window/state'))
        self.loadGeometry(self.window, self.settings.value('window/geo'))
        for name, widget in self.windows.items():
            parent = widget.parentWidget()
            self.loadState(parent, self.settings.value('{}/state'.format(name)))
            self.loadGeometry(parent, self.settings.value('{}/geo'.format(name)))
            if hasattr(widget, 'restoreSettings'):
                widget.restoreSettings(self.settings.value('{}/settings'.format(name), {}) or {})

    def saveSettings(self):
        self.settings.setValue('bindings', self.bindings.getBindings())
        self.settings.setValue('window/state', int(self.window.windowState()))
        self.settings.setValue('window/geo', self.window.geometry().getRect())
        for name, widget in self.windows.items():
            parent = widget.parentWidget()
            self.settings.setValue('{}/state'.format(name), int(parent.windowState()))
            self.settings.setValue('{}/geo'.format(name), parent.geometry().getRect())
            if hasattr(widget, 'saveSettings'):
                self.settings.setValue('{}/settings'.format(name), widget.saveSettings())

    def loadTheme(self):
        palette = QPalette()
        palette.setColor(QPalette.WindowText, QColor(180, 180, 180))
        palette.setColor(QPalette.Foreground, QColor(180, 180, 180))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.Light, QColor(80, 80, 80))
        palette.setColor(QPalette.Midlight, QColor(80, 80, 80))
        palette.setColor(QPalette.Mid, QColor(44, 44, 44))
        palette.setColor(QPalette.Dark, QColor(35, 35, 35))
        palette.setColor(QPalette.Text, QColor(190, 190, 190))
        palette.setColor(QPalette.BrightText, QColor(180, 180, 180))
        palette.setColor(QPalette.ButtonText, QColor(180, 180, 180))
        palette.setColor(QPalette.Base, QColor(42, 42, 42))
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.Background, QColor(53, 53, 53))
        palette.setColor(QPalette.Shadow, QColor(20, 20, 20))
        palette.setColor(QPalette.Highlight, QColor(110, 125, 190))
        palette.setColor(QPalette.HighlightedText, QColor(180, 180, 180))
        palette.setColor(QPalette.PlaceholderText, QColor(180, 180, 180))
        palette.setColor(QPalette.Link, QColor(56, 252, 196))
        palette.setColor(QPalette.AlternateBase, QColor(66, 66, 66))
        palette.setColor(QPalette.ToolTipBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipText, QColor(180, 180, 180))
        palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.Highlight, QColor(80, 80, 80))
        palette.setColor(QPalette.Disabled, QPalette.HighlightedText, QColor(127, 127, 127))
        palette.setColor(QPalette.Disabled, QPalette.PlaceholderText, QColor(127, 127, 127))
        self.app.setPalette(palette)
        self.app.setStyle('Fusion')


if __name__ == '__main__':
    try:
        LeagueDirector()
    except Exception as exception:
        logging.exception(exception)
