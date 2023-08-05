Basic Finite State Machine (FSM) tools.

*Latest release 20220805.1*:
* FSM: subclass DOTNodeMixin and provide a hook for a colour palette for node fillcolors.
* Other minor changes.

## Class `FSM(cs.gvutils.DOTNodeMixin)`

Base class for a finite state machine (FSM).

The allowed states and transitions are defined by the class
attribute `FSM_TRANSITIONS`, a mapping of
*state*->*event*->*new_state*.

Each instance has the following attributes:
* `fsm_state`: the current state value.
* `fsm_history`: an optional iterable of `FSMTransitionEvent`
  state transitions recorded by the `fsm_event` method.
  Usually this would be `None` (the default) or a `list`.

*Method `FSM.__init__(self, state, *, history=None, lock=None, transitions=None)`*:
Initialise the `FSM` from:
* `state`: the initial state
* `history`: an optional object to record state transition
  history, default `None`; if not `None` this should be an
  iterable object with a `.append(entry)` method such as a
  `list`.
* `lock`: an optional mutex to control access;
  if presupplied and shared with the caller
  it should probably be an `RLock`;
  the default is a `Lock`, which is enough for `FSM` private use
* `transitions`: optional *state*->*event*->*state* mapping;
  if provided, this will override the class `FSM_TRANSITIONS` mapping

*Method `FSM.__getattr__(self, attr)`*:
Provide the following attributes:
- present the state names as attributes, for example:
  `self.PENDING=='PENDING'` if there is a `'PENDING'` state
- present `is_`*statename* as a Boolean testing whether
  `self.fsm_state==`*statename*`.upper()`
- a callable calling `self.fsm_event(attr)` if `attr`
  is an event name for the current state
Fall back to the superclass `__getattr__`.

*Method `FSM.dot_node_attrs(self)`*:
DOT Node attributes.

*Method `FSM.dot_node_fillcolor(self) -> Optional[str]`*:
The default DOT node `fillcolor`.
Return a color name or `None`.

This implementation looks up `self.fsm_state`
in `self.DOT_NODE_FILLCOLOR_PALETTE` if that exists.
A default color can be provided with the key `None`
in the palette mapping.

*Method `FSM.fsm_callback(self, state, callback)`*:
Register a callback to be called immediately on transition
to `state` as `callback(self,FSMEventTransition)`.
The special `state` value `FSM.FSM_ANY_STATE` may be supplied
to register a callback which fires for every state transition.

    >>> fsm = FSM('state1',transitions={
    ...   'state1':{'ev_a':'state2'},
    ...   'state2':{'ev_b':'state1'},
    ... })
    >>> fsm.fsm_callback('state2',lambda task, transition: print(task, transition))
    >>> fsm.fsm_callback(FSM.FSM_ANY_STATE,lambda task, transition: print("ANY", task, transition))
    >>> fsm.ev_a(foo=3) # doctest: +ELLIPSIS
    ANY FSM:state2 FSMTransitionEvent(old_state='state1', new_state='state2', event='ev_a', when=..., extra={'foo': 3})
    FSM:state2 FSMTransitionEvent(old_state='state1', new_state='state2', event='ev_a', when=..., extra={'foo': 3})
    'state2'
    >>> fsm.ev_b(foo=4) # doctest: +ELLIPSIS
    ANY FSM:state1 FSMTransitionEvent(old_state='state2', new_state='state1', event='ev_b', when=..., extra={'foo': 4})
    'state1'

*Method `FSM.fsm_callback_discard(self, state, callback)`*:
Deregister a callback for `state`.

*Property `FSM.fsm_dot`*:
A DOT syntax description of `self.FSM_TRANSITIONS`.

*Method `FSM.fsm_event(self, event, **extra)`*:
Transition the FSM from the current state to a new state based on `event`.
Call any callbacks associated with the new state.
Returns the new state.

Optional information may be passed as keyword arguments.

A `transition` instance of `FSMTransitionEvent` is created
with the following attributes:
* `old_state`: the state when `fsm_event` was called
* `new_state`: the new state
* `event`: the `event`
* `when`: a UNIX timestamp from `time.time()`
* `extra`: a `dict` with the `extra` information
If `self.fsm_history` is not `None`,
`transition` is appended to it.
If there are callbacks for `new_state` or `FSM.FSM_ANY_STATE`,
call each callback as `callback(self,transition)`.

*Property `FSM.fsm_events`*:
Return a list of the events valid for the current state.

*Method `FSM.fsm_print(self, file=None, fmt=None, layout=None, **dot_kw)`*:
Print the state transition diagram to `file`, default `sys.stdout`,
in format `fmt` using the engine specified by `layout`, default `'dot'`.
This is a wrapper for `cs.gvutils.gvprint`.

*Method `FSM.fsm_transitions_as_dot(fsm_transitions, sep='\n', graph_name=None)`*:
Compute a DOT syntax graph description from a transitions dictionary.

        Parameters:
        * `fsm_transitions`: a mapping of *state*->*event*->*state*
        * `sep`: optional separator between "lines", default `'
'`
        * `graph_name`: optional name for the graph, default the class name

## Class `FSMError(builtins.Exception, builtins.BaseException)`

An exception associated with an `FSM`.

These have a `.fsm` attribute storing an (optional) `FSM`
reference supplied at initialisation.

## `FSMSubType = ~FSMSubType`

Type variable.

Usage::

  T = TypeVar('T')  # Can be anything
  A = TypeVar('A', str, bytes)  # Must be str or bytes

Type variables exist primarily for the benefit of static type
checkers.  They serve as the parameters for generic types as well
as for generic function definitions.  See class Generic for more
information on generic types.  Generic functions work as follows:

  def repeat(x: T, n: int) -> List[T]:
      '''Return a list containing n references to x.'''
      return [x]*n

  def longest(x: A, y: A) -> A:
      '''Return the longest of two strings.'''
      return x if len(x) >= len(y) else y

The latter example's signature is essentially the overloading
of (str, str) -> str and (bytes, bytes) -> bytes.  Also note
that if the arguments are instances of some subclass of str,
the return type is still plain str.

At runtime, isinstance(x, T) and issubclass(C, T) will raise TypeError.

Type variables defined with covariant=True or contravariant=True
can be used to declare covariant or contravariant generic types.
See PEP 484 for more details. By default generic types are invariant
in all type variables.

Type variables can be introspected. e.g.:

  T.__name__ == 'T'
  T.__constraints__ == ()
  T.__covariant__ == False
  T.__contravariant__ = False
  A.__constraints__ == (str, bytes)

Note that only type variables defined in global scope can be pickled.

## Class `FSMTransitionEvent(builtins.tuple)`

FSMTransitionEvent(old_state, new_state, event, when, extra)

*Property `FSMTransitionEvent.event`*:
Alias for field number 2

*Property `FSMTransitionEvent.extra`*:
Alias for field number 4

*Property `FSMTransitionEvent.new_state`*:
Alias for field number 1

*Property `FSMTransitionEvent.old_state`*:
Alias for field number 0

*Property `FSMTransitionEvent.when`*:
Alias for field number 3

# Release Log



*Release 20220805.1*:
* FSM: subclass DOTNodeMixin and provide a hook for a colour palette for node fillcolors.
* Other minor changes.

*Release 20220805*:
Initial PyPI release.
