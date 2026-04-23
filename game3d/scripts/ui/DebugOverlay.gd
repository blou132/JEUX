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
    var poi_snapshot: Dictionary = snapshot.get("poi_snapshot", {})
    var role_counts: Dictionary = snapshot.get("human_role_counts", {})
    var level_counts: Dictionary = snapshot.get("level_counts", {})
    var human_level_counts: Dictionary = snapshot.get("human_level_counts", {})
    var monster_level_counts: Dictionary = snapshot.get("monster_level_counts", {})
    var lines: Array[String] = []

    lines.append("SANDBOX FANTASY 3D MVP")
    lines.append("Tick %d | Time %.1fs" % [int(snapshot.get("tick", 0)), float(snapshot.get("time", 0.0))])
    lines.append("")

    lines.append(
        "Population: %d alive (H:%d M:%d, Brute:%d, Ranged:%d) | deaths total: %d"
        % [
            int(snapshot.get("alive_total", 0)),
            int(snapshot.get("humans_alive", 0)),
            int(snapshot.get("monsters_alive", 0)),
            int(snapshot.get("brute_alive", 0)),
            int(snapshot.get("ranged_alive", 0)),
            int(snapshot.get("deaths_total", 0))
        ]
    )
    lines.append(
        "Avg HP: %.1f | Avg Energy: %.1f"
        % [float(snapshot.get("avg_hp", 0.0)), float(snapshot.get("avg_energy", 0.0))]
    )
    lines.append(
        "Melee hits: %d | Magic hits: %d | Casts: %d (bolt:%d control:%d nova:%d) | Kills: %d"
        % [
            int(snapshot.get("melee_hits_total", 0)),
            int(snapshot.get("magic_hits_total", 0)),
            int(snapshot.get("casts_total", 0)),
            int(snapshot.get("bolt_casts_total", 0)),
            int(snapshot.get("control_casts_total", 0)),
            int(snapshot.get("nova_casts_total", 0)),
            int(snapshot.get("kills_total", 0))
        ]
    )
    lines.append(
        "Control applies: %d | Slowed alive: %d (H:%d M:%d)"
        % [
            int(snapshot.get("control_applies_total", 0)),
            int(snapshot.get("slowed_alive", 0)),
            int(snapshot.get("slowed_humans", 0)),
            int(snapshot.get("slowed_monsters", 0))
        ]
    )
    lines.append(
        "Human roles: fighter=%d mage=%d scout=%d"
        % [
            int(role_counts.get("fighter", 0)),
            int(role_counts.get("mage", 0)),
            int(role_counts.get("scout", 0))
        ]
    )
    lines.append(
        "Progression: avg_level=%.2f | level_ups=%d | L1=%d L2=%d L3=%d"
        % [
            float(snapshot.get("avg_level", 0.0)),
            int(snapshot.get("level_ups_total", 0)),
            int(level_counts.get("L1", 0)),
            int(level_counts.get("L2", 0)),
            int(level_counts.get("L3", 0))
        ]
    )
    lines.append(
        "Levels split H(L1/L2/L3)=%d/%d/%d M=%d/%d/%d"
        % [
            int(human_level_counts.get("L1", 0)),
            int(human_level_counts.get("L2", 0)),
            int(human_level_counts.get("L3", 0)),
            int(monster_level_counts.get("L1", 0)),
            int(monster_level_counts.get("L2", 0)),
            int(monster_level_counts.get("L3", 0))
        ]
    )
    lines.append(
        "Champions: alive=%d (H:%d M:%d) | promotions=%d | champion_kills=%d"
        % [
            int(snapshot.get("champion_alive_total", 0)),
            int(snapshot.get("human_champions_alive", 0)),
            int(snapshot.get("monster_champions_alive", 0)),
            int(snapshot.get("champion_promotions_total", 0)),
            int(snapshot.get("champion_kills_total", 0))
        ]
    )
    lines.append(
        "Flee events: %d | Engagement transitions: %d"
        % [
            int(snapshot.get("flee_events_total", 0)),
            int(snapshot.get("engagements_total", 0))
        ]
    )
    lines.append(
        "POI events: arrivals=%d contests=%d domination_shifts=%d"
        % [
            int(snapshot.get("poi_arrivals_total", 0)),
            int(snapshot.get("poi_contests_total", 0)),
            int(snapshot.get("poi_domination_changes_total", 0))
        ]
    )
    lines.append(
        "POI influence: active=%d on=%d off=%d regen_ticks=%d xp_ticks=%d"
        % [
            int(snapshot.get("poi_influence_active_count", 0)),
            int(snapshot.get("poi_influence_activation_events_total", 0)),
            int(snapshot.get("poi_influence_deactivation_events_total", 0)),
            int(snapshot.get("poi_influence_regen_ticks_total", 0)),
            int(snapshot.get("poi_influence_xp_grants_total", 0))
        ]
    )
    lines.append("")
    lines.append(
        "States: wander=%d poi=%d detect=%d chase=%d attack=%d cast=%d control=%d nova=%d reposition=%d flee=%d"
        % [
            int(state_counts.get("wander", 0)),
            int(state_counts.get("poi", 0)),
            int(state_counts.get("detect", 0)),
            int(state_counts.get("chase", 0)),
            int(state_counts.get("attack", 0)),
            int(state_counts.get("cast", 0)),
            int(state_counts.get("cast_control", 0)),
            int(state_counts.get("cast_nova", 0)),
            int(state_counts.get("reposition", 0)),
            int(state_counts.get("flee", 0))
        ]
    )
    lines.append("")
    lines.append(_format_poi_population(poi_population, poi_snapshot))
    lines.append("")
    lines.append("Recent events:")

    if events.is_empty():
        lines.append("- (none)")
    else:
        for item in events:
            lines.append("- %s" % item)

    _text.text = "\n".join(lines)


func _format_poi_population(poi_population: Dictionary, poi_snapshot: Dictionary) -> String:
    if poi_population.is_empty():
        return "POI: none"

    var chunks: Array[String] = []
    for poi_name in poi_population.keys():
        var counts: Dictionary = poi_population.get(poi_name, {})
        var details: Dictionary = poi_snapshot.get(poi_name, {})
        var status: String = _status_label(str(details.get("status", "calm")))
        var activity: String = _activity_label(str(details.get("activity", "low")))
        var influence: String = _influence_label(
            bool(details.get("influence_active", false)),
            str(details.get("dominant_faction", "")),
            str(details.get("influence_kind", ""))
        )
        var dominance_seconds: int = int(round(float(details.get("dominance_seconds", 0.0))))
        chunks.append(
            "%s[%s | %s | %s | dom:%ss] H:%d M:%d"
            % [
                poi_name,
                status,
                activity,
                influence,
                dominance_seconds,
                int(counts.get("human", 0)),
                int(counts.get("monster", 0))
            ]
        )

    chunks.sort()
    return "POI occupancy: %s" % " | ".join(chunks)


func _status_label(status: String) -> String:
    match status:
        "contested":
            return "conteste"
        "human_dominant":
            return "domine_humains"
        "monster_dominant":
            return "domine_monstres"
        _:
            return "calme"


func _activity_label(activity: String) -> String:
    match activity:
        "high":
            return "actif+"
        "medium":
            return "actif"
        _:
            return "leger"


func _influence_label(active: bool, faction: String, influence_kind: String) -> String:
    if not active:
        return "influence:off"
    return "influence:on(%s,%s)" % [faction, influence_kind]
