extends Camera3D
class_name FreeCamera

@export var move_speed: float = 20.0
@export var boost_multiplier: float = 2.0
@export var mouse_sensitivity: float = 0.12

var _yaw: float = 0.0
var _pitch: float = -20.0
var _rotating: bool = false


func _ready() -> void:
    _yaw = rotation_degrees.y
    _pitch = rotation_degrees.x


func _unhandled_input(event: InputEvent) -> void:
    if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_RIGHT:
        _rotating = event.pressed
        Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED if _rotating else Input.MOUSE_MODE_VISIBLE)
        return

    if _rotating and event is InputEventMouseMotion:
        _yaw -= event.relative.x * mouse_sensitivity
        _pitch = clamp(_pitch - event.relative.y * mouse_sensitivity, -75.0, 75.0)
        rotation_degrees = Vector3(_pitch, _yaw, 0.0)


func _process(delta: float) -> void:
    var forward := -global_transform.basis.z
    forward.y = 0.0
    if forward.length_squared() > 0.0:
        forward = forward.normalized()

    var right := global_transform.basis.x
    right.y = 0.0
    if right.length_squared() > 0.0:
        right = right.normalized()

    var direction := Vector3.ZERO
    if Input.is_key_pressed(KEY_Z):
        direction += forward
    if Input.is_key_pressed(KEY_S):
        direction -= forward
    if Input.is_key_pressed(KEY_D):
        direction += right
    if Input.is_key_pressed(KEY_Q):
        direction -= right
    if Input.is_key_pressed(KEY_E):
        direction += Vector3.UP
    if Input.is_key_pressed(KEY_A):
        direction += Vector3.DOWN

    if direction == Vector3.ZERO:
        return

    var speed := move_speed * (boost_multiplier if Input.is_key_pressed(KEY_SHIFT) else 1.0)
    global_position += direction.normalized() * speed * delta
