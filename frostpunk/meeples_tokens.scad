include <common.scad>

MEEPLES_TOKENS_X = LEFT_SIDE_GROUP_X - 2 * WALL;
MEEPLES_TOKENS_Y = 207;
MEEPLES_TOKENS_Z = 22; // FIXME Need to accomodate for rulebooks/cardboards.

MEEPLES_RIGHT_COLUMN_X = 9 * 10.5 - WALL;

BOTTOM_ROW_Y = 61;

WORKER_Y = 25;

SPECIAL_BUILDINGS_X = 9 * 12;
SPECIAL_BUILDINGS_Y = 40.5;

SPENT_WORKERS_X = 29;

AUTOMATONS_X = 71;
AUTOMATONS_Y = 66;

COAL_X = 50;
COAL_Y = 66;

TREES_X = 35.5;
TREES_X_2 = 18;
TREES_Y = 139;
TREE_BUMP_Z = MEEPLES_TOKENS_Z - 6;

STEEL_X = 40;

WOOD_X = AUTOMATONS_X + COAL_X - TREES_X - TREES_X_2 - WALL;
WOOD_Y = TREES_Y - BOTTOM_ROW_Y - WALL;

SCENARIO_TOKENS_X = 44;

function meeples_tokens() = [
    "Meeples/Tokens tray",
    [

        [BOX_SIZE_XYZ, [MEEPLES_TOKENS_X + 2 * WALL, MEEPLES_TOKENS_Y + 2 * WALL, MEEPLES_TOKENS_Z + BASE_HEIGHT]],
        [BOX_NO_LID_B, true],
        // Trees
        [BOX_COMPONENT, [
                [POSITION_XY, [0, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [TREES_X, TREES_Y, MEEPLES_TOKENS_Z]],
            ],
        ],
        // Trees, second bit
        [BOX_COMPONENT, [
                [POSITION_XY, [TREES_X + WALL, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [TREES_X_2, TREES_Y, MEEPLES_TOKENS_Z]],
            ],
        ],
        // Trees - shave off the bump
        [BOX_COMPONENT, [
                [POSITION_XY, [TREES_X - WALL, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [WALL * 3, TREES_Y, TREE_BUMP_Z]],
            ],
        ],
        // Steel
        [BOX_COMPONENT, [
                [POSITION_XY, [TREES_X + TREES_X_2 + 2 * WALL, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [STEEL_X, BOTTOM_ROW_Y, MEEPLES_TOKENS_Z]],
                [CMP_SHAPE, FILLET],
                [CMP_SHAPE_ROTATED_B, true],
            ],
        ],
        // Scenario tokens
        [BOX_COMPONENT, [
                [POSITION_XY, [TREES_X + TREES_X_2 + STEEL_X + 3 * WALL, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [SCENARIO_TOKENS_X, BOTTOM_ROW_Y, MEEPLES_TOKENS_Z]],
            ],
        ],
        // Spent workers, scenario-specific tokens, etc.
        [BOX_COMPONENT, [
                [POSITION_XY, [MAX, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [SPENT_WORKERS_X, BOTTOM_ROW_Y, MEEPLES_TOKENS_Z]],
                [CMP_NUM_COMPARTMENTS_XY, [3, 1]],
            ],
        ],
        // Wood
        [BOX_COMPONENT, [
                [POSITION_XY, [TREES_X + TREES_X_2 + 2 * WALL, BOTTOM_ROW_Y + WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [WOOD_X, WOOD_Y, MEEPLES_TOKENS_Z]],
                [CMP_SHAPE, FILLET],
                [CMP_SHAPE_ROTATED_B, true],
            ],
        ],
        // Special buildings
        [BOX_COMPONENT, [
                [POSITION_XY, [MAX, BOTTOM_ROW_Y + WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [SPECIAL_BUILDINGS_X, SPECIAL_BUILDINGS_Y, MEEPLES_TOKENS_Z]],
            ],
        ],
        // Automatons
        [BOX_COMPONENT, [
                [POSITION_XY, [0, MAX]],
                [CMP_COMPARTMENT_SIZE_XYZ, [AUTOMATONS_X, AUTOMATONS_Y, MEEPLES_TOKENS_Z]],
            ],
        ],
        // Coal
        [BOX_COMPONENT, [
                [POSITION_XY, [AUTOMATONS_X + WALL, MAX]],
                [CMP_COMPARTMENT_SIZE_XYZ, [COAL_X, COAL_Y, MEEPLES_TOKENS_Z]],
                [CMP_SHAPE, FILLET],
                [CMP_SHAPE_ROTATED_B, true],
            ],
        ],
        // 4 x Worker row (Workers, Engineers, Children, Steam Cores)
        [BOX_COMPONENT, [
                [POSITION_XY, [AUTOMATONS_X + COAL_X + 2 * WALL, MAX]],
                [CMP_COMPARTMENT_SIZE_XYZ, [MEEPLES_RIGHT_COLUMN_X, WORKER_Y, MEEPLES_TOKENS_Z]],
                [CMP_NUM_COMPARTMENTS_XY, [1, 4]],
                [CMP_CUTOUT_SIDES_4B, [false, false, false, true]],
                [CMP_CUTOUT_HEIGHT_PCT, 60],
                [CMP_CUTOUT_WIDTH_PCT, 70],
            ],
        ],
        // Separate compartment for worker bumpers
        [BOX_COMPONENT, [
                [POSITION_XY, [MAX, MAX]],
                [CMP_COMPARTMENT_SIZE_XYZ, [9 * 1.5, WORKER_Y, MEEPLES_TOKENS_Z]],
                [CMP_NUM_COMPARTMENTS_XY, [1, 4]],
            ],
        ],
    ]
];
