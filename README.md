# pytest-rally

**This software is currently under active development and should be considered experimental.**

`pytest-rally` is a pytest plugin that facilitates testing [Rally](https://esrally.readthedocs.io/en/stable/) track repositories, such as [rally-tracks](https://github.com/elastic/rally-tracks).

Its main feature is [automatic generation of integration tests](#test-generation) for track repositories. The plugin will generate a unique test for each [challenge](https://esrally.readthedocs.io/en/stable/track.html#challenge) of each track in the repository. By default, these tests will execute an `esrally race` command using [`--test-mode`](https://esrally.readthedocs.io/en/stable/command_line_reference.html#test-mode). You can think of this as an auto-generated suite of smoke tests.

The plugin also offers a library of [fixtures](#fixtures) that facilitate writing custom integration tests.

# Installation

Currently, the plugin must be installed from source:

```
pip install git+ssh://git@github.com/elastic/pytest-rally
```

# Features

## Test generation

If invoked from within a track repository, `pytest-rally` will attempt to generate a test for each challenge of each track contained in it, using the Git branch that is currently checked out.

For this to work, `pytest` must find an appropriately-named class (`TestTrackRepository` by default, configurable via `--generate-tests-for-class`) containing a test method that accepts both `track` and `challenge` as arguments. The plugin will inspect the track repository via `esrally list tracks` and build a list of all valid combinations of tracks and challenges. This will then be used to [parametrize](https://docs.pytest.org/en/6.2.x/parametrize.html) the test function's `track` and `challenge` arguments. The end result is a unique test per challenge per track.

### Example

Suppose we want to execute a race for each challenge of each track in the rally-tracks repository and assert that its exit code is `0`. Here are all of the tracks and challenges contained in the repository:

`esrally list tracks`

```
    ____        ____
   / __ \____ _/ / /_  __
  / /_/ / __ `/ / / / / /
 / _, _/ /_/ / / / /_/ /
/_/ |_|\__,_/_/_/\__, /
                /____/

Available tracks:

Name              Description                                                              Documents    Compressed Size    Uncompressed Size    Default Challenge        All Challenges
----------------  -----------------------------------------------------------------------  -----------  -----------------  -------------------  -----------------------  -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
eql               EQL benchmarks based on endgame index of SIEM demo cluster               60,782,211   4.5 GB             109.2 GB             default                  default,index-sorting
dense_vector      Benchmark for dense vector indexing and search                           10,000,000   7.2 GB             19.5 GB              index-and-search         index-and-search
geoshape          Shapes from PlanetOSM                                                    84,220,567   17.0 GB            58.7 GB              append-no-conflicts      append-no-conflicts,append-no-conflicts-big
tsdb              metricbeat information for elastic-app k8s cluster                       116,633,698  N/A                123.0 GB             append-no-conflicts      append-no-conflicts
nested            StackOverflow Q&A stored as nested docs                                  11,203,029   663.3 MB           3.4 GB               nested-search-challenge  nested-search-challenge,index-only
nyc_taxis         Taxi rides in New York in 2015                                           165,346,692  4.5 GB             74.3 GB              append-no-conflicts      append-no-conflicts,append-no-conflicts-index-only,append-sorted-no-conflicts-index-only,update,append-ml,aggs
geopointshape     Point coordinates from PlanetOSM indexed as geoshapes                    60,844,404   470.8 MB           2.6 GB               append-no-conflicts      append-no-conflicts,append-no-conflicts-index-only,append-fast-with-conflicts
geopoint          Point coordinates from PlanetOSM                                         60,844,404   482.1 MB           2.3 GB               append-no-conflicts      append-no-conflicts,append-no-conflicts-index-only,append-fast-with-conflicts
sql               SQL query performance based on NOAA Weather data                         33,659,481   949.4 MB           9.0 GB               sql                      sql
noaa              Global daily weather measurements from NOAA                              33,659,481   949.4 MB           9.0 GB               append-no-conflicts      append-no-conflicts,append-no-conflicts-index-only,aggs
pmc               Full text benchmark with academic papers from PMC                        574,199      5.5 GB             21.7 GB              append-no-conflicts      indexing-querying,append-no-conflicts,append-no-conflicts-index-only,append-sorted-no-conflicts,append-fast-with-conflicts
percolator        Percolator benchmark based on AOL queries                                2,000,000    121.1 kB           104.9 MB             append-no-conflicts      append-no-conflicts
metricbeat        Metricbeat data                                                          1,079,600    87.7 MB            1.2 GB               append-no-conflicts      append-no-conflicts
elastic/logs      Track for simulating logging workloads                                   16,469,078   N/A                N/A                  logging-indexing         logging-snapshot,logging-snapshot-restore,logging-disk-usage,logging-indexing-querying,many-shards-full,logging-indexing,logging-querying,many-shards-quantitative,many-shards-base
elastic/endpoint  Endpoint track                                                           0            0 bytes            0 bytes              default                  default
elastic/security  Track for simulating Elastic Security workloads                          77,513,777   N/A                N/A                  security-querying        security-indexing-querying,security-querying,security-indexing,index-alert-source-events
geonames          POIs from Geonames                                                       11,396,503   252.9 MB           3.3 GB               append-no-conflicts      append-no-conflicts,append-no-conflicts-index-only,append-fast-with-conflicts,significant-text
so                Indexing benchmark using up to questions and answers from StackOverflow  36,062,278   8.9 GB             33.1 GB              append-no-conflicts      append-no-conflicts
http_logs         HTTP server log data                                                     247,249,096  1.2 GB             31.1 GB              append-no-conflicts      append-no-conflicts,runtime-fields,append-no-conflicts-index-only,append-sorted-no-conflicts,append-index-only-with-ingest-pipeline,update,append-no-conflicts-index-reindex-only
```

We would write a class like this:

```python
class TestTrackRepository:
    def test_autogenerated(self, es_cluster, rally, track, challenge, rally_options):
        ret = rally.race(track=track, challenge=challenge, **rally_options)
        assert ret == 0
```

The `TestTrackRepository` class and the `test_autogenerated` method match the criteria described above, so `pytest-rally` will autogenerate tests for this class.

#### Test collection

During the collection phase, `pytest-rally` will generate a test per challenge based on the output of `esrally list tracks`:


`pytest --collect-only --log-cli-level=INFO it/test_all_tracks_and_challenges.py`

```
===================================================================================== test session starts ======================================================================================

collecting ...
------------------------------------------------------------------------------------- live log collection --------------------------------------------------------------------------------------
INFO     pytest_rally.rally:rally.py:107 Running command: [esrally list tracks --track-repository="/home/baamonde/code/elastic/rally-tracks" --track-revision="master" --configuration-name="pytest"]
collected 58 items

<Module it/test_all_tracks_and_challenges.py>
  <Class TestTrackRepository>
      <Function test_autogenerated[eql-default]>
      <Function test_autogenerated[eql-index-sorting]>
      <Function test_autogenerated[dense_vector-index-and-search]>
      <Function test_autogenerated[geoshape-append-no-conflicts]>
      <Function test_autogenerated[geoshape-append-no-conflicts-big]>
      <Function test_autogenerated[tsdb-append-no-conflicts]>
      <Function test_autogenerated[nested-nested-search-challenge]>
      <Function test_autogenerated[nested-index-only]>
      <Function test_autogenerated[nyc_taxis-append-no-conflicts]>
      <Function test_autogenerated[nyc_taxis-append-no-conflicts-index-only]>
      <Function test_autogenerated[nyc_taxis-append-sorted-no-conflicts-index-only]>
      <Function test_autogenerated[nyc_taxis-update]>
      <Function test_autogenerated[nyc_taxis-append-ml]>
      <Function test_autogenerated[nyc_taxis-aggs]>
      <Function test_autogenerated[geopointshape-append-no-conflicts]>
      <Function test_autogenerated[geopointshape-append-no-conflicts-index-only]>
      <Function test_autogenerated[geopointshape-append-fast-with-conflicts]>
      <Function test_autogenerated[geopoint-append-no-conflicts]>
      <Function test_autogenerated[geopoint-append-no-conflicts-index-only]>
      <Function test_autogenerated[geopoint-append-fast-with-conflicts]>
      <Function test_autogenerated[sql-sql]>
      <Function test_autogenerated[noaa-append-no-conflicts]>
      <Function test_autogenerated[noaa-append-no-conflicts-index-only]>
      <Function test_autogenerated[noaa-aggs]>
      <Function test_autogenerated[pmc-indexing-querying]>
      <Function test_autogenerated[pmc-append-no-conflicts]>
      <Function test_autogenerated[pmc-append-no-conflicts-index-only]>
      <Function test_autogenerated[pmc-append-sorted-no-conflicts]>
      <Function test_autogenerated[pmc-append-fast-with-conflicts]>
      <Function test_autogenerated[percolator-append-no-conflicts]>
      <Function test_autogenerated[metricbeat-append-no-conflicts]>
      <Function test_autogenerated[elastic/logs-logging-snapshot]>
      <Function test_autogenerated[elastic/logs-logging-snapshot-restore]>
      <Function test_autogenerated[elastic/logs-logging-disk-usage]>
      <Function test_autogenerated[elastic/logs-logging-indexing-querying]>
      <Function test_autogenerated[elastic/logs-many-shards-full]>
      <Function test_autogenerated[elastic/logs-logging-indexing]>
      <Function test_autogenerated[elastic/logs-logging-querying]>
      <Function test_autogenerated[elastic/logs-many-shards-quantitative]>
      <Function test_autogenerated[elastic/logs-many-shards-base]>
      <Function test_autogenerated[elastic/security-security-indexing-querying]>
      <Function test_autogenerated[elastic/security-security-querying]>
      <Function test_autogenerated[elastic/security-security-indexing]>
      <Function test_autogenerated[elastic/security-index-alert-source-events]>
      <Function test_autogenerated[geonames-append-no-conflicts]>
      <Function test_autogenerated[geonames-append-no-conflicts-index-only]>
      <Function test_autogenerated[geonames-append-fast-with-conflicts]>
      <Function test_autogenerated[geonames-significant-text]>
      <Function test_autogenerated[so-append-no-conflicts]>
      <Function test_autogenerated[http_logs-append-no-conflicts]>
      <Function test_autogenerated[http_logs-runtime-fields]>
      <Function test_autogenerated[http_logs-append-no-conflicts-index-only]>
      <Function test_autogenerated[http_logs-append-sorted-no-conflicts]>
      <Function test_autogenerated[http_logs-append-index-only-with-ingest-pipeline]>
      <Function test_autogenerated[http_logs-update]>
      <Function test_autogenerated[http_logs-append-no-conflicts-index-reindex-only]>

================================================================================= 58 tests collected in 3.11s ==================================================================================
```

Logging shows that the plugin first listed all tracks and then generated test functions for each track-challenge combination it found.

#### Test execution

Because our `test_autogenerated` function uses the [`es_cluster` fixture](#es_cluster), `pytest-rally` will install and start an Elasticsearch cluster during setup and stop it during teardown. All of our autogenerated tests will run their races with this cluster as their benchmark candidate.

The [`rally` fixture](#rally) used by the test function provides a `race` method, which we use to execute the actual race. This method generates the appropriate `esrally race` CLI string for each test and executes it in a [subprocess](https://docs.python.org/3/library/subprocess.html#subprocess.run), whose [return code](https://docs.python.org/3/library/subprocess.html#subprocess.CompletedProcess.returncode) we check in our assertion.

To see all of this in action, let's test a subset of the `http_logs` track:

`pytest it/test_all_tracks_and_challenges.py -k "http_logs-append-no-conflicts"`

```
===================================================================================== test session starts ======================================================================================
collected 56 items / 53 deselected / 3 selected

it/test_all_tracks_and_challenges.py::TestTrackRepository::test_autogenerated[http_logs-append-no-conflicts] FAILED                                                                      [ 33%]
it/test_all_tracks_and_challenges.py::TestTrackRepository::test_autogenerated[http_logs-append-no-conflicts-index-only] PASSED                                                           [ 66%]
it/test_all_tracks_and_challenges.py::TestTrackRepository::test_autogenerated[http_logs-append-no-conflicts-index-reindex-only] PASSED                                                   [100%]

=========================================================================================== FAILURES ===========================================================================================
____________________________________________________________ TestTrackRepository.test_autogenerated[http_logs-append-no-conflicts] _____________________________________________________________

self = <test_all_tracks_and_challenges.TestTrackRepository object at 0x7f3062c80a30>, es_cluster = <pytest_rally.elasticsearch.TestCluster object at 0x7f3062c809d0>
rally = <pytest_rally.rally.Rally object at 0x7f3062d1c0a0>, track = 'http_logs', challenge = 'append-no-conflicts', rally_options = {}

    def test_autogenerated(self, es_cluster, rally, track, challenge, rally_options):
        if track not in self.skip_tracks and challenge not in self.skip_challenges.get(track, []):
            ret = rally.race(track=track, challenge=challenge, **rally_options)
>           assert ret == 0
E           assert 64 == 0
E             +64
E             -0

it/test_all_tracks_and_challenges.py:30: AssertionError
------------------------------------------------------------------------------------ Captured stdout setup -------------------------------------------------------------------------------------

    ____        ____
   / __ \____ _/ / /_  __
  / /_/ / __ `/ / / / / /
 / _, _/ /_/ / / / /_/ /
/_/ |_|\__,_/_/_/\__, /
                /____/


--------------------------------
[INFO] SUCCESS (took 11 seconds)
--------------------------------
-------------------------------------------------------------------------------------- Captured log setup --------------------------------------------------------------------------------------
INFO     pytest_rally.elasticsearch:elasticsearch.py:84 Installing Elasticsearch: [esrally install --quiet --http-port=19200 --node=rally-node --master-nodes=rally-node --car=4gheap,trial-license,x-pack-ml --seed-hosts="127.0.0.1:19300" --revision=current]
INFO     pytest_rally.elasticsearch:elasticsearch.py:93 Starting Elasticsearch: [esrally start --runtime-jdk=bundled --installation-id=ad787106-2739-4a7b-abcf-36ca256f087b --race-id=9f1ac44d-b9c2-4dd1-b6ab-c3b274070834]
------------------------------------------------------------------------------------- Captured stdout call -------------------------------------------------------------------------------------

    ____        ____
   / __ \____ _/ / /_  __
  / /_/ / __ `/ / / / / /
 / _, _/ /_/ / / / /_/ /
/_/ |_|\__,_/_/_/\__, /
                /____/

[INFO] Race id is [0770593e-ab07-4ee4-9ebd-007caeedc297]
[ERROR] Cannot race. Error in load generator [0]
	Cannot run task [term]: Expected [hits] to be == [10000] but was [151].

Getting further help:
*********************
* Check the log files in /home/baamonde/.rally/logs for errors.
* Read the documentation at https://esrally.readthedocs.io/en/latest/.
* Ask a question on the forum at https://discuss.elastic.co/tags/c/elastic-stack/elasticsearch/rally.
* Raise an issue at https://github.com/elastic/rally/issues and include the log files in /home/baamonde/.rally/logs.

--------------------------------
[INFO] FAILURE (took 19 seconds)
--------------------------------

-------------------------------------------------------------------------------------- Captured log call ---------------------------------------------------------------------------------------
INFO     pytest_rally.rally:rally.py:141 Running command: [esrally race --track="http_logs" --challenge="append-no-conflicts" --track-repository="/home/baamonde/code/elastic/rally-tracks" --track-revision="ci-jobs" --configuration-name="pytest" --enable-assertions --kill-running-processes --on-error="abort" --pipeline="benchmark-only" --target-hosts="127.0.0.1:19200" --test-mode]
=================================================================================== short test summary info ====================================================================================
FAILED it/test_all_tracks_and_challenges.py::TestTrackRepository::test_autogenerated[http_logs-append-no-conflicts] - assert 64 == 0
==================================================================== 1 failed, 2 passed, 53 deselected in 86.58s (0:01:26) =====================================================================
```

We see that two tests passed, but `http_logs-append-no-conflicts` failed. The captured setup and teardown logs show Elasticsearch being installed, started, and finally stopped. The captured log from the failing test shows the `esrally race` command that the plugin generated, and its captured stdout shows the Rally error (in this case, a [failed assertion](https://esrally.readthedocs.io/en/stable/track.html#operations)) that caused the failure.

#### Customizing tests

For the sake of example, suppose that we want to skip the  `http_logs-append-no-conflicts` until we are able to address the failure. But, in the meantime, we still want to run the test, but disable Rally's assertion checking. Here's one way to do it:

```python
import pytest

class TestTrackRepository:
    skip_challenges = {
        "http_logs": ["append-no-conflicts"]
    }

    def test_autogenerated(self, es_cluster, rally, track, challenge, rally_options):
        if challenge not in self.skip_challenges.get(track, []):
            ret = rally.race(track=track, challenge=challenge, **rally_options)
            assert ret == 0
        else:
            pytest.skip(msg=f"{track}-{challenge} included in skip list")

    def test_http_logs_append_no_conflicts_assertions_disabled(self, es_cluster, rally):
        ret = rally.race(track="http_logs", challenge="append-no-conflicts", enable_assertions=False)
        assert ret == 0

```

Alternatively, instead of skipping the autogenerated test and creating a new one, we could modify the autogenerated test's `rally_options` dict of kwargs, which is passed through to the `rally.race` method:

```python

class TestTrackRepository:
    def test_autogenerated(self, es_cluster, rally, track, challenge, rally_options):
        if f"{track}-{challenge}" == "http_logs-append-no-conflicts":
            rally_options.update({"enable_assertions": False})
        ret = rally.race(track=track, challenge=challenge, **rally_options)
        assert ret == 0
```

Because tests are defined in Python and the full `pytest` API is available, we can manipulate these tests as needed when the plugin's defaults are insufficient.

## Fixtures

### rally

The main purpose of this fixture is to provide Python bindings for the `esrally` command-line interface. This makes it possible to execute complex `esrally` shell commands in pure Python without having to do any string manipulation. The fixture yields a [`Rally` object](pytest_rally/rally.py#L63), which is aware of the relevant track repository and track revision for the test session and passes them as options to the `esrally` commands that are ultimately invoked by its methods.

This is currently limited to [`list_tracks`](pytest_rally/rally.py#L69) and [`race`](pytest_rally/rally.py#L110), but future releases will expand coverage.

This fixture also installs a [Rally configuration file](https://esrally.readthedocs.io/en/stable/configuration.html#rally-configuration) in `RALLY_HOME` for use by the plugin. It deletes the file during teardown.

### es_cluster

This fixture installs Elasticsearch during setup, yields a [`TestCluster` object](pytest_rally/elasticsearch.py#L29) during test execution, and stops it during teardown. By default, Elasticsearch will be built from source by Rally using the currently-checked out revision in the Elasticsearch source tree.

To install a specific released version of Elasticsearch, use the plugin's `--distribution-version` option, which maps directly to the equivalent [Rally option](https://esrally.readthedocs.io/en/stable/command_line_reference.html#distribution-version).

To build a specific revision of Elasticsearch from source, use the plugin's `--revision` option, which also maps to the [Rally equivalent](https://esrally.readthedocs.io/en/stable/command_line_reference.html#revision).

Note that state (indices, settings, etc.) is not reset between tests.

## Debugging

The plugin includes the CLI option `--debug-rally`. If provided, the plugin will skip installing/starting Elasticsearch, and will only *log* `esrally` commands as opposed to actually running them. This is useful for quickly inspecting the `esrally` CLI strings that the plugin generates.

## Skipping autogenerated tests

The plugin [marks](https://docs.pytest.org/en/6.2.x/mark.html#mark) all autogenerated tests with `autogenerated`, a custom marker. If you would like to skip running tests generated by the plugin, simply pass `--skip-autogenerated-tests`. The plugin will then skip all tests with this marker. Note that this does not affect test collection.

# Testing

```
python -mvenv .venv
source .venv/bin/activate
# provide full path to Rally source repository
pip install -e "/<full-path>/rally[develop]"
pytest
```
