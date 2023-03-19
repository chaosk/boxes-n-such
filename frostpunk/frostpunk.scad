include <tarot_cards.scad>
include <cards_hope_discontent.scad>
include <setup_components.scad>
include <generator.scad>
include <map_tiles.scad>
include <meeples_tokens.scad>
include <buildings_tray.scad>

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