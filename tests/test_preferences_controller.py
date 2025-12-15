import os
import sqlite3

from app.preferences.PreferencesController import PreferencesController, Profile


def test_default_profile_created(tmp_path):
    db_path = tmp_path / "prefs.db"
    ctrl = PreferencesController(str(db_path))
    try:
        profiles = ctrl.get_all_profiles()
        assert len(profiles) >= 1
        assert profiles[0].name == "Default"
    finally:
        ctrl.close()


def test_crud_profile(tmp_path):
    db_path = tmp_path / "prefs.db"
    ctrl = PreferencesController(str(db_path))
    try:
        p = Profile(
            id=None,
            name="Work",
            camera_index=1,
            sensitivity=1.5,
            smoothing=0.4,
            pinch_threshold=0.06,
            area_top_left_x=0.1,
            area_top_left_y=0.2,
            area_bottom_right_x=0.9,
            area_bottom_right_y=0.8,
        )
        new_id = ctrl.create_profile(p)
        assert isinstance(new_id, int)

        loaded = ctrl.get_profile_by_name("Work")
        assert loaded is not None
        assert loaded.camera_index == 1

        loaded.smoothing = 0.5
        ctrl.update_profile(loaded)
        reloaded = ctrl.get_profile(loaded.id)
        assert reloaded.smoothing == 0.5

        ctrl.delete_profile(new_id)
        assert ctrl.get_profile(new_id) is None
    finally:
        ctrl.close()
