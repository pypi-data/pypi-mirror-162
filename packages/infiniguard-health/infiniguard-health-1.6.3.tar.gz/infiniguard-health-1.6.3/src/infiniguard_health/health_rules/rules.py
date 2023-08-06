import logging
import math
from dataclasses import dataclass, field
from numbers import Number
from typing import Type, List, Callable

from iba_install.lib.infinisafe_recovery import InfiniSafeRecoveryManager
from infi.caching import cached_function

from infiniguard_health.blueprints.components import (
    EthernetPorts,
    ComponentState,
    FcPorts,
    SYSTEM_COMPONENT_NAMES,
    ComponentContainer,
    SystemState,
    Bonds, SnapshotsCapacity,
    Snapshots, DDECapacity, Policies, Component
)
from infiniguard_health.event_engine import events
from infiniguard_health.event_engine.event_engine_infra import EventEngine
from infiniguard_health.event_engine.events import (
    BondDownEvent,
    BondUpEvent,
    ComponentNotFoundEvent,
    Event,
    SnapshotCapacityNormal,
    SnapshotCapacityHigh,
    SnapshotCapacityVeryHigh,
    SnapshotCapacityCriticallyHigh,
    SnapshotCapacityExhausted,
    DDECapacityNormal,
    DDECapacityHigh,
    DDECapacityVeryHigh,
    DDECapacityCriticallyHigh,
    MissingData,
    SnapshotNotDeletedEvent,
    AllSnapshotsPositiveEvent,
    SnapshotBadExpirationValue,
    SnapshotNotLocked,
    SnapshotBadCreationValue, SnapshotOverdue, ExcessiveSnapshots, NumSnapshotsOk,
    SnapshotsNumHigh, SnapshotsNumDangerous, SnapshotsNumCritical, SnapshotsNumDepleted
)
from infiniguard_health.message_queue.message_queue_infra import (
    MessageQueue, VALIDATE_NEW_SYSTEM_STATE_MESSAGE,
)
from infiniguard_health.utils import (
    Singleton, snake_case_to_camel_case, get_all_subclasses,
    get_infiniguard_health_start_time, get_default_policy_type,
    is_standby_app, get_default_policy
)

_logger = logging.getLogger(__name__)

"""
Instructions for adding a new rule:

Adding a new (non-generic) rule requires sublclassing the Rule class.

The new subclass must implement the following:

1. Set variable component_name with the component that the rule is in change of (e.g 'ethernet_ports'). 
This must be the same name that exists in the SystemState's dictionary. An easy way to accomplish this is to use
the name that exists in the Munch SYSTEM_COMPONENT_NAMES

2. Set variable component_change_message to be the message that the rule should subscribe on in the message queue.
When this message is published, the rule will be executed. It's best to take this directly from the relevant 
Component object.

3. Set variable state_when_component_not_valid to the state (e.g ComponentState.WARNING) that the component should
get if the rule determines that the state is not valid. If it is valid - the rule will always set the component's 
state to ComponentState.NORMAL.

4. Set variable component_positive_event to the Event class that should be emitted whenever the component is 
discovered to be in a healthy state (at the start of the system's run, and when moving from invalid to valid)

5. Set variable event_when_component_not_valid to the Event class that should be emitted whenever the component is
discovered to be in an invalid state (e.g a port's link is down). 

6. Implement method is_component_in_valid_state(component). This method receives an individual component
(e.g bmc component or single FC port) and returns a boolean indicating if this component is valid. If valid - will
produce a positive event. If invalid - will produce a negative event.

7. (optional) - override execute_rule_for_individual_component in order to further specify the rule's logic. 
Remember to call super's method at the start.   


Any component that doesn't have a specific subclass rule will have a generic rule defined for it, which checks if the
component is missing, and if not sets its state to ComponentState.NORMAL.
"""

STATE_FOR_MISSING_COMPONENT = ComponentState.ERROR
STATE_FOR_MISSING_DATA = ComponentState.ERROR
STATE_FOR_VALID_DATA = ComponentState.NORMAL
STATE_FOR_ETH_PORT_DOWN = ComponentState.WARNING
STATE_FOR_BOND_DOWN = ComponentState.WARNING
STATE_FOR_FC_PORT_DOWN = ComponentState.WARNING
STATE_FOR_PSU_DOWN = ComponentState.ERROR
STATE_FOR_DIMM_DOWN = ComponentState.WARNING
STATE_FOR_FAN_SPEED_WARNING = ComponentState.WARNING
STATE_FOR_FAN_SPEED_ERROR = ComponentState.ERROR
STATE_FOR_SNAPSHOTS_CAPACITY_LIMITED = ComponentState.WARNING
STATE_FOR_SNAPSHOTS_CAPACITY_HIGH = ComponentState.ERROR
STATE_FOR_SNAPSHOTS_CAPACITY_CRITICALLY_HIGH = ComponentState.CRITICAL
STATE_FOR_SNAPSHOTS_CAPACITY_EXHAUSTED = ComponentState.CRITICAL
STATE_FOR_DDE_CAPACITY_LIMITED = ComponentState.WARNING
STATE_FOR_DDE_CAPACITY_HIGH = ComponentState.ERROR
STATE_FOR_DDE_CAPACITY_CRITICALLY_HIGH = ComponentState.CRITICAL
STATE_FOR_SNAPSHOT_BAD_VALUES = ComponentState.CRITICAL
STATE_FOR_SNAPSHOTS_NUM_HIGH = ComponentState.WARNING
STATE_FOR_SNAPSHOTS_NUM_DANGEROUS = ComponentState.ERROR
STATE_FOR_SNAPSHOTS_NUM_CRITICAL = ComponentState.CRITICAL
STATE_FOR_SNAPSHOTS_NUM_DEPLETED = ComponentState.CRITICAL


