extends Node

const FAILURE_EXIT_CODE := 2

@onready var state_root: Node = $StateRoot


func _ready() -> void:
	call_deferred("_capture_selected_state")


func _capture_selected_state() -> void:
	var requested_state := OS.get_environment("GAME_START")
	var scene_path := OS.get_environment("GAME_RESOLVED_SCENE")
	var capture_path := OS.get_environment("GAME_CAPTURE_PATH")

	if requested_state.is_empty():
		_fail("GAME_START is empty")
		return
	if not scene_path.begins_with("res://"):
		_fail("GAME_RESOLVED_SCENE is not a res:// path: %s" % scene_path)
		return
	if capture_path.is_empty():
		_fail("GAME_CAPTURE_PATH is empty")
		return
	if not ResourceLoader.exists(scene_path, "PackedScene"):
		_fail("Resolved scene does not exist or is not a PackedScene: %s" % scene_path)
		return

	var packed_scene := load(scene_path) as PackedScene
	if packed_scene == null:
		_fail("Failed to load resolved scene: %s" % scene_path)
		return
	var instance := packed_scene.instantiate()
	if instance == null:
		_fail("Failed to instantiate resolved scene: %s" % scene_path)
		return
	state_root.add_child(instance)

	await get_tree().process_frame
	await get_tree().process_frame
	await RenderingServer.frame_post_draw

	var image := get_viewport().get_texture().get_image()
	if image == null or image.is_empty():
		_fail("Viewport returned an empty image after frame_post_draw")
		return

	var directory_error := DirAccess.make_dir_recursive_absolute(capture_path.get_base_dir())
	if directory_error != OK:
		_fail("Failed to create capture directory: %s" % error_string(directory_error))
		return
	var save_error := image.save_png(capture_path)
	if save_error != OK:
		_fail("Failed to save PNG: %s" % error_string(save_error))
		return

	var metadata := {
		"requested_state": requested_state,
		"resolved_scene": scene_path,
		"png_path": capture_path,
		"captured_at_utc": Time.get_datetime_string_from_system(true, true),
	}
	var metadata_path := capture_path + ".json"
	var metadata_file := FileAccess.open(metadata_path, FileAccess.WRITE)
	if metadata_file == null:
		_fail("Failed to open capture metadata: %s" % error_string(FileAccess.get_open_error()))
		return
	metadata_file.store_string(JSON.stringify(metadata, "\t") + "\n")
	metadata_file.close()

	print("godot-dev-loop: captured state=%s scene=%s png=%s" % [requested_state, scene_path, capture_path])
	get_tree().quit(0)


func _fail(message: String) -> void:
	push_error("godot-dev-loop capture failed: %s" % message)
	get_tree().quit(FAILURE_EXIT_CODE)
