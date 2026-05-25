from cratepilot import app


def test_main_launches_background_process_when_not_in_foreground(monkeypatch):
    spawned = {}

    class DummyProc:
        pass

    def fake_popen(cmd, **kwargs):
        spawned["cmd"] = cmd
        spawned["kwargs"] = kwargs
        return DummyProc()

    monkeypatch.delenv("CRATEPILOT_FOREGROUND", raising=False)
    monkeypatch.setattr(app.subprocess, "Popen", fake_popen)

    exit_code = app.main()

    assert exit_code == 0, "Expected launcher mode to return success immediately."
    assert spawned["cmd"][0] == app.sys.executable, "Expected launcher to reuse the current Python interpreter."
    assert spawned["cmd"][-1] == "cratepilot", "Expected launcher to start the cratepilot module in the child process."
    assert spawned["kwargs"]["env"]["CRATEPILOT_FOREGROUND"] == "1", "Expected child process to run in foreground mode."
    assert spawned["kwargs"]["start_new_session"] is True, "Expected detached launch for the GUI child process."


def test_main_runs_foreground_when_flag_is_set(monkeypatch):
    monkeypatch.setenv("CRATEPILOT_FOREGROUND", "1")
    monkeypatch.setattr(app, "_run_foreground_app", lambda: 7)
    spawned = {"called": False}

    def fake_popen(*_args, **_kwargs):
        spawned["called"] = True
        raise AssertionError("Popen should not be called in foreground mode")

    monkeypatch.setattr(app.subprocess, "Popen", fake_popen)

    assert app.main() == 7, "Expected foreground mode to delegate to the Qt app runner."
    assert spawned["called"] is False
