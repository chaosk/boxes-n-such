from .kit import Project
from .parts import Aliens, Cards


def do():
    project = Project(
        (
            Aliens("aliens"),
            Cards("cards_1"),
            Cards("cards_2"),
        ),
        show_object=show_object,
    )
    return project


if __file__ == "__main__":
    project = do()
