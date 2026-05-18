"""Preview: centralized light/dark design tokens for the modern minimalist UI update."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ThemeTokens:
    bg_primary: str
    bg_surface: str
    bg_elevated: str
    text_primary: str
    text_secondary: str
    text_tertiary: str
    accent: str
    border: str
    shadow_1: str
    shadow_2: str
    shadow_3: str
    radius_sm: int = 6
    radius_md: int = 10
    radius_lg: int = 16
    radius_xl: int = 24
    spacing_xs: int = 4
    spacing_sm: int = 8
    spacing_md: int = 16
    spacing_lg: int = 24
    spacing_xl: int = 40
    spacing_xxl: int = 64
    font_label: int = 11
    font_body: int = 13
    font_subhead: int = 15
    font_title: int = 17
    font_large_title: int = 22


LIGHT_TOKENS = ThemeTokens(
    bg_primary="#F9F9F9",
    bg_surface="#FFFFFF",
    bg_elevated="#F2F2F2",
    text_primary="#111111",
    text_secondary="#6B6B6B",
    text_tertiary="#AAAAAA",
    accent="#0A84FF",
    border="rgba(0,0,0,0.08)",
    shadow_1="0 1px 3px rgba(0,0,0,0.08)",
    shadow_2="0 4px 20px rgba(0,0,0,0.10)",
    shadow_3="0 8px 40px rgba(0,0,0,0.14)",
)

DARK_TOKENS = ThemeTokens(
    bg_primary="#111111",
    bg_surface="#1C1C1E",
    bg_elevated="#2C2C2E",
    text_primary="#F5F5F5",
    text_secondary="#8E8E93",
    text_tertiary="#48484A",
    accent="#0A84FF",
    border="rgba(255,255,255,0.08)",
    shadow_1="0 1px 3px rgba(0,0,0,0.08)",
    shadow_2="0 4px 20px rgba(0,0,0,0.10)",
    shadow_3="0 8px 40px rgba(0,0,0,0.14)",
)
