extends CanvasLayer
class_name DebugOverlay

const OVERLAY_MODE_PLAYER: String = "player"
const OVERLAY_MODE_DEBUG: String = "debug"
const OVERLAY_MODE_OFF: String = "off"

var _text: RichTextLabel
var _overlay_mode: String = OVERLAY_MODE_DEBUG
var _help_panel_visible: bool = false
var _debug_compact_mode: bool = false


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
    set_overlay_mode(_overlay_mode)


func set_overlay_mode(mode: String) -> void:
    var normalized: String = mode.strip_edges().to_lower()
    if not (normalized in [OVERLAY_MODE_PLAYER, OVERLAY_MODE_DEBUG, OVERLAY_MODE_OFF]):
        return
    _overlay_mode = normalized
    visible = _overlay_mode != OVERLAY_MODE_OFF
    if _overlay_mode == OVERLAY_MODE_OFF and _text != null:
        _text.text = ""


func get_overlay_mode() -> String:
    return _overlay_mode


func toggle_debug_compact_mode() -> void:
    _debug_compact_mode = not _debug_compact_mode


func get_debug_compact_mode() -> bool:
    return _debug_compact_mode


func cycle_overlay_mode() -> void:
    if _overlay_mode == OVERLAY_MODE_PLAYER:
        set_overlay_mode(OVERLAY_MODE_DEBUG)
        return
    if _overlay_mode == OVERLAY_MODE_DEBUG:
        set_overlay_mode(OVERLAY_MODE_OFF)
        return
    set_overlay_mode(OVERLAY_MODE_PLAYER)


func _toggle_overlay_player_debug_mode() -> void:
    if _overlay_mode == OVERLAY_MODE_DEBUG:
        set_overlay_mode(OVERLAY_MODE_PLAYER)
        return
    set_overlay_mode(OVERLAY_MODE_DEBUG)


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventKey:
        var key_event := event as InputEventKey
        if key_event.pressed and not key_event.echo:
            if key_event.keycode == KEY_F1 or key_event.keycode == KEY_TAB:
                _toggle_overlay_player_debug_mode()
                get_viewport().set_input_as_handled()
            elif key_event.keycode == KEY_H or key_event.keycode == KEY_F2:
                toggle_help_panel()
                get_viewport().set_input_as_handled()
            elif key_event.keycode == KEY_F3 and _overlay_mode == OVERLAY_MODE_DEBUG:
                toggle_debug_compact_mode()
                get_viewport().set_input_as_handled()


func toggle_help_panel() -> void:
    _help_panel_visible = not _help_panel_visible