class UndefinedFCPortRole(Exception):
    pass


def get_events_to_emit(events_current_cycle, events_last_cycle):
    """
    Only events that were not emitted in the last cycle should be emitted this cycle.
    This is done by comparing the events that apply to both cycles and selecting the events that only apply to the
    current cycle. Events are equal only if all their data (except for the timestamp) is equal. e.g if an event receives
    a custom parameter such as time_difference_minutes, if this value is different between the cycles, the event will be
    emitted.
    """

    def event_not_in_list(event, events_list):
        for other_event in events_list:
            if event == other_event:
                return False
        return True

    events_to_emit = []
    for event_current_cycle in events_current_cycle:
        if event_not_in_list(event_current_cycle, events_last_cycle):
            events_to_emit.append(event_current_cycle)

    return events_to_emit


class Rule(metaclass=Singleton):
    """
    Abstract Rule class.
    Each SystemState component has a rule defined, which is registered on the message_queue message of that
    component - to be run whenever the message_queue publishes that message. All rules are also automatically registered
    on the message VALIDATE_NEW_SYSTEM_STATE_MESSAGE - allowing the message_queue to invoke all rules at once at the
    start of a new run.

    The rule performs the following logic for each individual component (e.g each single FC port):
    1. If the component is missing, emit an event and break (unless emit_missing_event=False, in which case break and
    do nothing).
    2. If the component is in invalid state emit a negative event.
    3. If the component is in a valid state, emit a positive event.

    Logic in order to not repeat events:
    1. If the component was already missing in the last cycle - don't emit missing event again.
    2. If the component was already negative in the last cycle - don't emit negative event again.
    3. If the component was already positive in the last cycle - don't emit positive event again.
    4. If there is no last cycle (i.e this is the first run) - always emit both positive and negative events. This
    means that at the start of the system we will receive one event (probably mostly positive) for each individual
    component.
    5. If the component was missing and is now found - always emit event (either positive or negative). This allows for
    the alert regarding the missing component to know that component has been found (though it may be invalid).

    The GenericRule, which is defined automatically for all component that don't have a specific rule, only sets a
    valid state for the component.
    """
    emit_missing_event = True
    combine_positive_events = False
    negative_event_component_evaluators: List[Callable[[Component, SystemState], List[Event]]] = []
    negative_event_component_container_evaluators: List[Callable[[ComponentContainer, SystemState],
                                                                 List[Event]]] = []
    is_enabled = True

    def execute_rule_for_individual_component(self, new_component: Component, old_component: Component = None,
                                              new_system_state: SystemState = None,
                                              old_system_state: SystemState = None):
        new_component.state = STATE_FOR_VALID_DATA

        if new_component.is_missing:
            if self.emit_missing_event:
                if old_component is None or not old_component.is_missing:
                    _logger.info(f"Not able to find data for {new_component}. "
                                 f"Producing Infinibox event: ComponentMissingEvent")
                    EventEngine().register_event_request(ComponentNotFoundEvent(new_component))
                new_component.state = STATE_FOR_MISSING_COMPONENT

            return

        negative_events_current_cycle = []
        negative_events_last_cycle = []
        old_component_exists = old_component is not None and not old_component.is_missing

        for negative_event_evaluator in self.negative_event_component_evaluators:
            events_from_evaluator = negative_event_evaluator(new_component, new_system_state)
            negative_events_current_cycle.extend(events_from_evaluator if events_from_evaluator else [])

            if old_component_exists:
                events_from_evaluator = negative_event_evaluator(old_component, old_system_state)
                negative_events_last_cycle.extend(events_from_evaluator if events_from_evaluator else [])

        if negative_events_current_cycle:
            for negative_event in get_events_to_emit(negative_events_current_cycle, negative_events_last_cycle):
                if negative_event is not None:
                    _logger.info(f"State of {new_component} is invalid. "
                                 f"Producing Infinibox event: {negative_event}")
                    EventEngine().register_event_request(negative_event)
        else:
            if (negative_events_last_cycle or not old_component_exists) and not self.combine_positive_events:
                positive_event = self.component_positive_event(new_component)
                _logger.info(f"State of {new_component} is valid. "
                             f"Producing Infinibox events: {positive_event}")
                EventEngine().register_event_request(positive_event)

        if negative_events_current_cycle:
            new_component.state = self.state_when_component_not_valid

    def execute_rule_for_component_container(self, new_component_container: ComponentContainer,
                                             old_component_container: ComponentContainer = None,
                                             new_system_state: SystemState = None,
                                             old_system_state: SystemState = None):
        """
        # TODO Add to explanation: This function returns True or False according to if the container is valid (i.e,
        # TODO returns negative events). And returns the same for the old comnponent container.
        # TODO This is used since if the entire container has a negative event, calculating
        # TODO the state, which is done in __call__ will still return a NORMAL state if all snapshots are NORMAL
        """
        negative_events_current_cycle = []
        negative_events_last_cycle = []

        if self.negative_event_component_container_evaluators:
            old_component_exists = old_component_container is not None

            for negative_event_evaluator in self.negative_event_component_container_evaluators:
                events_from_evaluator = negative_event_evaluator(new_component_container, new_system_state)
                negative_events_current_cycle.extend(events_from_evaluator if events_from_evaluator else [])

                if old_component_exists:
                    events_from_evaluator = negative_event_evaluator(old_component_container, old_system_state)
                    negative_events_last_cycle.extend(events_from_evaluator if events_from_evaluator else [])

            if negative_events_current_cycle:
                for negative_event in get_events_to_emit(negative_events_current_cycle, negative_events_last_cycle):
                    if negative_event is not None:
                        _logger.info(f"State of {new_component_container} is invalid. "
                                     f"Producing Infinibox event: {negative_event}")
                        EventEngine().register_event_request(negative_event)

                new_component_container.state = self.state_when_component_not_valid

            else:
                if (negative_events_last_cycle or not old_component_exists) and not self.combine_positive_events:
                    positive_event = self.component_positive_event(new_component_container)
                    _logger.info(f"State of {new_component_container} is valid. "
                                 f"Producing Infinibox events: {positive_event}")
                    EventEngine().register_event_request(positive_event)

        return not bool(negative_events_current_cycle), not bool(negative_events_last_cycle)

    def _can_emit_new_event_to_delete(self, new_component, old_component, new_system_state=None):
        """
        Events should not be emitted if a previous event of the same type has already been emitted.
        Example: when checking a new ethernet port that has a link down, if the old component has a link down as well,
        an event would have been emitted already for the old component. Same if they were both with link up.

        If the old component is missing, a new component that is not missing should always emit an event,
        whether it is positive or negative. This will signal to the alert system that we have information about the
        component, and it is no longer missing.

        Note that in the case that all cases for which a new component is missing are already dealt with ath the start
        of execute_rule_for_individual_component.
        """
        # if (old_component is not None and not old_component.is_missing and
        #         self.is_component_in_valid_state(old_component, new_system_state) ==
        #         self.is_component_in_valid_state(new_component, new_system_state)):
        #     return False
        #
        # return True
        pass
        # TODO: put this explanation elsewhere

    def __call__(self, new_system_state, old_system_state=None):
        if not self.is_enabled:
            _logger.debug(f"Rule {self.__class__.__name__} is disabled. Skipping its operation.")
            return

        _logger.debug(f'Running {self.__class__.__name__} following change in {self.component_name}')

        old_component_object = getattr(old_system_state, self.component_name) if old_system_state else None
        new_component_object = getattr(new_system_state, self.component_name)

        if isinstance(new_component_object, ComponentContainer):
            for key, new_individual_component in new_component_object.get_dict().items():
                old_individual_component = old_component_object.get_dict().get(key) if old_component_object else None
                self.execute_rule_for_individual_component(new_individual_component, old_individual_component,
                                                           new_system_state, old_system_state)

            new_container_is_valid, old_container_is_valid = self.execute_rule_for_component_container(
                new_component_object, old_component_object, new_system_state, old_system_state)

            if self.combine_positive_events and new_container_is_valid:
                if (new_component_object.compute_state() is ComponentState.NORMAL and
                        (old_component_object is None
                         or old_component_object.compute_state() != ComponentState.NORMAL
                         or not old_container_is_valid)):
                    event_instance = self.component_positive_event(new_component_object)
                    _logger.info(f"Overall state of component container {new_component_object} is valid. "
                                 f"Producing Infinibox events: {event_instance}")
                    EventEngine().register_event_request(event_instance)

        else:
            self.execute_rule_for_individual_component(new_component_object, old_component_object,
                                                       new_system_state, old_system_state)

    def __init__(self):
        message_queue = MessageQueue()
        message_queue.add_function_to_message(self, self.component_change_message)
        message_queue.add_function_to_message(self, VALIDATE_NEW_SYSTEM_STATE_MESSAGE)


