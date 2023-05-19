import enum
import math
from dataclasses import dataclass

import cadquery as cq

BOX_XY = 76.6
BOX_Z = 42

LID_X = 74.5
LID_Y = 74
LID_Z = 2

PLANET_HOLE_DIAMETER = 73
PLANET_HOLE_DEPTH = 13.5
POINT_MARKER_DIAMETER = 25.55
POINT_MARKER_DEPTH = 4.5

SHIP_WELL_CIRCLE_RARIUS = 26.5

POINT_MARKET_FINGER = (20, 15, 45)
SHIP_WELL_FINGER = (25, 15, 90)


def polygon_point(radius, total_vertices, offset=0, *, idx):
    radians = idx * (2 * math.pi / total_vertices) + offset
    return radius * math.cos(radians), radius * math.sin(radians)


def polygon_points(radius, total_vertices, offset=0):
    for idx in range(total_vertices):
        yield polygon_point(radius, total_vertices, offset, idx=idx)


workplane = (
    cq.Workplane("XY")
    .box(BOX_XY, BOX_XY, BOX_Z)
    .edges("|Z")
    .fillet(1)
    .edges("|Y")
    .fillet(0.4)
)
base = workplane.faces(">Z").workplane()

box = (
    base
    # Planets hole
    .hole(PLANET_HOLE_DIAMETER, PLANET_HOLE_DEPTH)
    .tag("top")
    # Ship wells
    .pushPoints(polygon_points(SHIP_WELL_CIRCLE_RARIUS, 5))
    .hole(26.5, 39.5)
)

# Ship well finger holes


class ShipWellDirection(enum.Enum):
    LEFT = "left"
    RIGHT = "right"
    BOTTOM = "bottom"
    TOP = "top"


@dataclass
class ShipWell:
    direction: ShipWellDirection = ShipWellDirection.BOTTOM

    def offset(self) -> float:
        return {
            ShipWellDirection.BOTTOM: 0,
            ShipWellDirection.RIGHT: math.pi / 2,
            ShipWellDirection.TOP: math.pi,
            ShipWellDirection.LEFT: 3 * math.pi / 2,
        }[self.direction]

    def position(self, point: tuple[float, float]) -> tuple[float, float]:
        x1, y1 = point
        x2, y2 = polygon_point(POINT_MARKER_DIAMETER, 3, offset=self.offset(), idx=0)

        return x1 + x2 / 2, y1 + y2 / 2

    def size(self, size: tuple[float, float, float]) -> tuple[float, float, float]:
        if self.direction in (ShipWellDirection.BOTTOM, ShipWellDirection.TOP):
            return size
        return (*size[1::-1], size[2])


SHIP_WELLS = (
    ShipWell(),
    ShipWell(ShipWellDirection.RIGHT),
    ShipWell(ShipWellDirection.TOP),
    ShipWell(ShipWellDirection.TOP),
    ShipWell(ShipWellDirection.LEFT),
)

for ship_well, point in zip(
    SHIP_WELLS, list(polygon_points(SHIP_WELL_CIRCLE_RARIUS, 5))
):
    box = box.cut(
        base.center(*ship_well.position(point))
        .box(*ship_well.size(SHIP_WELL_FINGER), combine=False)
        .edges("|Z")
        .fillet(5)
    )

box = (
    box
    # Point marker
    .workplaneFromTagged("top")
    .hole(POINT_MARKER_DIAMETER, PLANET_HOLE_DEPTH + POINT_MARKER_DEPTH)
    .cut(
        box.center(
            *(
                p / 2
                for p in polygon_point(
                    POINT_MARKER_DIAMETER, 3, offset=11 * math.pi / 18, idx=0
                )
            )
        ).cylinder(36, 3.5, combine=False)
    )
    .cut(
        box.center(
            *(
                p / 2
                for p in polygon_point(
                    POINT_MARKER_DIAMETER, 3, offset=25 * math.pi / 18, idx=0
                )
            )
        ).cylinder(36, 3.5, combine=False)
    )
)

# Point marker finger hole
box = box.cut(
    base.center(*(p / 2 for p in polygon_point(POINT_MARKER_DIAMETER, 3, 0, idx=0)))
    .box(*POINT_MARKET_FINGER, combine=False)
    .edges("|Z")
    .fillet(5)
)

box = box.edges("|Z").fillet(0.4)


def make_lid(x, y, z):
    lid_base = cq.Workplane("XY", (-1, 0, 20)).box(x, y, z)
    lid_base = lid_base.faces(">Z").edges("#Y").chamfer(1.99, 1.5)
    lid_base = lid_base.edges("|Z").fillet(1)
    lid_base = lid_base.cut(
        lid_base.workplane()
        .center(35, 37.5)
        .lineTo(-2.0, 0)
        .threePointArc((-1.0, -2.0), (0.0, 0.0))
        .close()
        .extrude(LID_Z, combine=False, both=True)
    )
    lid_base = lid_base.cut(
        lid_base.workplane()
        .center(35, -37.5)
        .lineTo(-2.0, 0)
        .threePointArc((-1.0, 2.0), (0.0, 0.0))
        .close()
        .extrude(LID_Z, combine=False, both=True)
    )
    return lid_base


lid = make_lid(LID_X, LID_Y, LID_Z)
lid = lid.cut(lid.center(32, -34).box(11, 1, LID_Z, combine=False))
lid = lid.cut(lid.center(32, 34).box(11, 1, LID_Z, combine=False))
lid = lid.cut(
    lid.faces(">Z").workplane().center(-31, 0).box(10, 32, 1.5, combine=False)
)

box = box.cut(make_lid(LID_X + 0.5, LID_Y, LID_Z))

# box = box.box(BOX_XY, BOX_XY, BOX_Z)
