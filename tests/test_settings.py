from edutap.image_api.settings import Settings, get_settings


def test_defaults_are_sane():
    s = Settings()
    assert 0 < s.min_face_area_ratio < s.max_face_area_ratio <= 1.0
    assert s.default_output_size == 512
    assert s.min_output_size <= s.default_output_size <= s.max_output_size
    assert s.model_path.endswith("face_landmarker.task")


def test_env_override(monkeypatch):
    monkeypatch.setenv("IMAGE_API_MAX_YAW_DEG", "25")
    assert Settings().max_yaw_deg == 25.0


def test_get_settings_is_cached():
    assert get_settings() is get_settings()
