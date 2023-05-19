import cadquery as cq

from ..kit import Part


class Aliens(Part):
    """
    Box for alien cards.

    Print once.
    """

    size = (178, 120, 75)
    x_cutout_size = (75, 73, 100)
    y_cutout_size = (130, 73, 100)
    bottom_cutout_size = (138, 80)
    bottom_shell_fillet_radius = 6
    outer_shell_fillet_radius = 3

    def make(self):
        model = (
            cq.Workplane("XY")
            .box(*self.size)
            # Smooth the edges
            .edges("|Z")
            .fillet(1)
            # Remove the box fill
            .faces("+Z")
            .shell(1.5)
        )
        # Cutout sides for easier removal
        model = self.place_cutout(model, "+X", self.x_cutout_size)
        model = self.place_cutout(model, "+Y", self.y_cutout_size)
        # Round the upper edges of the cutouts
        return (
            model.faces(">Z")
            .edges(">X[0] or >X[-1] or >Y[0] or >Y[-1]")
            .fillet(self.outer_shell_fillet_radius)
            # Cut the bottom out
            .faces("<Z")
            .workplane()
            .placeSketch(self.cutout_bottom_shape())
            .cutThruAll()
        )

    def cutout_side_shape(self, size):
        # Make a trapezoid that's rounded at the bottom
        # (top is handled after cutting out the shape from the face)
        return (
            cq.Sketch()
            .trapezoid(*size)
            .vertices("<Y")
            .fillet(self.outer_shell_fillet_radius)
        )

    def cutout_bottom_shape(self):
        # Make a rounded rectangle
        return (
            cq.Sketch()
            .rect(*self.bottom_cutout_size)
            .vertices()
            .fillet(self.bottom_shell_fillet_radius)
        )

    def place_cutout(self, workplane, selector, size):
        return (
            workplane.faces(selector)
            .workplane()
            # Offset so that we can reach top edge without cutting through bottom edge as well
            .center(0, 1)
            .placeSketch(self.cutout_side_shape(size))
            .cutThruAll()
        )
