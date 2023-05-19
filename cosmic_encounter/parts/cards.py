import cadquery as cq

from ..kit import Part


class Cards(Part):
    """
    Box for regular size cards (sans Flare cards).

    Print twice.
    """

    size = (92, 60, 75)
    finger_hole_size = (45, 35)
    outer_rim_fillet = 1
    fillet_radius = 3

    def make(self):
        model = (
            cq.Workplane("XY")
            .box(*self.size)
            # Smooth the edges
            .edges("|Z")
            .fillet(self.outer_rim_fillet)
            # Remove the box fill
            .faces("+Z")
            .shell(1.5)
            .faces("<X")
            .workplane()
            .placeSketch((
	            cq.Sketch()
	            .rect(1, self.size[2])
	        ))
            .cutBlind("next")
            .faces("<Z")
            .workplane()
            .placeSketch((
	            cq.Sketch()
	            .rect(*self.finger_hole_size)
	            .vertices("<Z")
	            .fillet(self.fillet_radius)
	        )).cutThruAll()
	        .faces(">Z")
            .edges(">X[0]")
            .fillet(self.fillet_radius)
        )
        return model
