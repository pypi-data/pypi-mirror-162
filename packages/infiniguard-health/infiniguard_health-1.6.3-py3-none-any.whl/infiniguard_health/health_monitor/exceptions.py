import logging
import os
from functools import wraps

from infiniguard_health.event_engine.event_engine_infra import EventEngine
from infiniguard_health.event_engine.events import (
    DataCollectionError,
    CriticalDataCollectionError,
    DataCollectionException,
    FatalException
)
from infiniguard_health.utils import is_system_in_lab

_logger = logging.getLogger(__name__)


class LoaderException(Exception):
    """Generic loader exception"""

    def __init__(self, *args, loader=None):
        self.loader = loader
        super().__init__(*args)


class CollectorReturnedNone(LoaderException):
    """CollectorReturnedNone is raised when the collector function returns None,
       which might indicate of a collector function fault,
       as in case of no data, an empty list/dict should be returned.
    """
    pass


class RuntimeCollectorError(LoaderException):
    """RuntimeCollectorError is raised as a result of any exception that raises during a loader's execution.
       It encpsulates and logs the original exception (In Loader + handle_data_collection_exceptions).
       """
    pass


class CriticalRuntimeCollectorError(RuntimeCollectorError):
    """
    Runtime error that requires a critical level event
    """
    pass


class LoadConfigExecutionException(LoaderException):
    """Generic loader LoadConfig exception"""

    def __init__(self, load_config, *args, **kwargs):
        self.load_config = load_config
        super().__init__(*args, **kwargs)


class PreLoadParserFunctionError(LoadConfigExecutionException):
    """PreLoadParserFunctionError is raised when the pre-processing function raises an exception or returns None,
       which might indicate of a pre-processing function fault,
       as in case of no data, an empty list/dict should be returned.
    """
    pass


class InvalidIDFieldOrData(LoadConfigExecutionException):
    """InvalidIDFieldOrData
       Explained by Loader._convert_to_id_data_pair's docstring.
    """
    pass


def send_data_collection_error_event(exception):
    event = DataCollectionError(exception_string=repr(exception),
                                loader_name=repr(exception.loader))
    EventEngine().emit_urgent_event(event)


def send_critical_data_collection_error_event(exception):
    event = CriticalDataCollectionError(exception_string=repr(exception),
                                        loader_name=repr(exception.loader))
    EventEngine().emit_urgent_event(event)


def send_data_collection_exception_event(exception):
    # Data collection exception events are only send in our lab - not when running in the field.
    if is_system_in_lab():
        event = DataCollectionException(exception_string=repr(exception),
                                        loader_name=repr(exception.loader))
        EventEngine().emit_urgent_event(event)


def send_fatal_exception_event(exception):
    # Fatal exception events are always sent, both in the lab and in the field.
    event = FatalException(exception_string=repr(exception))
    EventEngine().emit_urgent_event(event)


def handle_data_collection_exceptions(method):
    @wraps(method)
    def wrapper(instance, *args, **kwargs):
        debug_mode = os.environ.get('INFINIGUARD_HEALTH_DEBUG', False)

        try:
            return method(instance, *args, **kwargs)

        except CriticalRuntimeCollectorError as e:
            _logger.exception(f'Loader\'s collector function failed with a critical error.\n'
                              f'{e.loader.exception_str}')
            send_critical_data_collection_error_event(e)

            if debug_mode:
                raise e

        except RuntimeCollectorError as e:
            _logger.exception(f'Loader\'s collector function failed.\n'
                              f'{e.loader.exception_str}')
            send_data_collection_error_event(e)

            if debug_mode:
                raise e

        except LoadConfigExecutionException as e:
            _logger.exception(f'Loader internal exception occurred during the execution of '
                              f'load config: {e.load_config.config_id}\n'
                              f'{e.loader.exception_str}')
            send_data_collection_exception_event(e)

            if debug_mode:
                raise e

        except LoaderException as e:
            _logger.exception('Loader internal exception occurred.\n'
                              f'{e.loader.exception_str}')
            send_data_collection_exception_event(e)

            if debug_mode:
                raise e

        except Exception as e:
            _logger.exception('Loader unhandled exception occurred')
            send_data_collection_exception_event(e)
            raise e

    return wrapper
