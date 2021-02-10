import os
import tempfile
import pytest
from docker import errors
from docker.context import ContextAPI
from docker.tls import TLSConfig
from .base import BaseAPIIntegrationTest


TEST_CONTEXT = "dockerpy_test"

class ContextLifecycleTest(BaseAPIIntegrationTest):
    def tearDown(self):
        if ContextAPI.get_context(TEST_CONTEXT):
            ContextAPI.remove_context(TEST_CONTEXT)
        super(ContextLifecycleTest, self).tearDown()


    def test_lifecycle(self):
        assert ContextAPI.get_context().Name == "default"
        assert not ContextAPI.get_context(TEST_CONTEXT)
        assert ContextAPI.get_current_context().Name == "default"

        dirpath = tempfile.mkdtemp()
        ca = tempfile.NamedTemporaryFile(
            prefix=os.path.join(dirpath, "ca.pem"), mode="r")
        cert = tempfile.NamedTemporaryFile(
            prefix=os.path.join(dirpath, "cert.pem"), mode="r")
        key = tempfile.NamedTemporaryFile(
            prefix=os.path.join(dirpath, "key.pem"), mode="r")

        # create context 'test
        docker_tls = TLSConfig(
            client_cert=(cert.name, key.name),
            ca_cert=ca.name)
        ContextAPI.create_context(
            TEST_CONTEXT, tls_cfg=docker_tls)

        # check for a context 'test' in the context store
        assert any([ctx.Name == TEST_CONTEXT for ctx in ContextAPI.contexts()])
        # retrieve a context object for 'test'
        assert ContextAPI.get_context(TEST_CONTEXT)
        # remove context
        ContextAPI.remove_context(TEST_CONTEXT)
        with pytest.raises(errors.ContextNotFound):
            ContextAPI.inspect_context(TEST_CONTEXT)
        # check there is no 'test' context in store
        assert not ContextAPI.get_context(TEST_CONTEXT)

        ca.close()
        key.close()
        cert.close()

    def test_context_remove(self):
        ContextAPI.create_context(TEST_CONTEXT)
        assert ContextAPI.inspect_context(TEST_CONTEXT)["Name"] == TEST_CONTEXT

        ContextAPI.remove_context(TEST_CONTEXT)
        with pytest.raises(errors.ContextNotFound):
            ContextAPI.inspect_context(TEST_CONTEXT)

    def test_load_context_without_orchestrator(self):
        ContextAPI.create_context(TEST_CONTEXT)
        ctx = ContextAPI.get_context(TEST_CONTEXT)
        assert ctx
        assert ctx.Name == TEST_CONTEXT
        assert ctx.Orchestrator is None
