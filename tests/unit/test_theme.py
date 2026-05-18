from cratepilot.gui import theme


def test_effective_theme_honors_manual_choice():
    assert theme.effective_theme("light") == "light"
    assert theme.effective_theme("dark") == "dark"


def test_effective_theme_uses_system_when_auto(monkeypatch):
    monkeypatch.setattr(theme, "detect_system_theme", lambda: "dark")
    assert theme.effective_theme("auto") == "dark"


def test_toggle_icon_for_theme():
    assert theme.toggle_icon_for("dark") == "☀  Light"
    assert theme.toggle_icon_for("light") == "🌙  Dark"