class GenericRule(Rule):
    """
    This rule is defined automatically for all components that don't have their own rule implemented.
    The generic rule only sets the component's state to NORMAL.
    """

    def execute_rule_for_individual_component(self, new_component: Component, old_component: Component = None,
                                              new_system_state: SystemState = None,
                                              old_system_state: SystemState = None):
        new_component.state = STATE_FOR_VALID_DATA


class BondRule(Rule):
    component_name = SYSTEM_COMPONENT_NAMES.bonds
    component_change_message = Bonds.component_change_message
    state_when_component_not_valid = STATE_FOR_BOND_DOWN
    component_positive_event = BondUpEvent

    @staticmethod
    def bond_status_evaluator(bond: Component, system_state: SystemState = None) -> List[Event]:
        if not bond.status:
            return [BondDownEvent(bond)]

    def __init__(self):
        """
        Appending the negative_event_evaluators list instead of overwriting it in the subclass, in order to use the
        typing annotation of the parent list.
        """
        super().__init__()
        self.negative_event_component_evaluators = [self.bond_status_evaluator]


class FCPortEventWrapper:
    """
    Dynamically wraps an FC Event object.
    At instantiation receives an FC event name, without its prefix. e.g FCPortUpEvent.
    The actual event object depends on the actual fc port used. i.e FrontendFCPortEvent or BackendFCPortEvent.

    When the wrapper is called with an fc port (as all events must be called with a component), it determines if that
    port is frontend or backend, and passes it to the correct FC event.
    """

    def __init__(self, fc_event_name_without_prefix):
        self.fc_event_name_without_prefix = fc_event_name_without_prefix

    def __eq__(self, other):
        return self.fc_event_name_without_prefix == other.fc_event_name_without_prefix

    def __hash__(self):
        return hash(self.fc_event_name_without_prefix)

    def __call__(self, fc_port, *args, **kwargs):
        if isinstance(fc_port.role, str):
            if 'backend' in fc_port.role.lower():
                prefix = 'Backend'
            elif 'frontend' in fc_port.role.lower():
                prefix = 'Frontend'
            else:
                prefix = 'Undefined'
        else:
            prefix = 'Undefined'

        return getattr(events, prefix + self.fc_event_name_without_prefix)(fc_port, *args, **kwargs)


