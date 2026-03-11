from voice_launcher_app.ui.theme import PREMIUM_PALETTE, mix_hex, premium_glow_colors


def test_mix_hex_bounds():
    left = PREMIUM_PALETTE["hero_left"]
    right = PREMIUM_PALETTE["hero_right"]
    assert mix_hex(left, right, 0.0) == left
    assert mix_hex(left, right, 1.0) == right


def test_premium_glow_has_enough_steps_and_warm_tail():
    colors = list(premium_glow_colors())
    assert len(colors) >= 8
    assert colors[-1].startswith("#FF")
