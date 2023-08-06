from functools import partial
from . expr import Parser
from . mqtt import topic


__all__ = ('StateAwareMixin', 'when')


class StateAwareMixin:
    ''' Mixin for stateful skills.
        Status updates are recorded in-memory from MQTT topics,
        e.g. `status/#`.
        The message payload for status updates is JSON-converted if possible.
        The last known state is available in `self.current_state`.
        Subclasses may define handler methods for particular topics,
        e.g. `on_status_lamp_brightness(payload)`.
    '''
    
    conditions = {}
    parser = Parser()
    
    def __init__(self):
        'Register topics and the state callcack.'
        
        super().__init__()
        self.current_state = {}

        status_topic = self.get_config().get('status_topic')
        assert status_topic, 'status_topic not found in configuration'

        # Subscribe to status updates
        register = topic(status_topic, payload_converter=self.decode_json)
        register(self.update_status)


    @staticmethod
    def update_status(self, _userdata, msg):
        ''' Track the global state,
            and invoke handler methods defined by subclasses
            with the message payload.
        '''
        if self.on_status_update(msg.topic, msg.payload):
            self.invoke_handlers(msg.topic, msg.payload)


    def on_status_update(self, topic, payload):
        ''' Keep the global state in-memory.
            Returns a path to the updated attribute in `self.current_state`
            when the state has changed, or `None` otherwise.
        '''
        # Update only if the value has changed
        if self.current_state.get(topic) != payload:
            self.current_state[topic] = payload
            self.log.info('Updated: %s = %s', topic, payload)
            return topic
    
    
    def invoke_handlers(self, topic, payload):
        'Run through conditions and invoke appropriate handlers'
        for expr, action in self.conditions.items():
            if topic not in expr.keys: continue
            
            id = action.func.__name__ if type(action) is partial else action.__name__
            try:
                if expr(self.current_state):
                    self.log.info('Invoking: %s', id)
                    action(self)
                else:
                    self.log.debug('Skipping: %s', id)
            except KeyError as e:
                self.log.warning('KeyError in %s: %s', id, e)


def when(expression):
    'Decorator for status handlers.'
    
    predicate = StateAwareMixin.parser.parse(expression)
    
    def wrapper(method):
        StateAwareMixin.conditions[predicate] = method
        return method
    return wrapper