func update_overlay(snapshot: Dictionary, events: Array[String]) -> void:
    if _overlay_mode == OVERLAY_MODE_OFF:
        visible = false
        _text.text = ""
        return

    visible = true
    if _overlay_mode == OVERLAY_MODE_PLAYER:
        _text.text = "\n".join(_build_player_overlay_lines(snapshot))
        return
    if _debug_compact_mode:
        _text.text = "\n".join(_build_debug_compact_overlay_lines(snapshot))
        return

    var state_counts: Dictionary = snapshot.get("state_counts", {})
    var poi_population: Dictionary = snapshot.get("poi_population", {})
    var poi_snapshot: Dictionary = snapshot.get("poi_snapshot", {})
    var role_counts: Dictionary = snapshot.get("human_role_counts", {})
    var level_counts: Dictionary = snapshot.get("level_counts", {})
    var human_level_counts: Dictionary = snapshot.get("human_level_counts", {})
    var monster_level_counts: Dictionary = snapshot.get("monster_level_counts", {})
    var relic_active_labels: Array = snapshot.get("relic_active_labels", [])
    var destiny_active_labels: Array = snapshot.get("destiny_active_labels", [])
    var convergence_active_labels: Array = snapshot.get("convergence_active_labels", [])
    var marked_zone_active_labels: Array = snapshot.get("marked_zone_active_labels", [])
    var rivalry_active_labels: Array = snapshot.get("rivalry_active_labels", [])
    var bond_active_labels: Array = snapshot.get("bond_active_labels", [])
    var splinter_active_labels: Array = snapshot.get("splinter_active_labels", [])
    var top_renown_labels: Array = snapshot.get("top_renown_labels", [])
    var top_notoriety_labels: Array = snapshot.get("top_notoriety_labels", [])
    var allegiance_member_counts: Dictionary = snapshot.get("allegiance_member_counts", {})
    var allegiance_structure_labels: Array = snapshot.get("allegiance_structure_labels", [])
    var allegiance_doctrine_labels: Array = snapshot.get("allegiance_doctrine_labels", [])
    var allegiance_doctrine_counts: Dictionary = snapshot.get("allegiance_doctrine_counts", {})
    var allegiance_doctrine_snapshot_labels: Array = snapshot.get(
        "allegiance_doctrine_snapshot_labels",
        allegiance_doctrine_labels
    )
    var allegiance_doctrine_source_counts: Dictionary = snapshot.get("allegiance_doctrine_source_counts", {})
    var allegiance_doctrine_average_biases: Dictionary = snapshot.get("allegiance_doctrine_average_biases", {})
    var doctrine_project_bias_counts: Dictionary = snapshot.get("doctrine_project_bias_counts", {})
    var doctrine_vendetta_bias_avg: float = float(snapshot.get("doctrine_vendetta_bias_avg", 0.0))
    var narrative_timeline_labels: Array = snapshot.get("narrative_timeline_labels", [])
    var narrative_timeline_count: int = int(snapshot.get("narrative_timeline_count", 0))
    var last_major_event_label: String = str(snapshot.get("last_major_event_label", "(none)"))
    var run_summary_title: String = str(snapshot.get("run_summary_title", "Run Summary"))
    var run_summary_lines: Array = snapshot.get("run_summary_lines", [])
    var run_status: String = str(snapshot.get("run_status", "running"))
    var run_result_visible: bool = bool(snapshot.get("run_result_visible", false))
    var run_metrics_export_label: String = str(snapshot.get("run_metrics_export_label", "not exported")).strip_edges()
    var allegiance_doctrine_fallback_labels: Array = snapshot.get("allegiance_doctrine_fallback_labels", [])
    var allegiance_doctrine_fallback_used_count: int = int(
        snapshot.get("allegiance_doctrine_fallback_used_count", 0)
    )
    var allegiance_doctrine_dominant_id: String = str(snapshot.get("allegiance_doctrine_dominant_id", ""))
    var allegiance_doctrine_dominant_count: int = int(snapshot.get("allegiance_doctrine_dominant_count", 0))
    var doctrine_templates_source: String = str(snapshot.get("doctrine_templates_source", "fallback"))
    var allegiance_project_labels: Array = snapshot.get("allegiance_project_labels", [])
    var allegiance_project_counts: Dictionary = snapshot.get("allegiance_project_counts", {})
    var allegiance_vendetta_labels: Array = snapshot.get("allegiance_vendetta_labels", [])
    var allegiance_crisis_labels: Array = snapshot.get("allegiance_crisis_labels", [])
    var allegiance_recovery_labels: Array = snapshot.get("allegiance_recovery_labels", [])
    var mending_active_labels: Array = snapshot.get("mending_active_labels", [])
    var oath_active_labels: Array = snapshot.get("oath_active_labels", [])
    var echo_active_labels: Array = snapshot.get("echo_active_labels", [])
    var expedition_active_labels: Array = snapshot.get("expedition_active_labels", [])
    var alert_active_labels: Array = snapshot.get("alert_active_labels", [])
    var sanctuary_bastion_active_labels: Array = snapshot.get("sanctuary_bastion_active_labels", [])
    var taboo_active_labels: Array = snapshot.get("taboo_active_labels", [])
    var legacy_successor_labels: Array = snapshot.get("legacy_successor_labels", [])
    var memorial_scar_labels: Array = snapshot.get("memorial_scar_labels", [])
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
    var support_gate_visual_state: String = str(snapshot.get("support_gate_visual_state", "inactive")).strip_edges()
    var support_gate_visual_label: String = str(
        snapshot.get("support_gate_visual_label", support_gate_visual_state)
    ).strip_edges()
    var support_gate_run_attempts: int = int(snapshot.get("support_gate_run_attempts", 0))
    var support_gate_run_success: int = int(snapshot.get("support_gate_run_success", 0))
    var support_gate_run_success_rate: int = int(
        round(clampf(float(snapshot.get("support_gate_run_success_rate", 0.0)), 0.0, 1.0) * 100.0)
    )
    var support_gate_run_available_ratio: int = int(
        round(clampf(float(snapshot.get("support_gate_run_available_ratio", 0.0)), 0.0, 1.0) * 100.0)
    )
    var support_gate_tuning_label: String = str(
        snapshot.get(
            "support_gate_tuning_label",
            "attempts=0 success=0 rate=0% available=0% blocked=0(cooldown=0 unavailable=0)"
        )
    ).strip_edges()
    var gate_response_human_label: String = str(snapshot.get("gate_response_human_label", "none"))
    var gate_response_monster_label: String = str(snapshot.get("gate_response_monster_label", "none"))

    lines.append("SANDBOX FANTASY 3D MVP")
    lines.append("Tick %d | Time %.1fs" % [int(snapshot.get("tick", 0)), float(snapshot.get("time", 0.0))])
    for help_line in _build_controls_help_lines(_overlay_mode, run_status, run_result_visible, false):
        lines.append(help_line)
    if _help_panel_visible:
        for panel_line in _build_help_panel_lines(snapshot):
            lines.append(panel_line)
    lines.append("")
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
    lines.append(
        "Gate Responses: H=%s M=%s | starts=%d ends=%d success=%d interrupted=%d"
        % [
            gate_response_human_label,
            gate_response_monster_label,
            int(snapshot.get("gate_response_started_total", 0)),
            int(snapshot.get("gate_response_ended_total", 0)),
            int(snapshot.get("gate_response_success_total", 0)),
            int(snapshot.get("gate_response_interrupted_total", 0))
        ]
    )
    lines.append(
        "Support gate visual: %s (%s)"
        % [
            support_gate_visual_state if support_gate_visual_state != "" else "inactive",
            support_gate_visual_label if support_gate_visual_label != "" else "inactive"
        ]
    )
    lines.append(
        "Support gate tuning: run attempts=%d success=%d rate=%d%% available=%d%%"
        % [
            support_gate_run_attempts,
            support_gate_run_success,
            support_gate_run_success_rate,
            support_gate_run_available_ratio
        ]
    )
    lines.append(
        "Support gate tuning session: %s"
        % [
            support_gate_tuning_label
            if support_gate_tuning_label != ""
            else "attempts=0 success=0 rate=0% available=0% blocked=0(cooldown=0 unavailable=0)"
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
        "Legacy: active=%d triggered=%d chosen=%d relic_inherited=%d faded=%d cooldown=%.1fs"
        % [
            int(snapshot.get("legacy_successor_active_count", 0)),
            int(snapshot.get("legacy_triggered_total", 0)),
            int(snapshot.get("legacy_successor_chosen_total", 0)),
            int(snapshot.get("legacy_relic_inherited_total", 0)),
            int(snapshot.get("legacy_faded_total", 0)),
            float(snapshot.get("legacy_cooldown_left", 0.0))
        ]
    )
    lines.append(
        "Legacy successors: %s"
        % (" | ".join(legacy_successor_labels) if not legacy_successor_labels.is_empty() else "(none)")
    )
    lines.append(
        "Memorial/Scar: active=%d memorial=%d scar=%d | born=%d faded=%d"
        % [
            int(snapshot.get("memorial_scar_active_total", 0)),
            int(snapshot.get("memorial_site_active_count", 0)),
            int(snapshot.get("scar_site_active_count", 0)),
            int(snapshot.get("memorial_scar_born_total", 0)),
            int(snapshot.get("memorial_scar_faded_total", 0))
        ]
    )
    lines.append(
        "Memorial/Scar sites: %s"
        % (" | ".join(memorial_scar_labels) if not memorial_scar_labels.is_empty() else "(none)")
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
        "Destiny: active=%d | start=%d end=%d fulfilled=%d interrupted=%d"
        % [
            int(snapshot.get("destiny_active_total", 0)),
            int(snapshot.get("destiny_started_total", 0)),
            int(snapshot.get("destiny_ended_total", 0)),
            int(snapshot.get("destiny_fulfilled_total", 0)),
            int(snapshot.get("destiny_interrupted_total", 0))
        ]
    )
    lines.append(
        "Destiny pulls: %s"
        % (" | ".join(destiny_active_labels) if not destiny_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Convergence: active=%d | start=%d end=%d interrupted=%d"
        % [
            int(snapshot.get("convergence_active_total", 0)),
            int(snapshot.get("convergence_started_total", 0)),
            int(snapshot.get("convergence_ended_total", 0)),
            int(snapshot.get("convergence_interrupted_total", 0))
        ]
    )
    lines.append(
        "Convergence zones: %s"
        % (" | ".join(convergence_active_labels) if not convergence_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Marked zones: active=%d (S:%d C:%d) | start=%d fade=%d"
        % [
            int(snapshot.get("marked_zone_active_total", 0)),
            int(snapshot.get("marked_zone_sanctified_active_total", 0)),
            int(snapshot.get("marked_zone_corrupted_active_total", 0)),
            int(snapshot.get("marked_zone_started_total", 0)),
            int(snapshot.get("marked_zone_faded_total", 0))
        ]
    )
    lines.append(
        "Marked zone labels: %s"
        % (" | ".join(marked_zone_active_labels) if not marked_zone_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Rivalries: active=%d duel=%d | start=%d end=%d resolved=%d expired=%d"
        % [
            int(snapshot.get("rivalry_active_total", 0)),
            int(snapshot.get("duel_active_total", 0)),
            int(snapshot.get("rivalry_started_total", 0)),
            int(snapshot.get("rivalry_ended_total", 0)),
            int(snapshot.get("rivalry_resolved_total", 0)),
            int(snapshot.get("rivalry_expired_total", 0))
        ]
    )
    lines.append(
        "Rival pairs: %s"
        % (" | ".join(rivalry_active_labels) if not rivalry_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Bonds: active=%d | start=%d end=%d broken=%d"
        % [
            int(snapshot.get("bond_active_total", 0)),
            int(snapshot.get("bond_started_total", 0)),
            int(snapshot.get("bond_ended_total", 0)),
            int(snapshot.get("bond_broken_total", 0))
        ]
    )
    lines.append(
        "Bond links: %s"
        % (" | ".join(bond_active_labels) if not bond_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Splinters: active=%d | start=%d end=%d resolved=%d faded=%d"
        % [
            int(snapshot.get("splinter_active_total", 0)),
            int(snapshot.get("splinter_started_total", 0)),
            int(snapshot.get("splinter_ended_total", 0)),
            int(snapshot.get("splinter_resolved_total", 0)),
            int(snapshot.get("splinter_faded_total", 0))
        ]
    )
    lines.append(
        "Splinter groups: %s"
        % (" | ".join(splinter_active_labels) if not splinter_active_labels.is_empty() else "(none)")
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
        "Doctrines: warlike=%d steadfast=%d arcane=%d fallback=%d"
        % [
            int(allegiance_doctrine_counts.get("warlike", 0)),
            int(allegiance_doctrine_counts.get("steadfast", 0)),
            int(allegiance_doctrine_counts.get("arcane", 0)),
            allegiance_doctrine_fallback_used_count
        ]
    )
    var dominant_label: String = "(none)"
    if allegiance_doctrine_dominant_id != "":
        dominant_label = "%s(%d)" % [allegiance_doctrine_dominant_id, allegiance_doctrine_dominant_count]
    lines.append(
        "Doctrine dominant: %s | source json=%d fallback=%d | load=%s"
        % [
            dominant_label,
            int(allegiance_doctrine_source_counts.get("json", 0)),
            int(allegiance_doctrine_source_counts.get("fallback", 0)),
            doctrine_templates_source
        ]
    )
    lines.append(
        "Doctrine bias avg: raid=%.2f defense=%.2f rally=%.2f magic=%.2f"
        % [
            float(allegiance_doctrine_average_biases.get("raid_bias", 0.0)),
            float(allegiance_doctrine_average_biases.get("defense_bias", 0.0)),
            float(allegiance_doctrine_average_biases.get("rally_bias", 0.0)),
            float(allegiance_doctrine_average_biases.get("magic_bias", 0.0))
        ]
    )
    lines.append(
        "Doctrine effects: project_bias=fortify:%d warband:%d ritual:%d vendetta_avg=%.2f"
        % [
            int(doctrine_project_bias_counts.get("fortify", 0)),
            int(doctrine_project_bias_counts.get("warband_muster", 0)),
            int(doctrine_project_bias_counts.get("ritual_focus", 0)),
            doctrine_vendetta_bias_avg
        ]
    )
    lines.append(
        "Doctrine map: %s"
        % (
            " | ".join(allegiance_doctrine_snapshot_labels)
            if not allegiance_doctrine_snapshot_labels.is_empty()
            else "(none)"
        )
    )
    lines.append(
        "Doctrine fallback map: %s"
        % (
            " | ".join(allegiance_doctrine_fallback_labels)
            if not allegiance_doctrine_fallback_labels.is_empty()
            else "(none)"
        )
    )
    lines.append(
        "Run status: %s | result_visible=%s"
        % [run_status, "yes" if run_result_visible else "no"]
    )
    lines.append(
        "Metrics export: %s"
        % [run_metrics_export_label if run_metrics_export_label != "" else "not exported"]
    )
    if run_result_visible:
        lines.append("--- Run Result Panel ---")
        for panel_line in _build_run_result_panel_lines(snapshot, 4):
            lines.append(panel_line)
        lines.append("--- End Run Result Panel ---")
    for objective_panel_line in _build_objective_panel_lines(snapshot, OVERLAY_MODE_DEBUG):
        lines.append(objective_panel_line)
    var objective_interaction_feedback_debug: String = _build_objective_interaction_feedback_line(snapshot, true)
    if objective_interaction_feedback_debug != "":
        lines.append(objective_interaction_feedback_debug)
    lines.append("%s:" % run_summary_title)
    if run_summary_lines.is_empty():
        lines.append("- (none)")
    else:
        var run_summary_visible_count: int = min(4, run_summary_lines.size())
        for index in range(run_summary_visible_count):
            lines.append("- %s" % str(run_summary_lines[index]))
    lines.append("Timeline: recent=%d | last=%s" % [narrative_timeline_count, last_major_event_label])
    if not narrative_timeline_labels.is_empty():
        var timeline_tail_count: int = min(6, narrative_timeline_labels.size())
        var timeline_start: int = narrative_timeline_labels.size() - timeline_tail_count
        for index in range(narrative_timeline_labels.size() - 1, timeline_start - 1, -1):
            lines.append("  %s" % str(narrative_timeline_labels[index]))
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
        "Crisis: active=%d | start=%d end=%d resolved=%d expired=%d"
        % [
            int(snapshot.get("allegiance_crisis_active_count", 0)),
            int(snapshot.get("crisis_started_total", 0)),
            int(snapshot.get("crisis_ended_total", 0)),
            int(snapshot.get("crisis_resolved_total", 0)),
            int(snapshot.get("crisis_expired_total", 0))
        ]
    )
    lines.append(
        "Crisis map: %s"
        % (" | ".join(allegiance_crisis_labels) if not allegiance_crisis_labels.is_empty() else "(none)")
    )
    lines.append(
        "Recovery: active=%d | start=%d end=%d interrupted=%d"
        % [
            int(snapshot.get("allegiance_recovery_active_count", 0)),
            int(snapshot.get("recovery_started_total", 0)),
            int(snapshot.get("recovery_ended_total", 0)),
            int(snapshot.get("recovery_interrupted_total", 0))
        ]
    )
    lines.append(
        "Recovery map: %s"
        % (" | ".join(allegiance_recovery_labels) if not allegiance_recovery_labels.is_empty() else "(none)")
    )
    lines.append(
        "Mending: active=%d | start=%d end=%d broken=%d"
        % [
            int(snapshot.get("mending_active_count", 0)),
            int(snapshot.get("mending_started_total", 0)),
            int(snapshot.get("mending_ended_total", 0)),
            int(snapshot.get("mending_broken_total", 0))
        ]
    )
    lines.append(
        "Mending arcs: %s"
        % (" | ".join(mending_active_labels) if not mending_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Oaths: active=%d | start=%d end=%d fulfilled=%d broken=%d"
        % [
            int(snapshot.get("oath_active_count", 0)),
            int(snapshot.get("oath_started_total", 0)),
            int(snapshot.get("oath_ended_total", 0)),
            int(snapshot.get("oath_fulfilled_total", 0)),
            int(snapshot.get("oath_broken_total", 0))
        ]
    )
    lines.append(
        "Oath labels: %s"
        % (" | ".join(oath_active_labels) if not oath_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Echoes: active=%d | start=%d end=%d faded=%d"
        % [
            int(snapshot.get("echo_active_count", 0)),
            int(snapshot.get("echo_started_total", 0)),
            int(snapshot.get("echo_ended_total", 0)),
            int(snapshot.get("echo_faded_total", 0))
        ]
    )
    lines.append(
        "Echo labels: %s"
        % (" | ".join(echo_active_labels) if not echo_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Expeditions: active=%d | start=%d arrived=%d end=%d interrupted=%d"
        % [
            int(snapshot.get("expedition_active_count", 0)),
            int(snapshot.get("expedition_started_total", 0)),
            int(snapshot.get("expedition_arrived_total", 0)),
            int(snapshot.get("expedition_ended_total", 0)),
            int(snapshot.get("expedition_interrupted_total", 0))
        ]
    )
    lines.append(
        "Expedition labels: %s"
        % (" | ".join(expedition_active_labels) if not expedition_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Alerts: active=%d | start=%d end=%d"
        % [
            int(snapshot.get("alert_active_count", 0)),
            int(snapshot.get("alert_started_total", 0)),
            int(snapshot.get("alert_ended_total", 0))
        ]
    )
    lines.append(
        "Alert labels: %s"
        % (" | ".join(alert_active_labels) if not alert_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Sanctuaries/Bastions: active=%d (S:%d B:%d) | rise(S:%d B:%d) fade=%d"
        % [
            int(snapshot.get("sanctuary_bastion_active_total", 0)),
            int(snapshot.get("sanctuary_site_active_total", 0)),
            int(snapshot.get("dark_bastion_active_total", 0)),
            int(snapshot.get("sanctuary_risen_total", 0)),
            int(snapshot.get("bastion_risen_total", 0)),
            int(snapshot.get("sanctuary_bastion_faded_total", 0))
        ]
    )
    lines.append(
        "Sanctuary/Bastion labels: %s"
        % (" | ".join(sanctuary_bastion_active_labels) if not sanctuary_bastion_active_labels.is_empty() else "(none)")
    )
    lines.append(
        "Taboos: active=%d (F:%d C:%d) | rise=%d fade=%d"
        % [
            int(snapshot.get("taboo_active_total", 0)),
            int(snapshot.get("forbidden_site_active_total", 0)),
            int(snapshot.get("cursed_warning_active_total", 0)),
            int(snapshot.get("taboo_risen_total", 0)),
            int(snapshot.get("taboo_faded_total", 0))
        ]
    )
    lines.append(
        "Taboo labels: %s"
        % (" | ".join(taboo_active_labels) if not taboo_active_labels.is_empty() else "(none)")
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


func _build_controls_help_lines(
    mode: String,
    run_status: String = "running",
    run_result_visible: bool = false,
    debug_compact_mode: bool = false
) -> Array[String]:
    var normalized_mode: String = mode.strip_edges().to_lower()
    var can_restart: bool = run_status in ["completed", "failed"]
    if normalized_mode == OVERLAY_MODE_OFF:
        return []
    if normalized_mode == OVERLAY_MODE_PLAYER:
        if can_restart:
            if run_result_visible:
                return [
                    "F1/Tab: HUD debug/player | mode=player",
                    "H/F2: help"
                ]
            return [
                "F1/Tab: HUD debug/player | mode=player",
                "O/PageDown: next objective",
                "R: restart run",
                "H/F2: help"
            ]
        return [
            "F1/Tab: HUD debug/player | mode=player",
            "H/F2: help"
        ]

    var lines: Array[String] = [
        "HUD: F1/Tab toggle player-debug | mode=%s" % normalized_mode,
        "Debug HUD is for development.",
        "O/PageDown: next objective (after run end)",
        "F4: export run metrics",
        "H/F2: help panel"
    ]
    lines.append(
        "Debug detail: %s (F3 toggle)"
        % ("debug_compact" if debug_compact_mode else "debug_full")
    )
    if can_restart:
        lines.append("R: restart run")
    else:
        lines.append("R: restart run (after run end)")
    return lines


func _build_help_panel_lines(snapshot: Dictionary) -> Array[String]:
    var run_status: String = str(snapshot.get("run_status", "running"))
    var run_state_label: String = "run terminee" if run_status in ["completed", "failed"] else "run en cours"
    return [
        "==================== HELP ====================",
        "F1/Tab: toggle HUD player/debug",
        "E: support objective (si objectif interactif actif)",
        "R: restart run (si run terminee)",
        "O/PageDown: next objective (si run terminee)",
        "F4: export run metrics (mode debug)",
        "H/F2: afficher/masquer aide",
        "HUD modes: player/debug/off | %s" % run_state_label,
        "================================================"
    ]


func _build_objective_panel_lines(
    snapshot: Dictionary,
    mode: String = OVERLAY_MODE_PLAYER
) -> Array[String]:
    var normalized_mode: String = mode.strip_edges().to_lower()
    if normalized_mode == OVERLAY_MODE_OFF:
        return []

    var objective_active: bool = bool(snapshot.get("objective_active", false))
    var objective_id: String = str(snapshot.get("objective_id", "")).strip_edges()
    var objective_title: String = str(snapshot.get("objective_title", "World objective")).strip_edges()
    var objective_description: String = str(snapshot.get("objective_description", "")).strip_edges()
    var objective_category: String = str(snapshot.get("objective_category", "")).strip_edges()
    var objective_config_label: String = str(snapshot.get("objective_config_label", "")).strip_edges()
    var objective_available_ids: Array = snapshot.get("objective_available_ids", [])
    var objective_selected_index: int = int(snapshot.get("objective_selected_index", -1))
    var objective_available_count: int = int(
        snapshot.get("objective_available_count", objective_available_ids.size())
    )
    var objective_completion_target_label: String = str(
        snapshot.get("objective_completion_target_label", "")
    ).strip_edges()
    var objective_status: String = str(snapshot.get("objective_status", "inactive")).strip_edges()
    var objective_progress_label: String = str(snapshot.get("objective_progress_label", "0%")).strip_edges()
    var objective_elapsed: float = float(snapshot.get("objective_elapsed", 0.0))
    var objective_required: float = float(snapshot.get("objective_required", 0.0))
    var objective_fail_reason: String = str(snapshot.get("objective_fail_reason", "")).strip_edges()
    var objective_dominant_faction: String = str(snapshot.get("objective_dominant_faction", "")).strip_edges()
    var objective_switch_count: int = int(snapshot.get("objective_switch_count", 0))
    var objective_result_label: String = str(snapshot.get("objective_result_label", "")).strip_edges()
    var objective_interaction_count: int = int(snapshot.get("objective_interaction_count", 0))
    var objective_interaction_required: int = int(snapshot.get("objective_interaction_required", 0))
    var objective_interaction_label: String = str(snapshot.get("objective_interaction_label", "")).strip_edges()
    var objective_interaction_available: bool = bool(snapshot.get("objective_interaction_available", false))
    var objective_interaction_cooldown: float = float(snapshot.get("objective_interaction_cooldown", 0.0))
    var objective_has_interaction: bool = objective_interaction_required > 0
    var run_result_visible: bool = bool(snapshot.get("run_result_visible", false))
    var lines: Array[String] = []

    if normalized_mode == OVERLAY_MODE_PLAYER and run_result_visible:
        var reduced_progress: String = objective_progress_label
        if objective_has_interaction:
            reduced_progress = (
                "%d/%d supports"
                % [objective_interaction_count, objective_interaction_required]
            )
        lines.append(
            "Objective Panel: %s | status=%s | progress=%s"
            % [objective_title, objective_status if objective_status != "" else "inactive", reduced_progress]
        )
        return lines

    if normalized_mode == OVERLAY_MODE_PLAYER:
        lines.append("------------ Objective Panel ------------")
        lines.append("Objective: %s" % objective_title)
        if objective_description != "":
            lines.append("Goal: %s" % objective_description)
        if objective_completion_target_label != "":
            lines.append("Target: %s" % objective_completion_target_label)
        lines.append("Progress: %s" % objective_progress_label)
        lines.append("Status: %s" % objective_status)
        if objective_has_interaction and objective_interaction_label != "":
            lines.append("%s" % objective_interaction_label)
            lines.append(
                "Support: %d/%d (%s)"
                % [
                    objective_interaction_count,
                    objective_interaction_required,
                    "ready" if objective_interaction_available else "wait"
                ]
            )
        if objective_status == "failed" and objective_fail_reason != "":
            lines.append("Fail reason: %s" % objective_fail_reason)
        elif objective_result_label != "":
            lines.append("Result: %s" % objective_result_label)

        while lines.size() > 7:
            var removable_index: int = -1
            for index in range(lines.size()):
                var line: String = str(lines[index])
                if line.begins_with("Goal:"):
                    removable_index = index
                    break
                if removable_index == -1 and line.begins_with("Target:"):
                    removable_index = index
            if removable_index == -1:
                lines.remove_at(lines.size() - 1)
            else:
                lines.remove_at(removable_index)
        return lines

    lines.append("------------ Objective Panel ------------")
    lines.append("Objective: %s" % objective_title)
    lines.append(
        "Objective status: %s | active=%s"
        % [objective_status if objective_status != "" else "inactive", "yes" if objective_active else "no"]
    )
    lines.append(
        "Objective id/category: %s / %s"
        % [
            objective_id if objective_id != "" else "(none)",
            objective_category if objective_category != "" else "(none)"
        ]
    )
    lines.append(
        "Objective dominance: faction=%s switches=%d"
        % [
            objective_dominant_faction if objective_dominant_faction != "" else "none",
            objective_switch_count
        ]
    )
    if objective_description != "":
        lines.append("Objective description: %s" % objective_description)
    if objective_completion_target_label != "":
        lines.append("Objective target: %s" % objective_completion_target_label)
    lines.append(
        "Objective progress: %s (%.1fs/%.1fs)"
        % [objective_progress_label, objective_elapsed, objective_required]
    )
    if objective_available_count > 0 and objective_selected_index >= 0:
        lines.append("Objective selection: %d/%d" % [objective_selected_index + 1, objective_available_count])
    if not objective_available_ids.is_empty():
        lines.append("Objective available: %s" % ", ".join(objective_available_ids))
    if objective_config_label != "":
        lines.append("Objective config: %s" % objective_config_label)
    if objective_has_interaction:
        if objective_interaction_label != "":
            lines.append("Objective interaction command: %s" % objective_interaction_label)
        lines.append(
            "Objective interaction: %d/%d available=%s cooldown=%.2fs"
            % [
                objective_interaction_count,
                objective_interaction_required,
                "yes" if objective_interaction_available else "no",
                objective_interaction_cooldown
            ]
        )
    if objective_status == "failed" and objective_fail_reason != "":
        lines.append("Objective fail reason: %s" % objective_fail_reason)
    if objective_result_label != "":
        lines.append("Objective result: %s" % objective_result_label)
    return lines


func _build_objective_interaction_feedback_line(
    snapshot: Dictionary,
    include_details: bool = false
) -> String:
    var feedback_label: String = str(snapshot.get("objective_interaction_feedback_label", "")).strip_edges()
    var feedback_type: String = str(snapshot.get("objective_interaction_feedback_type", "")).strip_edges().to_lower()
    var feedback_timer: float = float(snapshot.get("objective_interaction_feedback_timer", 0.0))
    if feedback_label == "" or feedback_timer <= 0.0:
        return ""
    if include_details:
        var resolved_type: String = feedback_type if feedback_type != "" else "info"
        return (
            "Interaction: type=%s timer=%.1fs label=%s"
            % [resolved_type, feedback_timer, feedback_label]
        )
    return "Interaction: %s" % feedback_label


func _build_run_result_panel_lines(
    snapshot: Dictionary,
    max_result_lines: int = 4
) -> Array[String]:
    var run_result_visible: bool = bool(snapshot.get("run_result_visible", false))
    if not run_result_visible:
        return []

    var run_status: String = str(snapshot.get("run_status", "running"))
    var run_result_title: String = str(snapshot.get("run_result_title", ""))
    var run_result_lines: Array = snapshot.get("run_result_lines", [])
    var lines: Array[String] = ["===================="]
    var panel_title: String = "RUN RESULT"
    if run_status == "completed":
        panel_title = "RUN COMPLETED"
    elif run_status == "failed":
        panel_title = "RUN FAILED"
    elif run_result_title != "":
        panel_title = run_result_title.to_upper()
    lines.append(panel_title)

    if run_result_lines.is_empty():
        lines.append("- (none)")
    else:
        var result_lines_limit: int = max(1, max_result_lines)
        var run_result_visible_count: int = min(result_lines_limit, run_result_lines.size())
        for index in range(run_result_visible_count):
            lines.append("- %s" % str(run_result_lines[index]))

    lines.append("R: restart run | O/PageDown: next objective")
    lines.append("====================")
    return lines


func _build_debug_compact_overlay_lines(snapshot: Dictionary) -> Array[String]:
    var lines: Array[String] = []
    var tick: int = int(snapshot.get("tick", 0))
    var sim_time: float = float(snapshot.get("time", 0.0))
    var run_status: String = str(snapshot.get("run_status", "running"))
    var run_result_visible: bool = bool(snapshot.get("run_result_visible", false))
    var run_metrics_export_label: String = str(snapshot.get("run_metrics_export_label", "not exported")).strip_edges()
    var world_event_id: String = str(snapshot.get("world_event_active_id", ""))
    var world_event_name: String = str(snapshot.get("world_event_active_name", "None"))
    var world_event_remaining: float = float(snapshot.get("world_event_remaining", 0.0))
    var world_event_next_in: float = float(snapshot.get("world_event_next_in", 0.0))
    var neutral_gate_active: bool = bool(snapshot.get("neutral_gate_active", false))
    var neutral_gate_status: String = str(snapshot.get("neutral_gate_status", "dormant"))
    var neutral_gate_poi: String = str(snapshot.get("neutral_gate_poi", "rift_gate"))
    var neutral_gate_remaining: float = float(snapshot.get("neutral_gate_remaining", 0.0))
    var neutral_gate_cooldown: float = float(snapshot.get("neutral_gate_cooldown", 0.0))
    var support_gate_visual_state: String = str(snapshot.get("support_gate_visual_state", "inactive")).strip_edges()
    var support_gate_run_attempts: int = int(snapshot.get("support_gate_run_attempts", 0))
    var support_gate_run_success: int = int(snapshot.get("support_gate_run_success", 0))
    var support_gate_run_success_rate: int = int(
        round(clampf(float(snapshot.get("support_gate_run_success_rate", 0.0)), 0.0, 1.0) * 100.0)
    )
    var support_gate_run_available_ratio: int = int(
        round(clampf(float(snapshot.get("support_gate_run_available_ratio", 0.0)), 0.0, 1.0) * 100.0)
    )
    var run_summary_lines: Array = snapshot.get("run_summary_lines", [])
    var narrative_timeline_labels: Array = snapshot.get("narrative_timeline_labels", [])
    var narrative_timeline_count: int = int(snapshot.get("narrative_timeline_count", 0))
    var last_major_event_label: String = str(snapshot.get("last_major_event_label", "(none)"))
    var doctrine_counts: Dictionary = snapshot.get("allegiance_doctrine_counts", {})
    var doctrine_dominant: String = str(snapshot.get("allegiance_doctrine_dominant_id", ""))
    var project_counts: Dictionary = snapshot.get("allegiance_project_counts", {})
    var vendetta_active_count: int = int(snapshot.get("allegiance_vendetta_active_count", 0))

    lines.append("SANDBOX FANTASY 3D MVP")
    lines.append("Tick %d | Time %.1fs | mode=debug_compact" % [tick, sim_time])
    for help_line in _build_controls_help_lines(
        OVERLAY_MODE_DEBUG,
        run_status,
        run_result_visible,
        true
    ):
        lines.append(help_line)
    if _help_panel_visible:
        for help_panel_line in _build_help_panel_lines(snapshot):
            lines.append(help_panel_line)
    if run_result_visible:
        for run_result_line in _build_run_result_panel_lines(snapshot, 4):
            lines.append(run_result_line)
    for objective_panel_line in _build_objective_panel_lines(snapshot, OVERLAY_MODE_PLAYER):
        lines.append(objective_panel_line)
    var objective_interaction_feedback_debug: String = _build_objective_interaction_feedback_line(snapshot, true)
    if objective_interaction_feedback_debug != "":
        lines.append(objective_interaction_feedback_debug)

    lines.append(
        "Population: alive=%d H:%d M:%d deaths=%d"
        % [
            int(snapshot.get("alive_total", 0)),
            int(snapshot.get("humans_alive", 0)),
            int(snapshot.get("monsters_alive", 0)),
            int(snapshot.get("deaths_total", 0))
        ]
    )
    if world_event_id != "":
        lines.append("World Event: %s (%.1fs)" % [world_event_name, world_event_remaining])
    else:
        lines.append("World Event: none (next %.1fs)" % world_event_next_in)
    if neutral_gate_active:
        lines.append("Neutral Gate: OPEN at %s (%.1fs)" % [neutral_gate_poi, neutral_gate_remaining])
    else:
        lines.append(
            "Neutral Gate: %s at %s (cooldown %.1fs)"
            % [neutral_gate_status, neutral_gate_poi, neutral_gate_cooldown]
        )
    lines.append(
        "Support gate visual: %s"
        % [support_gate_visual_state if support_gate_visual_state != "" else "inactive"]
    )
    lines.append(
        "Support gate tuning: run attempts=%d success=%d rate=%d%% available=%d%%"
        % [
            support_gate_run_attempts,
            support_gate_run_success,
            support_gate_run_success_rate,
            support_gate_run_available_ratio
        ]
    )
    lines.append(
        "Metrics export: %s"
        % [run_metrics_export_label if run_metrics_export_label != "" else "not exported"]
    )

    lines.append(
        "Doctrines: warlike=%d steadfast=%d arcane=%d dominant=%s"
        % [
            int(doctrine_counts.get("warlike", 0)),
            int(doctrine_counts.get("steadfast", 0)),
            int(doctrine_counts.get("arcane", 0)),
            doctrine_dominant if doctrine_dominant != "" else "none"
        ]
    )
    lines.append(
        "Projects/Vendettas: fortify=%d warband=%d ritual=%d vendettas=%d"
        % [
            int(project_counts.get("fortify", 0)),
            int(project_counts.get("warband_muster", 0)),
            int(project_counts.get("ritual_focus", 0)),
            vendetta_active_count
        ]
    )
    lines.append("Run Summary:")
    if run_summary_lines.is_empty():
        lines.append("- (none)")
    else:
        var summary_count: int = min(3, run_summary_lines.size())
        for index in range(summary_count):
            lines.append("- %s" % str(run_summary_lines[index]))
    lines.append("Timeline: recent=%d | last=%s" % [narrative_timeline_count, last_major_event_label])
    if narrative_timeline_labels.is_empty():
        lines.append("- (none)")
    else:
        var timeline_tail_count: int = min(3, narrative_timeline_labels.size())
        var timeline_start: int = narrative_timeline_labels.size() - timeline_tail_count
        for index in range(narrative_timeline_labels.size() - 1, timeline_start - 1, -1):
            lines.append("- %s" % str(narrative_timeline_labels[index]))
    return lines


func _build_player_overlay_lines(snapshot: Dictionary) -> Array[String]:
    var lines: Array[String] = []
    var tick: int = int(snapshot.get("tick", 0))
    var sim_time: float = float(snapshot.get("time", 0.0))
    var humans_alive: int = int(snapshot.get("humans_alive", 0))
    var monsters_alive: int = int(snapshot.get("monsters_alive", 0))
    var world_event_id: String = str(snapshot.get("world_event_active_id", ""))
    var world_event_name: String = str(snapshot.get("world_event_active_name", "None"))
    var world_event_remaining: float = float(snapshot.get("world_event_remaining", 0.0))
    var neutral_gate_active: bool = bool(snapshot.get("neutral_gate_active", false))
    var neutral_gate_poi: String = str(snapshot.get("neutral_gate_poi", "rift_gate"))
    var neutral_gate_remaining: float = float(snapshot.get("neutral_gate_remaining", 0.0))
    var dominant_faction: String = str(snapshot.get("dominant_faction", "neutral"))
    var dominant_doctrine: String = str(snapshot.get("dominant_doctrine", "")).strip_edges()
    var run_status: String = str(snapshot.get("run_status", "running"))
    var run_result_visible: bool = bool(snapshot.get("run_result_visible", false))
    var run_summary_lines: Array = snapshot.get("run_summary_lines", [])
    var narrative_timeline_labels: Array = snapshot.get("narrative_timeline_labels", [])

    for panel_line in _build_run_result_panel_lines(snapshot, 4):
        lines.append(panel_line)
    if run_result_visible:
        lines.append("")
    if _help_panel_visible:
        for help_panel_line in _build_help_panel_lines(snapshot):
            lines.append(help_panel_line)
        lines.append("")
    var objective_panel_lines: Array[String] = _build_objective_panel_lines(snapshot, OVERLAY_MODE_PLAYER)
    if not objective_panel_lines.is_empty():
        for objective_panel_line in objective_panel_lines:
            lines.append(objective_panel_line)
        lines.append("")
    var objective_interaction_feedback_player: String = _build_objective_interaction_feedback_line(snapshot, false)
    if objective_interaction_feedback_player != "":
        lines.append(objective_interaction_feedback_player)
        lines.append("")

    lines.append("HUD player | tick=%d t=%.0fs" % [tick, sim_time])
    lines.append("Population: H:%d M:%d" % [humans_alive, monsters_alive])
    if world_event_id != "":
        lines.append("World Event: %s (%.0fs)" % [world_event_name, world_event_remaining])
    else:
        lines.append("World Event: none")
    if neutral_gate_active:
        lines.append(
            "Neutral Gate: OPEN at %s (%.0fs)"
            % [neutral_gate_poi if neutral_gate_poi != "" else "rift_gate", neutral_gate_remaining]
        )

    var faction_label: String = "neutral"
    if dominant_faction == "human":
        faction_label = "humans"
    elif dominant_faction == "monster":
        faction_label = "monsters"
    var doctrine_label: String = dominant_doctrine if dominant_doctrine != "" else "(none)"
    lines.append("Dominance: faction=%s doctrine=%s" % [faction_label, doctrine_label])
    for help_line in _build_controls_help_lines(_overlay_mode, run_status, run_result_visible, false):
        lines.append(help_line)
    lines.append("Run Summary:")
    if run_summary_lines.is_empty():
        lines.append("- (none)")
    else:
        var run_summary_visible_count: int = min(2, run_summary_lines.size())
        for index in range(run_summary_visible_count):
            lines.append("- %s" % str(run_summary_lines[index]))

    lines.append("Timeline:")
    if narrative_timeline_labels.is_empty():
        lines.append("- (none)")
    else:
        var timeline_tail_count: int = min(3, narrative_timeline_labels.size())
        var timeline_start: int = narrative_timeline_labels.size() - timeline_tail_count
        for index in range(narrative_timeline_labels.size() - 1, timeline_start - 1, -1):
            lines.append("- %s" % str(narrative_timeline_labels[index]))

    return lines


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
            float(details.get("allegiance_vendetta_remaining", 0.0)),
            bool(details.get("allegiance_alert_active", false)),
            str(details.get("allegiance_alert_cause", "")),
            float(details.get("allegiance_alert_remaining", 0.0))
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
    vendetta_remaining: float = 0.0,
    alert_active: bool = false,
    alert_cause: String = "",
    alert_remaining: float = 0.0
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
    if alert_active:
        tags.append("alert:%s@%.0fs" % [alert_cause if alert_cause != "" else "watch", alert_remaining])
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