class FCPortsRule(Rule):
    component_name = SYSTEM_COMPONENT_NAMES.fc_ports
    component_change_message = FcPorts.component_change_message
    state_when_component_not_valid = STATE_FOR_FC_PORT_DOWN
    component_positive_event = FCPortEventWrapper('FCPortUpEvent')

    @staticmethod
    def fc_link_state_evaluator(fc_port: Component, system_state: SystemState = None) -> List[FCPortEventWrapper]:
        if not fc_port.link_state:
            return [FCPortEventWrapper('FCPortDownEvent')(fc_port)]

    def __init__(self):
        super().__init__()
        # Annotation appears incorrect here, due to the wrapper
        self.negative_event_component_evaluators = [self.fc_link_state_evaluator]

    def execute_rule_for_individual_component(self, new_fc_port, old_fc_port=None, new_system_state=None,
                                              old_system_state=None):
        super().execute_rule_for_individual_component(new_fc_port, old_fc_port)
        change_speed_event = FCPortEventWrapper('FCPortSpeedChangeEvent')

        # Emits speed change event only if change happened while link was up.
        if (old_fc_port is not None and new_fc_port.link_state and old_fc_port.link_state and
                new_fc_port.connection_speed != old_fc_port.connection_speed):
            _logger.info(f"Connection speed of {new_fc_port} has changed from {old_fc_port.connection_speed},"
                         f" to {new_fc_port.connection_speed}. Producing InfiniBox event.")
            EventEngine().register_event_request(change_speed_event(new_fc_port,
                                                                    previous_speed=old_fc_port.connection_speed))


class EthPortEventWrapper:
    """
    Dynamically wraps an ethernet event object.
    At instantiation receives an ethernet event name, without its prefix. e.g EthPortUpEvent.
    The actual event object depends on the actual ethernet port used. i.e FrontendEthPortEvent or BackendEthPortEvent.

    When the wrapper is called with an ethernet port (as all events must be called with a component),
    it determines if that port is frontend or backend, and passes it to the correct ethernet Event object.
    """

    def __init__(self, eth_event_name_without_prefix):
        self.eth_event_name_without_prefix = eth_event_name_without_prefix

    def __eq__(self, other):
        return self.eth_event_name_without_prefix == other.eth_event_name_without_prefix

    def __hash__(self):
        return hash(self.eth_event_name_without_prefix)

    def __call__(self, eth_port, *args, **kwargs):
        if 'em' in eth_port.id.lower():
            prefix = 'Backend'
        else:
            prefix = 'Frontend'

        return getattr(events, prefix + self.eth_event_name_without_prefix)(eth_port, *args, **kwargs)


class EthernetPortsRule(Rule):
    component_name = SYSTEM_COMPONENT_NAMES.ethernet_ports
    component_change_message = EthernetPorts.component_change_message
    state_when_component_not_valid = STATE_FOR_ETH_PORT_DOWN
    component_positive_event = EthPortEventWrapper('EthPortUpEvent')

    @staticmethod
    def eth_link_state_evaluator(eth_port: Component, system_state: SystemState = None) -> List[
        EthPortEventWrapper]:
        if not eth_port.link_state:
            return [EthPortEventWrapper('EthPortDownEvent')(eth_port)]

    def __init__(self):
        """
        Appending the negative_event_evaluators list instead of overwriting it in the subclass, in order to use the
        typing annotation of the parent list.
        """
        super().__init__()
        # Annotation appears incorrect here, due to the wrapper
        self.negative_event_component_evaluators = [self.eth_link_state_evaluator]

    def execute_rule_for_individual_component(self, new_eth_port, old_eth_port=None, new_system_state=None,
                                              old_system_state=None):
        super().execute_rule_for_individual_component(new_eth_port, old_eth_port)
        change_speed_event = EthPortEventWrapper('EthPortSpeedChangeEvent')

        # Emits speed change event only if change happened while link was up.
        if (old_eth_port is not None and new_eth_port.link_state and old_eth_port.link_state and
                new_eth_port.maximum_speed != old_eth_port.maximum_speed):
            _logger.info(f"Maximum speed of {new_eth_port} has changed from {old_eth_port.maximum_speed},"
                         f" to {new_eth_port.maximum_speed}. Producing InfiniBox event.")
            EventEngine().register_event_request(change_speed_event(new_eth_port,
                                                                    previous_speed=old_eth_port.maximum_speed))


