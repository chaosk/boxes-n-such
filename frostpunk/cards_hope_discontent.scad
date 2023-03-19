include <common.scad>

BAGS_X = RIGHT_SIDE_GROUP_X - 2 * WALL;
BAGS_Y = 65.5;
CARDS_AND_BAGS_Z = 98;

CARDS_Y = 66;

// Technology and Weather decks
CARDS_X_1 = 25;

// Expedition decks
CARDS_X_2 = 29;

// Citizens deck
CARDS_X_3 = 21;

CARDS_COMMON = [
    [CMP_CUTOUT_SIDES_4B, [false, false, true, false]],
    [CMP_CUTOUT_HEIGHT_PCT, 60],
    [CMP_CUTOUT_WIDTH_PCT, 70],
];

CHD_BOX_Y = BAGS_Y + CARDS_Y + 3 * WALL;

assert(CARDS_X_1 + CARDS_X_2 + CARDS_X_3 + 4 * WALL == RIGHT_SIDE_GROUP_X);

function cards_hope_discontent() = [
    "Smaller cards tray and Hope/Discontent bags",
    [
        [BOX_SIZE_XYZ, [RIGHT_SIDE_GROUP_X, CHD_BOX_Y, CARDS_AND_BAGS_Z + BASE_HEIGHT]],
        [BOX_NO_LID_B, true],
        // Hope/Discontent
        [BOX_COMPONENT, [
                [POSITION_XY, [0, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [BAGS_X, BAGS_Y, CARDS_AND_BAGS_Z]],
            ],
        ],
        // Card tray - Technology/Weather decks
        [BOX_COMPONENT, concat(
            [
                [POSITION_XY, [0, BAGS_Y + WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [CARDS_X_1, CARDS_Y, CARDS_AND_BAGS_Z]],
            ],
            CARDS_COMMON)
        ],
        // Card tray - Expedition decks
        [BOX_COMPONENT, concat(
            [
                [POSITION_XY, [CARDS_X_1 + WALL, BAGS_Y + WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [CARDS_X_2, CARDS_Y, CARDS_AND_BAGS_Z]],
            ],
            CARDS_COMMON)
        ],
        // Card tray - Citizens deck
        [BOX_COMPONENT, concat(
            [
                [POSITION_XY, [CARDS_X_1 + CARDS_X_2 + 2 * WALL, BAGS_Y + WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [CARDS_X_3, CARDS_Y, CARDS_AND_BAGS_Z]],
            ],
            CARDS_COMMON)
        ],
    ]
];
