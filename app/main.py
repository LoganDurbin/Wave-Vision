from app.camera.CameraController import CameraController
from app.cursor.CursorController import CursorController
from app.system.SystemController import SystemController
from app.tracking.TrackingController import TrackingController
from app.tracking.TrackingParams import TrackingParams


def main():
    system_controller = SystemController(
        camera_controller=CameraController(0, size=(1920, 1080), fps=30),
        tracking_controller=TrackingController(
            TrackingParams(area_size_x=1920//4, area_size_y=1080//4, model_path="models/hand_landmarker.task")
        ),
        cursor_controller=CursorController()
    )

    system_controller.start()


if __name__ == "__main__":
    main()
