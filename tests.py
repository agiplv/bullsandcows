from time import sleep

from bullsandcows import BullAndCows

game = BullAndCows()
chat_id = "123456789"
game.reset_game(chat_id)


def test_init():
    assert 4 == game.size
    assert "0123456789" == game.digits
    assert "" == game.get_secret(chat_id)
    assert not game.get_win(chat_id)
    assert 0 == game.get_attempts(chat_id)


def test_validation():
    assert not game.validate("1111")
    assert not game.validate("test")
    assert not game.validate("12345")
    assert game.validate("1234")


def test_get_bulls_and_cows():
    secret = "1234"
    assert (4, 0) == game.get_bull_and_cows("1234", secret)
    assert (3, 0) == game.get_bull_and_cows("1230", secret)
    assert (0, 4) == game.get_bull_and_cows("4321", secret)
    assert (0, 3) == game.get_bull_and_cows("4320", secret)
    assert (2, 2) == game.get_bull_and_cows("1243", secret)


def test_set_bull_and_cows_message():
    assert "🐂\n1 Bull" == game.set_bull_and_cows_message(1, 0)
    assert "🐂🐂🐂🐂\n4 Bulls" == game.set_bull_and_cows_message(4, 0)
    assert "🐄🐄🐄🐄\n4 Cows" == game.set_bull_and_cows_message(0, 4)
    assert "🐂🐄\n1 Bull and 1 Cow" == game.set_bull_and_cows_message(1, 1)
    assert "🐂🐂🐄🐄\n2 Bulls and 2 Cows" == game.set_bull_and_cows_message(2, 2)
    assert "\n0 Bulls and 0 Cows" == game.set_bull_and_cows_message(0, 0)


def test_game():
    game.test = True
    game.start_game(chat_id)
    secret = game.get_secret(chat_id)
    assert "1234" == secret
    assert not game.get_win(chat_id)
    assert 0 == game.get_attempts(chat_id)
    problem = "Problem, try again. You need to enter %i unique digits from 0 to 9" % game.size

    assert (problem, False) == game.guess("test", chat_id)
    assert ("🐂🐂🐄🐄\n2 Bulls and 2 Cows", True) == game.guess("1243", chat_id)
    assert 1 == game.get_attempts(chat_id)
    assert ("WIN!!!", True) == game.guess("1234", chat_id)
    assert game.get_win(chat_id)

    game.restart_game(chat_id)
    secret = game.get_secret(chat_id)
    assert "1234" == secret
    assert not game.get_win(chat_id)
    assert 0 == game.get_attempts(chat_id)


def test_reset_game():
    game.reset_game(chat_id)
    assert "" == game.get_secret(chat_id)
    assert not game.get_win(chat_id)
    assert 0 == game.get_attempts(chat_id)
