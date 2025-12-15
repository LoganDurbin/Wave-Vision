from app.tracking.TrackingMapper import TrackingMapper


def test_mapping_and_press_state():
    mapper = TrackingMapper()
    mapper.alpha = 1.0
    mapper.sensitivity = 1.0

    res = mapper.process_landmarks((0.1, 0.2), (0.3, 0.4), screen_width=100, screen_height=200)
    assert res is not None
    assert res.cursor_position_x == 80
    assert res.cursor_position_y == 60
    assert res.pressed is False


def test_smoothing_behavior():
    mapper = TrackingMapper()
    mapper.alpha = 0.5
    mapper.sensitivity = 1.0

    first = mapper.process_landmarks((0.0, 0.0), (0.0, 0.0), 100, 100)
    assert first.cursor_position_x == 100
    assert first.cursor_position_y == 0

    second = mapper.process_landmarks((1.0, 1.0), (1.0, 1.0), 100, 100)
    assert second.cursor_position_x == 50
    assert second.cursor_position_y == 50


def test_area_bounds_mapping():
    mapper = TrackingMapper()
    mapper.alpha = 1.0
    mapper.sensitivity = 1.0

    mapper.area_top_left_x = 0.25
    mapper.area_top_left_y = 0.25
    mapper.area_bottom_right_x = 0.75
    mapper.area_bottom_right_y = 0.75

    res = mapper.process_landmarks((0.5, 0.5), (0.5, 0.5), 100, 100)
    assert res.cursor_position_x == 50
    assert res.cursor_position_y == 50