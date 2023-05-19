from .kit import Project
from .parts import Aliens, Cards


aliens = Aliens().make()
cards = Cards().make()
# project = Project(
#     aliens=Aliens(),
#     cards1=Cards(),
#     cards2=Cards(),
# )
# show_object(project.assembly)

# project = Project(
#     (Aliens(), Cards(), Cards())
# )
