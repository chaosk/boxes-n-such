include <../common.scad>

MEEPLES_TOKENS_Y = 195;
MEEPLES_TOKENS_Z = 22;

MEEPLES_RIGHT_COLUMN_X = 86.5;

BOTTOM_ROW_Y = 46;

WORKER_Y = 22;
CHILDREN_Y = 25;

SPECIAL_BUILDINGS_X = 101;
SPECIAL_BUILDINGS_Y = 38.5;

SPENT_WORKERS_X = 24;
SPENT_WORKERS_Y = 53;
// last row is slightly larger
LARGER_TOKENS_X = 29;

AUTOMATONS_X = 71;
AUTOMATONS_Y = 63;

COAL_X = 50;
COAL_Y = AUTOMATONS_Y;

TREES_X = 32.5;
TREES_X_2 = 16;
TREES_Y = 127;
TREE_BUMP_Z = MEEPLES_TOKENS_Z - 6;

STEEL_X = 45;

WOOD_X = AUTOMATONS_X + COAL_X - TREES_X - TREES_X_2 - WALL;
WOOD_Y = TREES_Y - BOTTOM_ROW_Y - WALL;

SCENARIO_TOKENS_X = 46;
// that shape behind wood comparment
SCENARIO_TOKENS_X_2 = 20;

function meeples_tokens() = [
    "Meeples/Tokens tray",
    [

        [BOX_SIZE_XYZ, [LEFT_SIDE_GROUP_X, MEEPLES_TOKENS_Y, MEEPLES_TOKENS_Z + BASE_HEIGHT]],
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
        [BOX_COMPONENT, [
                [POSITION_XY, [TREES_X + TREES_X_2 + WOOD_X + 3 * WALL, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [SCENARIO_TOKENS_X_2, SPENT_WORKERS_Y, MEEPLES_TOKENS_Z]],
            ],
        ],
        // Spent workers, scenario-specific tokens, etc.
        [BOX_COMPONENT, [
                [POSITION_XY, [TREES_X + TREES_X_2 + STEEL_X + SCENARIO_TOKENS_X + 4 * WALL, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [SPENT_WORKERS_X, SPENT_WORKERS_Y, MEEPLES_TOKENS_Z]],
                [CMP_NUM_COMPARTMENTS_XY, [2, 1]],
            ],
        ],
        [BOX_COMPONENT, [
                [POSITION_XY, [MAX, 0]],
                [CMP_COMPARTMENT_SIZE_XYZ, [LARGER_TOKENS_X, SPENT_WORKERS_Y, MEEPLES_TOKENS_Z]],
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
                [POSITION_XY, [MAX, SPENT_WORKERS_Y + WALL]],
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
        // 2 x Worker row (Workers, Engineers, Children, Steam Cores)
        [BOX_COMPONENT, [
                [POSITION_XY, [AUTOMATONS_X + COAL_X + 2 * WALL, MAX]],
                [CMP_COMPARTMENT_SIZE_XYZ, [MEEPLES_RIGHT_COLUMN_X, WORKER_Y, MEEPLES_TOKENS_Z]],
                [CMP_NUM_COMPARTMENTS_XY, [1, 2]],
                [CMP_CUTOUT_SIDES_4B, [false, false, false, true]],
                [CMP_CUTOUT_HEIGHT_PCT, 60],
                [CMP_CUTOUT_WIDTH_PCT, 65],
            ],
        ],
        // 2 x Worker-like row - those meeples are higher (Children, Steam Cores)
        [BOX_COMPONENT, [
                [POSITION_XY, [AUTOMATONS_X + COAL_X + 2 * WALL, SPENT_WORKERS_Y + SPECIAL_BUILDINGS_Y + 2 * WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [MEEPLES_RIGHT_COLUMN_X, CHILDREN_Y, MEEPLES_TOKENS_Z]],
                [CMP_NUM_COMPARTMENTS_XY, [1, 2]],
                [CMP_CUTOUT_SIDES_4B, [false, false, false, true]],
                [CMP_CUTOUT_HEIGHT_PCT, 60],
                [CMP_CUTOUT_WIDTH_PCT, 65],
            ],
        ],
        // Separate compartment for worker bumpers
        [BOX_COMPONENT, [
                [POSITION_XY, [MAX, MAX]],
                [CMP_COMPARTMENT_SIZE_XYZ, [9 * 1.5, WORKER_Y, MEEPLES_TOKENS_Z]],
                [CMP_NUM_COMPARTMENTS_XY, [1, 2]],
            ],
        ],
        [BOX_COMPONENT, [
                [POSITION_XY, [MAX, SPENT_WORKERS_Y + SPECIAL_BUILDINGS_Y + 2 * WALL]],
                [CMP_COMPARTMENT_SIZE_XYZ, [9 * 1.5, CHILDREN_Y, MEEPLES_TOKENS_Z]],
                [CMP_NUM_COMPARTMENTS_XY, [1, 2]],
            ],
        ],
    ]
];
