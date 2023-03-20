include <../common.scad>

TAROT_X = RIGHT_SIDE_GROUP_X - 2 * WALL;
TAROT_Z = 125;

// Morning deck
TAROT_Y_1 = 25;

// Social Dispute deck
TAROT_Y_2 = 8;

// Dusk deck
TAROT_Y_3 = 43;

// Law Consequences cards
TAROT_Y_4 = 24;

// Law cards
TAROT_Y_5 = 14;

// Society cards
TAROT_Y_6 = 12;

// Scenario cards
TAROT_Y_7 = 27;

TAROT_COMMON = [
    [CMP_CUTOUT_SIDES_4B, [true, false, false, false]],
    [CMP_CUTOUT_HEIGHT_PCT, 60],
    [CMP_CUTOUT_WIDTH_PCT, 70],
];

TAROT_BOX_Y = TAROT_Y_1 + TAROT_Y_2 + TAROT_Y_3 + TAROT_Y_4 + TAROT_Y_5 + TAROT_Y_6 + TAROT_Y_7 + 8 * WALL;

function tarot() = [
    "Tarot-sized card tray",
    [
        [BOX_SIZE_XYZ, [RIGHT_SIDE_GROUP_X, TAROT_BOX_Y, TAROT_Z + BASE_HEIGHT]],
        [BOX_NO_LID_B, true],
        [BOX_COMPONENT, concat(
            [
                [POSITION_XY, [0, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [TAROT_X, TAROT_Y_1, TAROT_Z]],
            ],
            TAROT_COMMON)
        ],
        [BOX_COMPONENT, concat(
            [
                [POSITION_XY, [0, TAROT_Y_1 + WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [TAROT_X, TAROT_Y_2, TAROT_Z]],
            ],
            TAROT_COMMON)
        ],
        [BOX_COMPONENT, concat(
            [
                [POSITION_XY, [0, TAROT_Y_1 + TAROT_Y_2 + 2 * WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [TAROT_X, TAROT_Y_3, TAROT_Z]],
            ],
            TAROT_COMMON)
        ],
        [BOX_COMPONENT, concat(
            [
                [POSITION_XY, [0, TAROT_Y_1 + TAROT_Y_2 + TAROT_Y_3 + 3 * WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [TAROT_X, TAROT_Y_4, TAROT_Z]],
            ],
            TAROT_COMMON)
        ],
        [BOX_COMPONENT, concat(
            [
                [POSITION_XY, [0, TAROT_Y_1 + TAROT_Y_2 + TAROT_Y_3 + TAROT_Y_4 + 4 * WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [TAROT_X, TAROT_Y_5, TAROT_Z]],
            ],
            TAROT_COMMON)
        ],
        [BOX_COMPONENT, concat(
            [
                [POSITION_XY, [0, TAROT_Y_1 + TAROT_Y_2 + TAROT_Y_3 + TAROT_Y_4 + TAROT_Y_5 + 5 * WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [TAROT_X, TAROT_Y_6, TAROT_Z]],
            ],
            TAROT_COMMON)
        ],
        [BOX_COMPONENT, concat(
            [
                [POSITION_XY, [0, TAROT_Y_1 + TAROT_Y_2 + TAROT_Y_3 + TAROT_Y_4 + TAROT_Y_5 + TAROT_Y_6 + 6 * WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [TAROT_X, TAROT_Y_7, TAROT_Z]],
            ],
            TAROT_COMMON)
        ],
    ]
];
