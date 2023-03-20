include <../common.scad>

BUILDINGS_X = 100;
BUILDINGS_Y = 100;
BUILDINGS_Z = 100;

function buildings_tray() = [
    "Buildings tray",
    [
        [BOX_SIZE_XYZ, [BUILDINGS_X, BUILDINGS_Y, BUILDINGS_Z + BASE_HEIGHT]],
        [BOX_NO_LID_B, true],
    ]
];
