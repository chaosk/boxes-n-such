include <../common.scad>

BUILDING_TILE_X = 33;
BUILDING_TILE_DOUBLE_X = 65;
BUILDING_TILE_Y = 33;
BUILDING_TILE_Z = 2.5;
BUILDING_TILE_THICKNESS = 2.5;

COMPARTMENT_DEPTH = BUILDING_TILE_Z * 5;

BUILDINGS_COMMON = [
	[CMP_PADDING_XY, [WALL, WALL]],
    [CMP_CUTOUT_SIDES_4B, [false, false, true, true]],
    [CMP_CUTOUT_HEIGHT_PCT, 90],
    [CMP_CUTOUT_WIDTH_PCT, 65],
    [CMP_CUTOUT_DEPTH_PCT, 10],
];

BUILDINGS_BOX_X = BUILDING_TILE_X * 3 + 4 * WALL;
BUILDINGS_BOX_Y = 195;
// Center the compartments in the box
BUILDINGS_OFFSET = ( BUILDINGS_BOX_Y - (5 * BUILDING_TILE_X + 6 * WALL) ) / 2;


function buildings_tray() = [
    "Buildings tray",
    [
        [BOX_SIZE_XYZ, [BUILDINGS_BOX_X, BUILDINGS_BOX_Y, COMPARTMENT_DEPTH + BASE_HEIGHT]],
        [BOX_STACKABLE_B, true],
        [BOX_LID, [
	        	[LID_INSET_B, true],
	        	[LID_TABS_4B, [true, true, false, false]],
        	]
        ],
        [BOX_COMPONENT, concat([
                [POSITION_XY, [0, BUILDINGS_OFFSET]],
                [CMP_COMPARTMENT_SIZE_XYZ, [BUILDING_TILE_X, BUILDING_TILE_Y, COMPARTMENT_DEPTH]],
                [CMP_NUM_COMPARTMENTS_XY, [1, 3]],
            ], BUILDINGS_COMMON),
        ],
        [BOX_COMPONENT, concat([
                [POSITION_XY, [BUILDING_TILE_X + WALL, BUILDINGS_OFFSET]],
                [CMP_COMPARTMENT_SIZE_XYZ, [BUILDING_TILE_DOUBLE_X + WALL, BUILDING_TILE_Y, COMPARTMENT_DEPTH]],
                [CMP_NUM_COMPARTMENTS_XY, [1, 3]],
            ], BUILDINGS_COMMON),
        ],
        [BOX_COMPONENT, concat([
                [POSITION_XY, [0, BUILDINGS_OFFSET + BUILDING_TILE_Y * 3 + 3 * WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [BUILDING_TILE_X, BUILDING_TILE_Y, COMPARTMENT_DEPTH]],
                [CMP_NUM_COMPARTMENTS_XY, [3, 2]],
            ], BUILDINGS_COMMON),
        ],
    ]
];