SNAPSHOT_DELETION_DELTA_SECONDS = 63 * 60  # 63 minutes, since snapman runs every hour, plus minus 2 minutes.
SNAPSHOT_CREATION_DELTA_SECONDS = 5 * 60  # Snapman can take a snapshot 5 minutes before its time


class SnapshotRule(Rule):
    component_name = SYSTEM_COMPONENT_NAMES.snapshots
    component_change_message = Snapshots.component_change_message
    state_when_component_not_valid = STATE_FOR_SNAPSHOT_BAD_VALUES
    component_positive_event = AllSnapshotsPositiveEvent
    emit_missing_event = False
    combine_positive_events = True

    # ========= Individual snapshot evaluators ========

    @staticmethod
    def snapshot_bad_expiration_value_evaluator(snapshot: Component,
                                                system_state: SystemState = None) -> List[Event]:
        if not snapshot.expires_at:
            return [SnapshotBadExpirationValue(snapshot)]

    @staticmethod
    def snapshot_bad_creation_value(snapshot: Component,
                                    system_state: SystemState = None) -> List[Event]:
        """
        """
        # TODO: Change text
        if not snapshot.created_at:
            return [SnapshotBadCreationValue(snapshot)]

    @staticmethod
    def snapshot_not_deleted_evaluator(snapshot: Component,
                                       system_state: SystemState = None) -> List[Event]:
        """
        Returns False iff more than 63 minutes have passed since snapshot.expires_at.
        If snapshot delete has been suspended in the system, there is no point in testing for deleted snapshots, and
        the snapshots are always valid.
        """
        # TODO: Change comment text

        if snapshot.expires_at and not system_state.snapshot_suspend_delete.suspend_delete:
            if snapshot.original_policy.policy_type == get_default_policy_type():
                active_policy = system_state.policies[snapshot.original_policy.policy_type]
                if not active_policy.enabled:
                    return

            # Using the last time the snapshot was updated as current time - as that was the current time
            # in regards to this SystemState (which may be the older system state). For this reason, we don't
            # want to use Arrow.now() for this value.
            current_time = snapshot.updated_at
            time_since_expired = (current_time - snapshot.expires_at).total_seconds()
            if time_since_expired > SNAPSHOT_DELETION_DELTA_SECONDS:
                return [SnapshotNotDeletedEvent(snapshot)]

    @staticmethod
    def snapshot_not_locked_evaluator(snapshot: Component,
                                      system_state: SystemState = None) -> List[Event]:
        """
        If the snapshot is immutable according to its origin - verify that it is locked.
        For system snapshots (immutable), we expect them to always be locked.
        For manual snapshots that we're taking as immutable, we expect them to never be unlocked either.
        If they are unlocked manually (by support), the event will still be sent.
        """
        if snapshot.original_policy.immutable and not snapshot.lock_expires_at:
            return [SnapshotNotLocked(snapshot)]

    # ========= Evaluators for entire Snapshots ComponentContainer========
    @staticmethod
    def snapshot_timing_evaluator(snapshots: ComponentContainer,
                                  system_state: SystemState = None) -> List[Event]:
        from iba_api.snapshot.snapman import MAX_DELTA_MINUTES

        # Using the last time the snapshots were updated as current time - as that was the current time
        # in regards to this SystemState (which may be the older system state). For this reason, we don't
        # want to use Arrow.now()
        current_time = snapshots.updated_at

        policy = get_default_policy(system_state)
        current_hour = current_time.hour
        service_start = get_infiniguard_health_start_time()
        daily_updated_at = policy.daily_updated_at or service_start
        enabled_at = policy.enabled_at or service_start

        snap_window_start = current_time.floor('hour').shift(minutes=-MAX_DELTA_MINUTES)
        snap_window_end = current_time.floor('hour').shift(minutes=MAX_DELTA_MINUTES)
        recent_snaps = snapshots.get_ordered_snapshots_after_checkpoint(snap_window_start)

        negative_events = []
        if not policy.enabled:
            return negative_events

        if len(recent_snaps) > 1:
            negative_events.append(ExcessiveSnapshots(snapshots, recent_snaps=recent_snaps))

        if (service_start < snap_window_start and daily_updated_at < snap_window_start
                and current_time > snap_window_end):
            if current_hour in policy.daily:
                if enabled_at < snap_window_start and (len(recent_snaps) == 0
                                                       or recent_snaps[0].created_at > snap_window_end):
                    negative_events.append(SnapshotOverdue(snapshots, hour=current_hour))
            else:
                if len(recent_snaps) == 1:
                    negative_events.append(ExcessiveSnapshots(snapshots, recent_snaps=recent_snaps))

        return negative_events

    def __init__(self):
        """
        Appending the negative_event_evaluators list instead of overwriting it in the subclass, in order to use the
        typing annotation of the parent list.
        """
        super().__init__()
        self.negative_event_component_evaluators = [self.snapshot_bad_expiration_value_evaluator,
                                                    self.snapshot_not_deleted_evaluator,
                                                    self.snapshot_bad_creation_value,
                                                    self.snapshot_not_locked_evaluator,
                                                    ]
        self.negative_event_component_container_evaluators = [self.snapshot_timing_evaluator]


