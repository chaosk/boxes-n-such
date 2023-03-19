include <common.scad>

MAP_TILES_X = 48;
MAP_TILES_Y = 87;
MAP_TILES_EMPTY_Y = 30;
MAP_TILES_Z = 84; // FIXME Need to accomodate for rulebooks/cardboards.

MAP_TILES_COMMON = [
	[CMP_COMPARTMENT_SIZE_XYZ, [MAP_TILES_X, MAP_TILES_Y, MAP_TILES_Z]],
	[CMP_SHAPE, HEX],
	[CMP_SHAPE_ROTATED_B, true],
	[CMP_CUTOUT_SIDES_4B, [false, false, true, true]],
    [CMP_CUTOUT_HEIGHT_PCT, 60],
    [CMP_CUTOUT_WIDTH_PCT, 60],
];

MAP_TILES_BOX_Y = 210;

function map_tiles() = [
    "Map tiles",
    [
        [BOX_SIZE_XYZ, [MAP_TILES_X + 2 * WALL, MAP_TILES_BOX_Y, MAP_TILES_Z + BASE_HEIGHT]],
        [BOX_NO_LID_B, true],
        [BOX_COMPONENT, concat([
                [POSITION_XY, [0, 0]],  
            ],
            MAP_TILES_COMMON)
        ],
        [BOX_COMPONENT, [
                [POSITION_XY, [0, MAP_TILES_Y + WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [MAP_TILES_X, MAP_TILES_EMPTY_Y, MAP_TILES_Z]],
                [CMP_CUTOUT_SIDES_4B, [false, false, true, true]],
			    [CMP_CUTOUT_HEIGHT_PCT, 40],
			    [CMP_CUTOUT_WIDTH_PCT, 70],
            ],
        ],
        [BOX_COMPONENT, concat([
                [POSITION_XY, [0, MAP_TILES_Y + MAP_TILES_EMPTY_Y + 2 * WALL]],
            ],
            MAP_TILES_COMMON)
        ],
    ]
];
