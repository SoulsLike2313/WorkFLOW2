from voice_launcher_app.core.matching import command_match_score, find_best_command


def test_exact_match_wins():
    commands = {"запусти танки": {"path": "X"}}
    result = find_best_command(["запусти танки"], commands, base_threshold=0.72)
    assert result.phrase == "запусти танки"
    assert result.score == 1.0


def test_short_fragment_matches_expected_phrase():
    commands = {"танки": {"path": "X"}, "запрет": {"path": "Y"}}
    result = find_best_command(["та"], commands, base_threshold=0.72)
    assert result.phrase == "танки"
    assert result.score >= 0.66


def test_short_fragment_wrong_first_letter_rejected():
    commands = {"танки": {"path": "X"}}
    result = find_best_command(["зо"], commands, base_threshold=0.72)
    assert result.phrase is None


def test_score_prefers_prefix():
    assert command_match_score("тан", "танки") > command_match_score("тан", "запрет")
