include <common.scad>

GENERATOR_X = LEFT_SIDE_GROUP_X - 2 * WALL;
GENERATOR_Y = 110;
GENERATOR_Z = 108; // FIXME Need to accomodate for rulebooks/cardboards.

function generator() = [
    "Generator container",
    [
        [BOX_SIZE_XYZ, [LEFT_SIDE_GROUP_X, GENERATOR_Y + 2 * WALL, GENERATOR_Z + BASE_HEIGHT]],
        [BOX_NO_LID_B, true],
        [BOX_COMPONENT, [
                [POSITION_XY, [0, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [GENERATOR_X, GENERATOR_Y, GENERATOR_Z]],
                [CMP_CUTOUT_SIDES_4B, [true, true, false, false]],
                [CMP_CUTOUT_HEIGHT_PCT, 60],
			    [CMP_CUTOUT_WIDTH_PCT, 80],
            ],
        ],
    ]
];
