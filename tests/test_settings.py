from wordle.settings import Settings


def test_settings() -> None:
    settings = Settings()
    assert settings.guess_len == 5
    assert settings.num_guesses == 6
