from unittest import mock

from django.test import TestCase
from viewflow import lock, signals as vf_signals
from viewflow.activation import STATUS
from viewflow.base import this

from ..flows import AsyncActivationHandler, AsyncHandler


class ProcessStub(object):
    _default_manager = mock.Mock()

    def __init__(self, flow_class=None):
        self.flow_class = flow_class

    def active_tasks(self):
        return []

    def save(self):
        self.pk = 1
        return


class TaskStub(object):
    _default_manager = mock.Mock()

    def __init__(self, flow_task=None):
        self.flow_task = flow_task
        self.process_id = 1
        self.pk = 1
        self.status = STATUS.NEW
        self.started = None

    @property
    def leading(self):
        from viewflow.models import Task
        return Task.objects.none()

    def save(self):
        self.pk = 1
        return


class FlowStub(object):
    process_class = ProcessStub
    task_class = TaskStub
    lock_impl = lock.no_lock
    instance = None


class AsyncFlow(FlowStub):
    handler_task = AsyncHandler(this.task_handler)
    method_called = False

    def task_handler(self, activation):
        AsyncFlow.method_called = True


class AsyncActivationHandlerTestCase(TestCase):

    def init_node(self, node, flow_class=None, name='test_node'):
        node.flow_class = flow_class or FlowStub
        node.name = name
        node.ready()
        return node

    def setUp(self):
        ProcessStub._default_manager.get.return_value = ProcessStub()
        TaskStub._default_manager.get.return_value = TaskStub()
        FlowStub.instance = FlowStub()

    def test_perform(self):

        AsyncFlow.instance = AsyncFlow()
        flow_task = self.init_node(
            AsyncFlow.handler_task,
            flow_class=AsyncFlow,
            name='task'
        )
        # Prepare signal receiver
        self.task_started_signal_called = False

        def handler(sender, **kwargs):
            self.task_started_signal_called = True

        vf_signals.task_started.connect(handler)

        act = AsyncActivationHandler()
        act.initialize(flow_task, TaskStub())

        # execute
        act.perform()
        self.assertEqual(act.task.status, STATUS.NEW)
        self.assertTrue(AsyncFlow.method_called)
        self.assertTrue(self.task_started_signal_called)

    def test_callback(self):

        AsyncFlow.instance = AsyncFlow()
        flow_task = self.init_node(
            AsyncFlow.handler_task,
            flow_class=AsyncFlow,
            name='task'
        )

        # Prepare signal receiver
        self.task_finished_signal_called = False

        def handler(sender, **kwargs):
            self.task_finished_signal_called = True

        vf_signals.task_finished.connect(handler)

        act = AsyncActivationHandler()
        act.initialize(flow_task, TaskStub())

        # execute
        act.perform()
        act.callback()
        self.assertEqual(act.task.status, STATUS.DONE)
        self.assertTrue(self.task_finished_signal_called)
