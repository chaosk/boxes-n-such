include <parts/tarot_cards.scad>
include <parts/cards_hope_discontent.scad>
include <parts/setup_components.scad>
include <parts/generator.scad>
include <parts/map_tiles.scad>
include <parts/meeples_tokens.scad>
include <parts/buildings_tray.scad>

data = [
	tarot(),
	cards_hope_discontent(),
	setup_components(),
	generator(),
	map_tiles(),
    meeples_tokens(),
    buildings_tray(),
];

MakeAll();
