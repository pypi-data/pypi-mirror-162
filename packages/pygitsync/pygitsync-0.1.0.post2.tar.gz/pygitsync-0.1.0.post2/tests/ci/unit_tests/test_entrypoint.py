import pathlib
import tempfile
import typing

import pytest
from click.testing import CliRunner

from pygitsync._configuration import (
    ApplicationConfiguration,
    GitSyncConfiguration,
    RepoConfiguration,
)
from pygitsync.entrypoint import (
    WhileContext,
    _working_directory,
    flit_entry,
    main,
    process_cli_arguments,
)


@pytest.fixture()
def mock_configuration(mocker):
    value = GitSyncConfiguration.parse_obj(
        {
            "application": ApplicationConfiguration.parse_obj(
                {
                    "exception_sleep_seconds": 0.1,
                    "sleep_duration_seconds": 0.1,
                }
            ),
            "repo": RepoConfiguration.parse_obj(
                {
                    "pattern": "master",
                    "pattern_type": "branch",
                    "url": "https://some.where",
                }
            ),
        }
    )
    return mocker.patch(
        "pygitsync.entrypoint._load_configuration", return_value=value
    )


@pytest.fixture()
def mock_daemon_context(mocker):
    return mocker.patch("pygitsync.entrypoint.daemon.DaemonContext")


@pytest.fixture()
def mock_main(mocker):
    return mocker.patch("pygitsync.entrypoint.main", mocker.AsyncMock())


@pytest.fixture()
def mock_runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def mock_while_context(mocker):
    def _apply(returns: typing.List[bool]):
        import pygitsync.entrypoint

        mocker.patch(
            "pygitsync._configuration.EXCEPTION_SLEEP_DURATION_SECONDS", 0.1
        )

        return mocker.patch.object(
            pygitsync.entrypoint.WhileContext,
            "keep_running",
            side_effect=returns,
        )

    return _apply


class TestWhileContext:
    def test_not_run_once(self):
        under_test = WhileContext(False)

        assert not under_test.run_once

        # keep_running is true both times (looks like redundant tests, but it's not)
        assert under_test.keep_running()
        assert under_test.keep_running()

    def test_run_once(self):
        under_test = WhileContext(True)

        assert under_test.run_once

        assert under_test.keep_running()
        assert not under_test.keep_running()


class TestWorkingDirectory:
    @pytest.mark.asyncio
    async def test_user_specified_exists(self):
        with tempfile.TemporaryDirectory() as td:
            ud = pathlib.Path(td)
            assert ud.is_dir()

            async with _working_directory(ud) as d:
                assert ud == d
                assert d.is_dir()

    @pytest.mark.asyncio
    async def test_user_specified_created(self):
        with tempfile.TemporaryDirectory() as td:
            ud = pathlib.Path(td) / "some/new/dir"
            assert not ud.is_dir()

            async with _working_directory(ud) as d:
                assert ud == d
                assert d.is_dir()

    @pytest.mark.asyncio
    async def test_user_specified_empty(self):
        async with _working_directory(None) as d:
            assert d.is_dir()


class TestMain:
    MOCK_PATH = pathlib.Path("some/path")

    @pytest.mark.asyncio
    async def test_is_daemon(
        self, mock_configuration, mock_while_context, mocker
    ):
        # cannot test true infinite loop, but at least show that it doesn't
        # exit after the first iteration.
        mock_keep_running = mock_while_context([True, True, False])
        await main(self.MOCK_PATH, True, 1, None)

        mock_keep_running.assert_has_calls(
            [
                mocker.call(),
                mocker.call(),
                mocker.call(),
            ]
        )

    @pytest.mark.asyncio
    async def test_not_daemon(
        self, mock_configuration, mock_while_context, mocker
    ):
        mock_keep_running = mock_while_context([True, False])
        await main(self.MOCK_PATH, True, 1, None)

        mock_keep_running.assert_has_calls(
            [
                mocker.call(),
                mocker.call(),
            ]
        )


class TestProcessCliArguments:
    def test_default(
        self, mock_configuration, mock_daemon_context, mock_main, mock_runner
    ):
        result = mock_runner.invoke(process_cli_arguments, [])

        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            pathlib.Path(".pygitsync.yaml"), False, None, None
        )
        mock_daemon_context.assert_not_called()

    def test_configuration_long(
        self, mock_configuration, mock_daemon_context, mock_main, mock_runner
    ):
        result = mock_runner.invoke(
            process_cli_arguments, ["--configuration", "some/file"]
        )

        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            pathlib.Path("some/file"), False, None, None
        )
        mock_daemon_context.assert_not_called()

    def test_configuration_short(
        self, mock_configuration, mock_daemon_context, mock_main, mock_runner
    ):
        result = mock_runner.invoke(process_cli_arguments, ["-c", "some/file"])

        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            pathlib.Path("some/file"), False, None, None
        )
        mock_daemon_context.assert_not_called()

    def test_interval_long(self, mock_configuration, mock_main, mock_runner):
        result = mock_runner.invoke(process_cli_arguments, ["--interval", "25"])

        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            pathlib.Path(".pygitsync.yaml"), False, 25, None
        )

    def test_interval_short(self, mock_configuration, mock_main, mock_runner):
        result = mock_runner.invoke(process_cli_arguments, ["-i", "25"])

        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            pathlib.Path(".pygitsync.yaml"), False, 25, None
        )

    def test_enable_daemon_long(
        self, mock_configuration, mock_daemon_context, mock_main, mock_runner
    ):
        result = mock_runner.invoke(process_cli_arguments, ["--daemon"])

        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            pathlib.Path(".pygitsync.yaml"), True, None, None
        )
        mock_daemon_context.assert_called_once()

    def test_enable_daemon_short(
        self, mock_configuration, mock_daemon_context, mock_main, mock_runner
    ):
        result = mock_runner.invoke(process_cli_arguments, ["-d"])

        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            pathlib.Path(".pygitsync.yaml"), True, None, None
        )
        mock_daemon_context.assert_called_once()

    def test_working_directory_long(
        self, mock_configuration, mock_daemon_context, mock_main, mock_runner
    ):
        result = mock_runner.invoke(
            process_cli_arguments, ["--working", "some/path"]
        )

        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            pathlib.Path(".pygitsync.yaml"),
            False,
            None,
            pathlib.Path("some/path"),
        )

    def test_working_directory_short(
        self, mock_configuration, mock_daemon_context, mock_main, mock_runner
    ):
        result = mock_runner.invoke(process_cli_arguments, ["-w", "some/path"])

        assert result.exit_code == 0
        mock_main.assert_awaited_once_with(
            pathlib.Path(".pygitsync.yaml"),
            False,
            None,
            pathlib.Path("some/path"),
        )


class TestFlitEntry:
    def test_clean(self, mocker):
        mock_main = mocker.patch("pygitsync.entrypoint.process_cli_arguments")

        flit_entry()

        mock_main.assert_called_once()
