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

import pytest

from pytest_rally.elasticsearch import TestCluster
from pytest_rally.rally import Rally

@pytest.fixture(scope="module")
def distribution_version(request):
    return request.config.option.distribution_version

@pytest.fixture(scope="module")
def revision(request):
    return request.config.option.revision

@pytest.fixture(scope="class")
def rally(request):
    r = request.config.option.rally
    yield r
    r.delete_config_file()

@pytest.fixture(scope="module", autouse=False)
def es_cluster(request, distribution_version, revision):
    dist = distribution_version
    rev = revision
    debug = request.config.option.debug_rally
    cluster = TestCluster(distribution_version=dist, debug=debug)
    cluster.install()
    cluster.start()
    yield cluster
    cluster.stop()
