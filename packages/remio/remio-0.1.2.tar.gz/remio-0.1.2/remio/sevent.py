class Emitter:
    """This class implements a simple event emitter.
    Args:
        emitterIsEnabled: enable callbacks execution?

    Example usage::
        callback = lambda message: print(message)
        event = Emitter()
        event.on('ready', callback)
        event.emit('ready', 'Finished!')
    """

    def __init__(self, emitterIsEnabled: bool = True, *args, **kwargs):
        self.callbacks = None
        self.emitterIsEnabled = emitterIsEnabled

    def on(self, eventName: str = "", callback=None):
        """It sets the callback functions.
        Args:
            eventName: name of the event
            callback: function
        """
        if self.callbacks is None:
            self.callbacks = {}

        if eventName in self.callbacks:
            self.callbacks[eventName].append(callback)
        else:
            self.callbacks[eventName] = [callback]

    def emit(self, eventName: str = "", *args, **kwargs):
        """It emits an event, and calls the corresponding callback function.

        Args:
            eventName: name of the event.
        """
        if self.emitterIsEnabled:
            if self.callbacks is not None and len(eventName) > 0:
                if eventName in self.callbacks:
                    for callback in self.callbacks[eventName]:
                        if callback.__code__.co_argcount > 0:
                            callback(*args, **kwargs)
                        else:
                            callback()

    def clearEvent(self, eventName: str):
        """It clears the callbacks associated to a specific event name.

        Args:
            eventName: name of the event.
        """
        if eventName in self.callbacks:
            del self.callbacks[eventName]

    def clearAllEvents(self):
        """It clears all events."""
        self.callbacks = None

    def disableEvents(self):
        """It disables emit function."""
        self.emitterIsEnabled = False

    def enableEvents(self):
        """It enables emit function."""
        self.emitterIsEnabled = True