# ====== Threshold Rules =======
"""
Rules which work according to thresholds and several levels (e.g NORMAL, LIMITED, CRITICAL),
instead of binary valid/invalid states.
Rules to implement a new event of this type:

"""


# TODO: write instruction for new rule


@dataclass
class ThresholdLevel:
    """
    ThresholdLevel defines the event and state to be used when that level is reached, given a certain value.

    A level is defined according to the minimal value required to qualify for that level,
    and until the minimal level of the next object in line.
    For instance, if between 0 and 0.4 is level NORMAL and above 0.4 is ERROR, we'll create two objects, one for NORMAL,
    with a min level of 0, and one for ERROR, with a min level of 0.4.
    (This example assumes the value is a float representing a percent, but it works the same with an int representing
    anything else, like number of snapshots).
    """
    min_value: float  # Implies int as well
    event: Type[Event]
    state: ComponentState
    event_params: dict = field(default_factory=dict)


class ThresholdRule(Rule):
    forbid_negative_values = True
    ignore_old_component_is_missing = False

    @property
    def normal_level(self):
        return self.get_threshold_levels()[0]

    @property
    def most_severe_level(self):
        return self.get_threshold_levels()[-1]

    @staticmethod
    def is_component_in_valid_state(component):
        """
        The threshold rule logic doesn't need this method.
        """
        pass

    def get_threshold_levels(self):
        raise NotImplementedError

    def get_current_threshold_level(self, component) -> ThresholdLevel:
        current_value = self.get_value_from_component(component)
        descending_levels = sorted(self.get_threshold_levels(), key=lambda level: level.min_value, reverse=True)

        for level in descending_levels:
            if self.forbid_negative_values and current_value < 0:
                _logger.error(f"{self.field_name} received is {current_value} (below zero). This should not be "
                              f"possible")
                return self.most_severe_level

            if current_value >= level.min_value or math.isclose(current_value, level.min_value):
                return level

    def get_value_from_component(self, component):
        """
        Returns value that should be used in order to determine threshold.
        """
        return getattr(component, self.field_name)

    def _can_emit_new_event(self, new_component, old_component):
        """
        Events should not be emitted if a previous event of the same level has already be emitted.

        If the old component is missing, a new component that is not missing should always emit an event,
        whether it is positive or negative. This will signal to the alert system that we have information about the
        component, and it is no longer missing. If ignore_old_component_is_missing = True, don't emit event
        if old_component was missing - only pay attention to changes in value.

        Note that in the case that all cases for which a new component is missing are already dealt with ath the start
        of execute_rule_for_individual_component.
        """
        if (old_component is not None and (self.ignore_old_component_is_missing or not old_component.is_missing) and
                self.get_current_threshold_level(new_component).min_value ==
                self.get_current_threshold_level(old_component).min_value):
            return False
        else:
            return True

    def execute_rule_for_individual_component(self, new_component, old_component=None, new_system_state=None,
                                              old_system_state=None):
        _logger.debug(f'Running {self.__class__.__name__} following change in {self.component_name}')

        component_value = self.get_value_from_component(new_component)

        if new_component.is_missing:
            if old_component is None or not old_component.is_missing:
                _logger.error(f"Not able to find data for {new_component}. "
                              f"Producing Infinibox event: ComponentMissingEvent")
                EventEngine().register_event_request(ComponentNotFoundEvent(new_component))

            new_component.state = STATE_FOR_MISSING_COMPONENT
            return

        if not isinstance(component_value, Number):
            _logger.error(f"Field {self.field_name} of component {new_component} is {component_value}. "
                          f"Producing Infinibox event: MissingData")
            EventEngine().register_event_request(MissingData(new_component, field_name=self.field_name))

            new_component.state = STATE_FOR_MISSING_DATA
            return

        threshold_level = self.get_current_threshold_level(new_component)
        new_component.state = threshold_level.state
        event_class = threshold_level.event

        if self._can_emit_new_event(new_component, old_component):
            _logger.info(f"{self.field_name} is {self.get_value_from_component(new_component)}. "
                         f"Producing Infinibox event: {event_class}")
            EventEngine().register_event_request(event_class(new_component, **threshold_level.event_params))


