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

# Marks at module level 
pytestmark = pytest.mark.track("test-track")

class TestMarkedModule:
    def test_mark_track(self, es_cluster, rally):
        rally.race(track="test-track",challenge="index-only")
  
class TestMarkedFunctions:
    @pytest.mark.track("test-track2")
    def test_mark_track2(self, es_cluster, rally):
        rally.race(track="test-track2",challenge="cluster-health")

@pytest.mark.track("test-track")
class TestMarkedClass:
    def test_mark_track(self, es_cluster, rally):
        rally.race(track="test-track",challenge="force-merge")

    @pytest.mark.track("test-track2")
    def test_mark_track3(self, es_cluster, rally):
        rally.race(track="test-track2",challenge="index-only")

class TestMarkedTrackList:
    @pytest.mark.track(["many-tracks/sub-track", "many-tracks/sub-track2"])
    def test_mark_track_list(self, es_cluster, rally):
        rally.race(track="many-tracks/sub-track",challenge="index-only")
        rally.race(track="many-tracks/sub-track2",challenge="index-only")

    @pytest.mark.track("many-tracks/sub-track,many-tracks/sub-track2")
    def test_mark_track_list_comma_separated(self, es_cluster, rally):
        rally.race(track="many-tracks/sub-track",challenge="index-only")
        rally.race(track="many-tracks/sub-track2",challenge="index-only")

class TestMarkedSubTrack:
    @pytest.mark.track("many-tracks/sub-track")
    def test_mark_sub_track(self, es_cluster, rally):
        rally.race(track="many-tracks/sub-track",challenge="index-only")

    @pytest.mark.track("many-tracks/sub-track2")
    def test_mark_sub_track2(self, es_cluster, rally):
        rally.race(track="many-tracks/sub-track2",challenge="index-only")

    @pytest.mark.track("many-tracks/sub-track3")
    def test_mark_sub_track3(self, es_cluster, rally):
        rally.race(track="many-tracks/sub-track3",challenge="index-only")

