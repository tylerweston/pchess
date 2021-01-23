from pchess.models import SingleGame

# Models without hitting the database
def test_new_singlegame():
    sg = SingleGame(name="testgame")
    assert sg.name == "testgame"