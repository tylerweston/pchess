from pchess.models import SingleGame


def test_new_singlegame():
    sg = SingleGame(name="testgame")
    assert sg.name == "testgame"