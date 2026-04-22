extends CanvasLayer
class_name DebugOverlay

var _text: RichTextLabel


func _ready() -> void:
    layer = 20

    var panel := PanelContainer.new()
    panel.set_anchors_preset(Control.PRESET_TOP_LEFT)
    panel.position = Vector2(12, 12)
    panel.size = Vector2(620, 420)
    add_child(panel)

    var margin := MarginContainer.new()
    margin.set_anchors_preset(Control.PRESET_FULL_RECT)
    margin.add_theme_constant_override("margin_left", 8)
    margin.add_theme_constant_override("margin_top", 8)
    margin.add_theme_constant_override("margin_right", 8)
    margin.add_theme_constant_override("margin_bottom", 8)
    panel.add_child(margin)

    _text = RichTextLabel.new()
    _text.set_anchors_preset(Control.PRESET_FULL_RECT)
    _text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
    _text.scroll_active = false
    margin.add_child(_text)


func update_overlay(snapshot: Dictionary, events: Array[String]) -> void:
    var state_counts: Dictionary = snapshot.get("state_counts", {})
    var poi_population: Dictionary = snapshot.get("poi_population", {})
    var lines: Array[String] = []

    lines.append("SANDBOX FANTASY 3D MVP")
    lines.append("Tick %d | Time %.1fs" % [int(snapshot.get("tick", 0)), float(snapshot.get("time", 0.0))])
    lines.append("")

    lines.append(
        "Population: %d alive (H:%d M:%d, Brute:%d) | deaths total: %d"
        % [
            int(snapshot.get("alive_total", 0)),
            int(snapshot.get("humans_alive", 0)),
            int(snapshot.get("monsters_alive", 0)),
            int(snapshot.get("brute_alive", 0)),
            int(snapshot.get("deaths_total", 0))
        ]
    )
    lines.append(
        "Avg HP: %.1f | Avg Energy: %.1f"
        % [float(snapshot.get("avg_hp", 0.0)), float(snapshot.get("avg_energy", 0.0))]
    )
    lines.append(
        "Melee hits: %d | Magic hits: %d | Casts: %d (bolt:%d nova:%d) | Kills: %d"
        % [
            int(snapshot.get("melee_hits_total", 0)),
            int(snapshot.get("magic_hits_total", 0)),
            int(snapshot.get("casts_total", 0)),
            int(snapshot.get("bolt_casts_total", 0)),
            int(snapshot.get("nova_casts_total", 0)),
            int(snapshot.get("kills_total", 0))
        ]
    )
    lines.append(
        "Flee events: %d | Engagement transitions: %d"
        % [
            int(snapshot.get("flee_events_total", 0)),
            int(snapshot.get("engagements_total", 0))
        ]
    )
    lines.append("")
    lines.append(
        "States: wander=%d poi=%d detect=%d chase=%d attack=%d cast=%d nova=%d flee=%d"
        % [
            int(state_counts.get("wander", 0)),
            int(state_counts.get("poi", 0)),
            int(state_counts.get("detect", 0)),
            int(state_counts.get("chase", 0)),
            int(state_counts.get("attack", 0)),
            int(state_counts.get("cast", 0)),
            int(state_counts.get("cast_nova", 0)),
            int(state_counts.get("flee", 0))
        ]
    )
    lines.append("")
    lines.append(_format_poi_population(poi_population))
    lines.append("")
    lines.append("Recent events:")

    if events.is_empty():
        lines.append("- (none)")
    else:
        for item in events:
            lines.append("- %s" % item)

    _text.text = "\n".join(lines)


func _format_poi_population(poi_population: Dictionary) -> String:
    if poi_population.is_empty():
        return "POI: none"

    var chunks: Array[String] = []
    for poi_name in poi_population.keys():
        var counts: Dictionary = poi_population.get(poi_name, {})
        chunks.append(
            "%s(H:%d M:%d)"
            % [
                poi_name,
                int(counts.get("human", 0)),
                int(counts.get("monster", 0))
            ]
        )

    chunks.sort()
    return "POI occupancy: %s" % " | ".join(chunks)