class SnapshotsCapacityRule(ThresholdRule):
    component_name = SYSTEM_COMPONENT_NAMES.snapshots_capacity
    component_change_message = SnapshotsCapacity.component_change_message
    ignore_old_component_is_missing = True
    field_name = "used_snapshot_capacity_percent"

    def get_threshold_levels(self):
        # Must be in ascending order, with the first level being "normal".
        return [
            ThresholdLevel(min_value=0,
                           event=SnapshotCapacityNormal,
                           state=STATE_FOR_VALID_DATA),
            ThresholdLevel(min_value=0.75,
                           event=SnapshotCapacityHigh,
                           state=STATE_FOR_SNAPSHOTS_CAPACITY_LIMITED),
            ThresholdLevel(min_value=0.8,
                           event=SnapshotCapacityHigh,
                           state=STATE_FOR_SNAPSHOTS_CAPACITY_LIMITED),
            ThresholdLevel(min_value=0.85,
                           event=SnapshotCapacityVeryHigh,
                           state=STATE_FOR_SNAPSHOTS_CAPACITY_HIGH),
            ThresholdLevel(min_value=0.9,
                           event=SnapshotCapacityVeryHigh,
                           state=STATE_FOR_SNAPSHOTS_CAPACITY_HIGH),
            ThresholdLevel(min_value=0.95,
                           event=SnapshotCapacityCriticallyHigh,
                           state=STATE_FOR_SNAPSHOTS_CAPACITY_CRITICALLY_HIGH),
            ThresholdLevel(min_value=1,
                           event=SnapshotCapacityExhausted,
                           state=STATE_FOR_SNAPSHOTS_CAPACITY_EXHAUSTED)
        ]


class DDECapacityRule(ThresholdRule):
    component_name = SYSTEM_COMPONENT_NAMES.dde_capacity
    component_change_message = DDECapacity.component_change_message
    ignore_old_component_is_missing = True
    field_name = "used_dde_capacity_percent"

    def get_threshold_levels(self):
        # Must be in ascending order, with the first level being "normal".
        return [
            ThresholdLevel(min_value=0,
                           event=DDECapacityNormal,
                           state=STATE_FOR_VALID_DATA,
                           event_params={'capacity_is_below': 75}),
            ThresholdLevel(min_value=0.75,
                           event=DDECapacityHigh,
                           state=STATE_FOR_DDE_CAPACITY_LIMITED,
                           event_params={'capacity_exceeded': 75}),
            ThresholdLevel(min_value=0.8,
                           event=DDECapacityHigh,
                           state=STATE_FOR_DDE_CAPACITY_LIMITED,
                           event_params={'capacity_exceeded': 80}),
            ThresholdLevel(min_value=0.85,
                           event=DDECapacityVeryHigh,
                           state=STATE_FOR_DDE_CAPACITY_HIGH,
                           event_params={'capacity_exceeded': 85}),
            ThresholdLevel(min_value=0.9,
                           event=DDECapacityVeryHigh,
                           state=STATE_FOR_DDE_CAPACITY_HIGH,
                           event_params={'capacity_exceeded': 90}),
            ThresholdLevel(min_value=0.95,
                           event=DDECapacityCriticallyHigh,
                           state=STATE_FOR_DDE_CAPACITY_CRITICALLY_HIGH,
                           event_params={'capacity_exceeded': 95}),
        ]


class SnapshotsNumRule(ThresholdRule):
    component_name = SYSTEM_COMPONENT_NAMES.snapshots
    component_change_message = Snapshots.component_change_message
    ignore_old_component_is_missing = True

    def get_threshold_levels(self):
        from iba_mgmt.const import MAX_SG_PER_CG

        HIGH_LIMIT = 0.8
        DANGEROUS_LIMIT = 0.9
        CRITICAL_LIMIT = 0.95

        def _percent_to_snapshots_limit(percent):
            """
            Receives a percentage number as a float (e.g 0.4) and returns the corresponding limit according to the max
            number of snapshots allowed.
            For example, if MAX_SG_PER_CG is 1000 and percent is 0.3, will return 300.
            """
            return int(percent * MAX_SG_PER_CG)

        def _percent_float_to_string(percent):
            """
            Converts float such as 0.95 to a string such as "95"
            """
            return str(int(percent * 100))

        # Must be in ascending order, with the first level being "normal".
        return [
            ThresholdLevel(min_value=0,
                           event=NumSnapshotsOk,
                           state=STATE_FOR_VALID_DATA,
                           event_params={'snapshots_num_limit': MAX_SG_PER_CG}),
            ThresholdLevel(min_value=_percent_to_snapshots_limit(HIGH_LIMIT),
                           event=SnapshotsNumHigh,
                           state=STATE_FOR_SNAPSHOTS_NUM_HIGH,
                           event_params={
                               'snapshots_num_percent_reached': _percent_float_to_string(HIGH_LIMIT),
                               'snapshots_num_limit': MAX_SG_PER_CG
                           }),
            ThresholdLevel(min_value=_percent_to_snapshots_limit(DANGEROUS_LIMIT),
                           event=SnapshotsNumDangerous,
                           state=STATE_FOR_SNAPSHOTS_NUM_DANGEROUS,
                           event_params={
                               'snapshots_num_percent_reached': _percent_float_to_string(DANGEROUS_LIMIT),
                               'snapshots_num_limit': MAX_SG_PER_CG
                           }),
            ThresholdLevel(min_value=_percent_to_snapshots_limit(CRITICAL_LIMIT),
                           event=SnapshotsNumCritical,
                           state=STATE_FOR_SNAPSHOTS_NUM_CRITICAL,
                           event_params={
                               'snapshots_num_percent_reached': _percent_float_to_string(CRITICAL_LIMIT),
                               'snapshots_num_limit': MAX_SG_PER_CG
                           }),
            ThresholdLevel(min_value=MAX_SG_PER_CG,
                           event=SnapshotsNumDepleted,
                           state=STATE_FOR_SNAPSHOTS_NUM_DEPLETED,
                           event_params={
                               'snapshots_num_limit': MAX_SG_PER_CG
                           }),
        ]

    def get_value_from_component(self, snapshots_container):
        """
        Returns value that should be used in order to determine threshold.
        """
        return len(snapshots_container)

    def __call__(self, new_system_state, old_system_state=None):
        if not self.is_enabled:
            _logger.debug(f"Rule {self.__class__.__name__} is disabled. Skipping its operation.")
            return

        _logger.debug(f'Running {self.__class__.__name__} following change in {self.component_name}')

        old_snapshots_container = getattr(old_system_state, self.component_name) if old_system_state else None
        new_snapshots_container = getattr(new_system_state, self.component_name)

        threshold_level = self.get_current_threshold_level(new_snapshots_container)
        event_class = threshold_level.event

        if self._can_emit_new_event(new_snapshots_container, old_snapshots_container):
            _logger.info(f"Num of snapshots in system is {self.get_value_from_component(new_snapshots_container)}. "
                         f"Producing Infinibox event: {event_class}")
            EventEngine().register_event_request(event_class(new_snapshots_container, **threshold_level.event_params))


