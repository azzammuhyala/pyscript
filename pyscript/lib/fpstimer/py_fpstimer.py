from time import monotonic, sleep
from pyscript.core.utils.decorators import immutable, inheritable, singleton

from typing import Optional

@singleton
@immutable
@inheritable
class FPSTimer:

    __slots__ = ()

    _framerate = 60
    _lastTick = 0.0
    _timeElapsed = 0.0
    _rawTime = 0.0
    _framesPerSecond = 0.0

    def __new_singleton__(cls) -> 'FPSTimer':
        global fpstimer
        fpstimer = super(cls, cls).__new__(cls)
        return fpstimer

    def tick(self, framerate: Optional[int | float] = None) -> float:
        currentTime = monotonic()
        framerate = FPSTimer._framerate if framerate is None else framerate
        lastTick = FPSTimer._lastTick
        elapsedTime = currentTime - lastTick

        if framerate > 0:
            minFrameTime = 1 / framerate
            if elapsedTime < minFrameTime:
                sleep(minFrameTime - elapsedTime)

        currentTime = monotonic()

        FPSTimer._timeElapsed = timeElapsed = currentTime - lastTick
        FPSTimer._framesPerSecond = 0.0 if timeElapsed == 0 else 1 / timeElapsed
        FPSTimer._rawTime = elapsedTime
        FPSTimer._lastTick = currentTime

        return timeElapsed

    def get_framerate(self) -> int | float:
        return FPSTimer._framerate

    def get_time(self) -> float:
        return FPSTimer._timeElapsed

    def get_rawtime(self) -> float:
        return FPSTimer._rawTime

    def get_fps(self) -> float:
        return FPSTimer._framesPerSecond

    def set_framerate(self, framerate: int | float) -> None:
        FPSTimer._framerate = framerate

FPSTimer()