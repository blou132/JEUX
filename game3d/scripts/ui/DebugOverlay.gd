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
    var relic_active_labels: Array = snapshot.get("relic_active_labels", [])
    var top_renown_labels: Array = snapshot.get("top_renown_labels", [])
    var top_notoriety_labels: Array = snapshot.get("top_notoriety_labels", [])
    var allegiance_member_counts: Dictionary = snapshot.get("allegiance_member_counts", {})
    var allegiance_structure_labels: Array = snapshot.get("allegiance_structure_labels", [])
    var allegiance_doctrine_labels: Array = snapshot.get("allegiance_doctrine_labels", [])
    var allegiance_doctrine_counts: Dictionary = snapshot.get("allegiance_doctrine_counts", {})
    var allegiance_project_labels: Array = snapshot.get("allegiance_project_labels", [])
    var allegiance_project_counts: Dictionary = snapshot.get("allegiance_project_counts", {})
    var allegiance_vendetta_labels: Array = snapshot.get("allegiance_vendetta_labels", [])
    var lines: Array[String] = []
    var world_event_name: String = str(snapshot.get("world_event_active_name", "None"))
    var world_event_id: String = str(snapshot.get("world_event_active_id", ""))
    var world_event_remaining: float = float(snapshot.get("world_event_remaining", 0.0))
    var world_event_next_in: float = float(snapshot.get("world_event_next_in", 0.0))
    var neutral_gate_poi: String = str(snapshot.get("neutral_gate_poi", "rift_gate"))
    var neutral_gate_status: String = str(snapshot.get("neutral_gate_status", "dormant"))
    var neutral_gate_active: bool = bool(snapshot.get("neutral_gate_active", false))
    var neutral_gate_remaining: float = float(snapshot.get("neutral_gate_remaining", 0.0))
    var neutral_gate_cooldown: float = float(snapshot.get("neutral_gate_cooldown", 0.0))

    lines.append("SANDBOX FANTASY 3D MVP")
    lines.append("Tick %d | Time %.1fs" % [int(snapshot.get("tick", 0)), float(snapshot.get("time", 0.0))])
    if world_event_id != "":
        lines.append(
            "World Event: %s (%.1fs left) | starts=%d ends=%d"
            % [
                world_event_name,
                world_event_remaining,
                int(snapshot.get("world_event_started_total", 0)),
                int(snapshot.get("world_event_ended_total", 0))
            ]
        )
    else:
        lines.append(
            "World Event: None (next in %.1fs) | starts=%d ends=%d"
            % [
                world_event_next_in,
                int(snapshot.get("world_event_started_total", 0)),
                int(snapshot.get("world_event_ended_total", 0))
            ]
        )
    if neutral_gate_active:
        lines.append(
            "Neutral Gate: OPEN at %s (%.1fs left) | opens=%d closes=%d breaches=%d"
            % [
                neutral_gate_poi if neutral_gate_poi != "" else "rift_gate",
                neutral_gate_remaining,
                int(snapshot.get("neutral_gate_opened_total", 0)),
                int(snapshot.get("neutral_gate_closed_total", 0)),
                int(snapshot.get("neutral_gate_breach_total", 0))
            ]
        )
    else:
        lines.append(
            "Neutral Gate: %s at %s (cooldown %.1fs) | opens=%d closes=%d breaches=%d"
            % [
                neutral_gate_status if neutral_gate_status != "" else "dormant",
                neutral_gate_poi if neutral_gate_poi != "" else "rift_gate",
                neutral_gate_cooldown,
                int(snapshot.get("neutral_gate_opened_total", 0)),
                int(snapshot.get("neutral_gate_closed_total", 0)),
                int(snapshot.get("neutral_gate_breach_total", 0))
            ]
        )
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
        "Renown: avg=%.1f | notable=%d (H:%d M:%d) | rising=%d"
        % [
            float(snapshot.get("avg_renown", 0.0)),
            int(snapshot.get("renown_figures_total", 0)),
            int(snapshot.get("renown_figures_humans", 0)),
            int(snapshot.get("renown_figures_monsters", 0)),
            int(snapshot.get("renown_rising_events_total", 0))
        ]
    )
    lines.append(
        "Top renown figures: %s"
        % (" | ".join(top_renown_labels) if not top_renown_labels.is_empty() else "(none)")
    )
    lines.append(
        "Notoriety: avg=%.1f | notable=%d (H:%d M:%d) | rising=%d"
        % [
            float(snapshot.get("avg_notoriety", 0.0)),
            int(snapshot.get("notoriety_figures_total", 0)),
            int(snapshot.get("notoriety_figures_humans", 0)),
            int(snapshot.get("notoriety_figures_monsters", 0)),
            int(snapshot.get("notoriety_rising_events_total", 0))
        ]
    )
    lines.append(
        "Top notoriety figures: %s"
        % (" | ".join(top_notoriety_labels) if not top_notoriety_labels.is_empty() else "(none)")
    )
    lines.append(
        "Special arrivals: active=%d (H:%d M:%d) | total=%d (H:%d M:%d) | fallen=%d"
        % [
            int(snapshot.get("special_arrivals_active_total", 0)),
            int(snapshot.get("special_arrivals_active_humans", 0)),
            int(snapshot.get("special_arrivals_active_monsters", 0)),
            int(snapshot.get("special_arrivals_total", 0)),
            int(snapshot.get("special_arrivals_human_total", 0)),
            int(snapshot.get("special_arrivals_monster_total", 0)),
            int(snapshot.get("special_arrivals_fallen_total", 0))
        ]
    )
    lines.append(
        "Relics: active=%d (H:%d M:%d) | appear=%d acquired=%d lost=%d"
        % [
            int(snapshot.get("relic_active_total", 0)),
            int(snapshot.get("relic_active_humans", 0)),
            int(snapshot.get("relic_active_monsters", 0)),
            int(snapshot.get("relic_appear_total", 0)),
            int(snapshot.get("relic_acquired_total", 0)),
            int(snapshot.get("relic_lost_total", 0))
        ]
    )
    lines.append(
        "Relic carriers: %s"
        % (" | ".join(relic_active_labels) if not relic_active_labels.is_empty() else "(none)")
    )
    if bool(snapshot.get("bounty_active", false)):
        lines.append(
            "Bounty: ACTIVE target=%s source=%s/%s (%.1fs left) | marked=%d (H:%d M:%d)"
            % [
                str(snapshot.get("bounty_target_label", "unknown")),
                str(snapshot.get("bounty_source_faction", "-")),
                str(snapshot.get("bounty_source_poi", "-")),
                float(snapshot.get("bounty_remaining", 0.0)),
                int(snapshot.get("bounty_marked_total", 0)),
                int(snapshot.get("bounty_marked_humans", 0)),
                int(snapshot.get("bounty_marked_monsters", 0))
            ]
        )
    else:
        lines.append(
            "Bounty: inactive | marked=%d (H:%d M:%d)"
            % [
                int(snapshot.get("bounty_marked_total", 0)),
                int(snapshot.get("bounty_marked_humans", 0)),
                int(snapshot.get("bounty_marked_monsters", 0))
            ]
        )
    lines.append(
        "Bounty events: starts=%d cleared=%d expired=%d"
        % [
            int(snapshot.get("bounty_started_total", 0)),
            int(snapshot.get("bounty_cleared_total", 0)),
            int(snapshot.get("bounty_expired_total", 0))
        ]
    )
    lines.append(
        "Allegiances: active=%d | affiliated=%d (H:%d M:%d) | unassigned=%d"
        % [
            int(snapshot.get("allegiance_active_count", 0)),
            int(snapshot.get("allegiance_affiliated_total", 0)),
            int(snapshot.get("allegiance_affiliated_humans", 0)),
            int(snapshot.get("allegiance_affiliated_monsters", 0)),
            int(snapshot.get("allegiance_unaffiliated_total", 0))
        ]
    )
    lines.append(
        "Allegiance events: up=%d down=%d assign=%d lost=%d"
        % [
            int(snapshot.get("allegiance_created_total", 0)),
            int(snapshot.get("allegiance_removed_total", 0)),
            int(snapshot.get("allegiance_assignments_total", 0)),
            int(snapshot.get("allegiance_losses_total", 0))
        ]
    )
    lines.append(
        "Doctrines: warlike=%d steadfast=%d arcane=%d | assigned=%d"
        % [
            int(allegiance_doctrine_counts.get("warlike", 0)),
            int(allegiance_doctrine_counts.get("steadfast", 0)),
            int(allegiance_doctrine_counts.get("arcane", 0)),
            int(snapshot.get("doctrine_assigned_total", 0))
        ]
    )
    lines.append(
        "Doctrine map: %s"
        % (" | ".join(allegiance_doctrine_labels) if not allegiance_doctrine_labels.is_empty() else "(none)")
    )
    lines.append(
        "Projects: active=%d fortify=%d warband_muster=%d ritual_focus=%d | start=%d end=%d interrupted=%d"
        % [
            int(snapshot.get("allegiance_project_active_count", 0)),
            int(allegiance_project_counts.get("fortify", 0)),
            int(allegiance_project_counts.get("warband_muster", 0)),
            int(allegiance_project_counts.get("ritual_focus", 0)),
            int(snapshot.get("project_started_total", 0)),
            int(snapshot.get("project_ended_total", 0)),
            int(snapshot.get("project_interrupted_total", 0))
        ]
    )
    lines.append(
        "Project map: %s"
        % (" | ".join(allegiance_project_labels) if not allegiance_project_labels.is_empty() else "(none)")
    )
    lines.append(
        "Vendettas: active=%d | start=%d end=%d resolved=%d expired=%d"
        % [
            int(snapshot.get("allegiance_vendetta_active_count", 0)),
            int(snapshot.get("vendetta_started_total", 0)),
            int(snapshot.get("vendetta_ended_total", 0)),
            int(snapshot.get("vendetta_resolved_total", 0)),
            int(snapshot.get("vendetta_expired_total", 0))
        ]
    )
    lines.append(
        "Vendetta map: %s"
        % (" | ".join(allegiance_vendetta_labels) if not allegiance_vendetta_labels.is_empty() else "(none)")
    )
    lines.append(
        "Allegiance cores: %s"
        % (" | ".join(allegiance_structure_labels) if not allegiance_structure_labels.is_empty() else "(none)")
    )
    lines.append("Allegiance members: %s" % _format_allegiance_members(allegiance_member_counts))
    lines.append(
        "Rally: leaders=%d (H:%d M:%d) | followers=%d (H:%d M:%d) | bonus_near_leader=%d"
        % [
            int(snapshot.get("rally_leaders_active", 0)),
            int(snapshot.get("rally_human_leaders_active", 0)),
            int(snapshot.get("rally_monster_leaders_active", 0)),
            int(snapshot.get("rally_followers_active", 0)),
            int(snapshot.get("rally_human_followers_active", 0)),
            int(snapshot.get("rally_monster_followers_active", 0)),
            int(snapshot.get("rally_bonus_followers_active", 0))
        ]
    )
    lines.append(
        "Rally events: formed=%d dissolved=%d | follow_ticks=%d | bonus_ticks=%d"
        % [
            int(snapshot.get("rally_groups_formed_total", 0)),
            int(snapshot.get("rally_groups_dissolved_total", 0)),
            int(snapshot.get("rally_follow_ticks_total", 0)),
            int(snapshot.get("rally_bonus_ticks_total", 0))
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
    lines.append(
        "POI structures: active=%d up=%d down=%d regen_bonus_ticks=%d"
        % [
            int(snapshot.get("poi_structure_active_count", 0)),
            int(snapshot.get("poi_structure_established_total", 0)),
            int(snapshot.get("poi_structure_lost_total", 0)),
            int(snapshot.get("poi_structure_regen_bonus_ticks_total", 0))
        ]
    )
    lines.append(
        "Raid: active=%s attacker=%s source=%s target=%s | starts=%d ends=%d success=%d interrupted=%d timeout=%d"
        % [
            "yes" if bool(snapshot.get("raid_active", false)) else "no",
            str(snapshot.get("raid_attacker_faction", "-")),
            str(snapshot.get("raid_source_poi", "-")),
            str(snapshot.get("raid_target_poi", "-")),
            int(snapshot.get("raid_started_total", 0)),
            int(snapshot.get("raid_ended_total", 0)),
            int(snapshot.get("raid_success_total", 0)),
            int(snapshot.get("raid_interrupted_total", 0)),
            int(snapshot.get("raid_timeout_total", 0))
        ]
    )
    lines.append("")
    lines.append(
        "States: wander=%d poi=%d raid=%d hunt=%d rally=%d detect=%d chase=%d attack=%d cast=%d control=%d nova=%d reposition=%d flee=%d"
        % [
            int(state_counts.get("wander", 0)),
            int(state_counts.get("poi", 0)),
            int(state_counts.get("raid", 0)),
            int(state_counts.get("hunt", 0)),
            int(state_counts.get("rally", 0)),
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
        var structure: String = _structure_label(
            bool(details.get("structure_active", false)),
            str(details.get("structure_state", ""))
        )
        var raid_role: String = _raid_role_label(str(details.get("raid_role", "none")))
        var gate: String = _gate_label(
            bool(details.get("gate_active", false)),
            str(details.get("gate_status", "")),
            float(details.get("gate_remaining", 0.0)),
            float(details.get("gate_cooldown", 0.0))
        )
        var allegiance: String = _allegiance_label(
            str(details.get("allegiance_id", "")),
            str(details.get("allegiance_doctrine", "")),
            str(details.get("allegiance_project", "")),
            float(details.get("allegiance_project_remaining", 0.0)),
            str(details.get("allegiance_vendetta_target", "")),
            float(details.get("allegiance_vendetta_remaining", 0.0))
        )
        var dominance_seconds: int = int(round(float(details.get("dominance_seconds", 0.0))))
        var structure_seconds: int = int(round(float(details.get("structure_seconds", 0.0))))
        chunks.append(
            "%s[%s | %s | %s | %s | %s | %s | %s | dom:%ss | struct:%ss] H:%d M:%d"
            % [
                poi_name,
                status,
                activity,
                influence,
                structure,
                raid_role,
                gate,
                allegiance,
                dominance_seconds,
                structure_seconds,
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


func _structure_label(active: bool, structure_state: String) -> String:
    if not active or structure_state == "":
        return "structure:off"
    if structure_state == "human_outpost":
        return "structure:outpost"
    if structure_state == "monster_lair":
        return "structure:lair"
    return "structure:%s" % structure_state


func _raid_role_label(raid_role: String) -> String:
    if raid_role == "source":
        return "raid:source"
    if raid_role == "target":
        return "raid:target"
    return "raid:none"


func _gate_label(active: bool, gate_status: String, remaining: float, cooldown: float) -> String:
    if active:
        return "gate:open(%.0fs)" % remaining
    if gate_status == "":
        return "gate:none"
    return "gate:%s(%.0fs)" % [gate_status, cooldown]


func _allegiance_label(
    allegiance_id: String,
    doctrine: String = "",
    project_id: String = "",
    project_remaining: float = 0.0,
    vendetta_target: String = "",
    vendetta_remaining: float = 0.0
) -> String:
    if allegiance_id == "":
        return "allegiance:none"
    var tags: Array[String] = []
    if doctrine != "":
        tags.append(doctrine)
    if project_id != "":
        tags.append("%s@%.0fs" % [project_id, project_remaining])
    if vendetta_target != "":
        tags.append("vs:%s@%.0fs" % [vendetta_target, vendetta_remaining])
    if not tags.is_empty():
        return "allegiance:%s[%s]" % [allegiance_id, "|".join(tags)]
    return "allegiance:%s" % allegiance_id


func _format_allegiance_members(member_counts: Dictionary) -> String:
    if member_counts.is_empty():
        return "(none)"
    var parts: Array[String] = []
    for allegiance_id in member_counts.keys():
        parts.append("%s=%d" % [str(allegiance_id), int(member_counts.get(allegiance_id, 0))])
    parts.sort()
    return " | ".join(parts)
