# Licensed to Elasticsearch B.V. under one or more contributor
# license agreements. See the NOTICE file distributed with
# this work for additional information regarding copyright
# ownership. Elasticsearch B.V. licenses this file to you under
# the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# 	http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import errno
import json
import logging
import shlex
import socket
import subprocess
import time

from pytest_rally import process
import uuid

class TestCluster:
    def __init__(self,
                 distribution_version=None,
                 revision=None,
                 http_port=19200,
                 node_name="rally-node",
                 car="4gheap,trial-license,x-pack-ml,lean-watermarks",
                 debug=False):
        self.installation_id = None
        self.distribution_version = distribution_version
        self.revision = "current" if not revision else revision
        self.http_port = http_port
        self.transport_port = http_port + 100
        self.node_name = node_name
        self.car = car
        self.debug = debug
        self.logger = logging.getLogger(__name__)

    def wait_until_port_is_free(self, timeout=120):
        start = time.perf_counter()
        end = start + timeout
        while time.perf_counter() < end:
            c = socket.socket()
            connect_result = c.connect_ex(("127.0.0.1", self.http_port))
            # noinspection PyBroadException
            try:
                if connect_result == errno.ECONNREFUSED:
                    c.close()
                    return
                else:
                    c.close()
                    time.sleep(0.5)
            except Exception:
                pass

            raise TimeoutError(f"Port [{self.http_port}] is occupied after [{timeout}] seconds")

    def install(self):
        cmd = (f"esrally install --quiet "
               f"--http-port={self.http_port} --node={self.node_name} "
               f"--master-nodes={self.node_name} --car={self.car} "
               f'--seed-hosts="127.0.0.1:{self.transport_port}"')

        if self.distribution_version is not None:
            cmd += f" --distribution-version={self.distribution_version}"
        else:
            cmd += f" --revision={self.revision}"

        self.logger.debug("Installing Elasticsearch: [%s]", cmd)

        if self.debug:
            return
        else:
            try:
                self.wait_until_port_is_free()
                self.logger.info("Installing Elasticsearch: [%s]", cmd)
                output = process.run_command_with_output(cmd)
                self.installation_id = json.loads("".join(output))["installation-id"]
            except subprocess.CalledProcessError as e:
                raise AssertionError(f"Failed to install Elasticsearch", e)

    def start(self):
        race = str(uuid.uuid4())
        cmd = f'esrally start --runtime-jdk=bundled --installation-id={self.installation_id} --race-id={race}'
        self.logger.info("Starting Elasticsearch: [%s]", cmd)
        if self.debug:
            return
        else:
            try:
                subprocess.run(shlex.split(cmd), check=True)
            except subprocess.CalledProcessError as e:
                raise AssertionError("Failed to start Elasticsearch test cluster.", e)

    def stop(self):
        cmd = f"esrally stop --installation-id={self.installation_id}"
        self.logger.info("Stopping Elasticsearch: [%s]", cmd)
        if self.debug:
            return
        else:
            try:
                subprocess.run(shlex.split(cmd))
            except subprocess.CalledProcessError as e:
                raise AssertionError("Failed to stop Elasticsearch test cluster.", e)

    def __str__(self):
        return f"TestCluster[installation-id={self.installation_id}]"