# ======= Rules that don't emit and event ========
class PolicyRule(Rule):
    component_name = SYSTEM_COMPONENT_NAMES.policies
    component_change_message = Policies.component_change_message

    def execute_rule_for_individual_component(self, new_policy, old_policy=None, new_system_state=None,
                                              old_system_state=None):
        """
        This rule sets the values of enabled_at and daily_updated_at, and does nothing else.
        It does not emit events or change state of the component.

        enabled_at:

        Sets the enabled_at field of the policy as the last time in which the policy was changed from disabled to
        enabled.
        * If a policy changed from disabled to enabled, sets the enabled_at field to be the time that is was
        last updated (which is "now", but taken at the time of the data collection, not when the rule is run).
        * If the infiniguard health service is just starting (old_policy is None), sets the enabled_at field to be now
        as well, since there is no way to know how long the policy has been enabled before - and infiniguard health
        treats the situation as a clean slate when it is first started.
        * If the policy is currently disabled, enabled_at should be None.
        * If the policy has remained enabled, does nothing - as we want to save the time in which it first became
        enabled.

        latest_frequency_decrease:

        Sets the latest_frequency_decrease field of the policy to be the last time that the frequency value of the
        policy has decreased, or the first time that it was set if it never decreased.

        * If the frequency value is None, latest_frequency_decrease will be None
        * If this is the first cycle (there is no previous policy), sets the field to now (according when data was
        collected)
        * If the frequency field has decreased since the last cycle, or if the frequency field changed from None to a
        value, sets the latest_frequency_decrease to now.
        * If the frequency field has stayed the same or increased, the latest_frequency_decrease stays the same
        """
        if not new_policy.enabled:
            new_policy.enabled_at = None
        elif old_policy is None or not old_policy.enabled:
            new_policy.enabled_at = new_policy.updated_at

        if new_policy.daily is None:
            new_policy.daily_updated_at = None
        elif old_policy is None or old_policy.daily is None or old_policy.daily != new_policy.daily:
            new_policy.daily_updated_at = new_policy.updated_at


# ============ Initializing Rules ==========
ABSTRACT_RULES = (GenericRule, ThresholdRule)
CYBER_RECOVERY_RULES = (SnapshotRule, SnapshotsCapacityRule, PolicyRule, DDECapacityRule, SnapshotsNumRule)
initialized_rules = []


def initialize_rules():
    # On the standby app, cyber security monitoring should be disabled
    if is_standby_app() or not InfiniSafeRecoveryManager.is_enabled():
        for rule_class in CYBER_RECOVERY_RULES:
            rule_class.is_enabled = False

    if not initialized_rules:
        initialized_rules.extend([rule() for rule in get_all_implemented_rules()])
        initialized_rules.extend([rule() for rule in get_all_generic_rules()])


def reset_rules():
    global initialized_rules
    initialized_rules.clear()

    for rule_class in CYBER_RECOVERY_RULES:
        rule_class.is_enabled = True


def get_all_implemented_rules():
    return [rule for rule in get_all_subclasses(Rule) if rule not in ABSTRACT_RULES
            and rule.__base__ is not GenericRule]


@cached_function  # Caching so we don't have a situation of several new Class objects for the same rule.
def get_all_generic_rules():
    implemented_components = [rule.component_name for rule in get_all_implemented_rules()]
    generic_rule_classes = []

    for component_name, component_class in SystemState._system_components.items():
        if component_name not in implemented_components:
            new_class_name = snake_case_to_camel_case(component_name) + 'Rule'
            generic_rule_classes.append(type(new_class_name, (GenericRule,),
                                             {
                                                 'component_name': component_name,
                                                 'component_change_message': component_class.component_change_message
                                             }))

    return generic_rule_classes
