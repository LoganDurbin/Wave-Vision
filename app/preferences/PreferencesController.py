import sqlite3
from dataclasses import dataclass


@dataclass
class Profile:
    id: int | None
    name: str
    camera_index: int
    sensitivity: float
    smoothing: float
    pinch_threshold: float

    # Custom area mapping (normalized 0.0-1.0 coordinates)
    area_top_left_x: float = 0.0
    area_top_left_y: float = 0.0
    area_bottom_right_x: float = 1.0
    area_bottom_right_y: float = 1.0


class PreferencesController:
    def __init__(self, db_path: str = "preferences.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self._initialize_db()

    def _initialize_db(self):
        cur = self.conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")

        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS Profiles (
              profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
              profile_name TEXT NOT NULL UNIQUE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS CameraConfigs (
              camera_config_id INTEGER PRIMARY KEY AUTOINCREMENT,
              camera_index INTEGER NOT NULL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS TrackingParams (
              tracking_params_id INTEGER PRIMARY KEY AUTOINCREMENT,
              smoothing REAL NOT NULL,
              sensitivity REAL NOT NULL,
              pinch_threshold REAL NOT NULL,
              area_top_left_x REAL NOT NULL DEFAULT 0.0,
              area_top_left_y REAL NOT NULL DEFAULT 0.0,
              area_bottom_right_x REAL NOT NULL DEFAULT 1.0,
              area_bottom_right_y REAL NOT NULL DEFAULT 1.0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ProfileMap_Camera (
              profile_id INTEGER PRIMARY KEY,
              camera_config_id INTEGER NOT NULL,
              FOREIGN KEY (profile_id) REFERENCES Profiles(profile_id) ON DELETE CASCADE,
              FOREIGN KEY (camera_config_id) REFERENCES CameraConfigs(camera_config_id)
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ProfileMap_Tracking (
              profile_id INTEGER PRIMARY KEY,
              tracking_params_id INTEGER NOT NULL,
              FOREIGN KEY (profile_id) REFERENCES Profiles(profile_id) ON DELETE CASCADE,
              FOREIGN KEY (tracking_params_id) REFERENCES TrackingParams(tracking_params_id)
            )
            """
        )
        self.conn.commit()

        cur.execute("SELECT COUNT(*) FROM Profiles")
        count = cur.fetchone()[0]
        if count == 0:
            self.create_profile(
                Profile(
                    id=None,
                    name="Default",
                    camera_index=0,
                    sensitivity=1.0,
                    smoothing=0.3,
                    pinch_threshold=0.05,
                )
            )

    def create_profile(self, profile: Profile) -> int:
        cur = self.conn.cursor()
        cur.execute("INSERT INTO Profiles(profile_name) VALUES (?)", (profile.name,))
        profile_id = cur.lastrowid
        cur.execute("INSERT INTO CameraConfigs(camera_index) VALUES (?)", (profile.camera_index,))
        camera_config_id = cur.lastrowid
        cur.execute(
            """
            INSERT INTO TrackingParams(smoothing, sensitivity, pinch_threshold,
              area_top_left_x, area_top_left_y, area_bottom_right_x, area_bottom_right_y)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile.smoothing,
                profile.sensitivity,
                profile.pinch_threshold,
                profile.area_top_left_x,
                profile.area_top_left_y,
                profile.area_bottom_right_x,
                profile.area_bottom_right_y,
            ),
        )
        tracking_params_id = cur.lastrowid
        cur.execute(
            "INSERT INTO ProfileMap_Camera(profile_id, camera_config_id) VALUES (?, ?)",
            (profile_id, camera_config_id),
        )
        cur.execute(
            "INSERT INTO ProfileMap_Tracking(profile_id, tracking_params_id) VALUES (?, ?)",
            (profile_id, tracking_params_id),
        )
        self.conn.commit()
        return profile_id

    def _row_to_profile(self, row) -> Profile:
        return Profile(
            id=row[0],
            name=row[1],
            camera_index=row[2],
            sensitivity=row[3],
            smoothing=row[4],
            pinch_threshold=row[5],
            area_top_left_x=row[6],
            area_top_left_y=row[7],
            area_bottom_right_x=row[8],
            area_bottom_right_y=row[9],
        )

    def get_profile(self, profile_id: int) -> Profile | None:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT p.profile_id, p.profile_name, c.camera_index,
                   t.sensitivity, t.smoothing, t.pinch_threshold,
                   t.area_top_left_x, t.area_top_left_y, t.area_bottom_right_x, t.area_bottom_right_y
            FROM Profiles p
              JOIN ProfileMap_Camera pmc ON pmc.profile_id = p.profile_id
              JOIN CameraConfigs c ON c.camera_config_id = pmc.camera_config_id
              JOIN ProfileMap_Tracking pmt ON pmt.profile_id = p.profile_id
              JOIN TrackingParams t ON t.tracking_params_id = pmt.tracking_params_id
            WHERE p.profile_id = ?
            """,
            (profile_id,),
        )
        row = cur.fetchone()
        return self._row_to_profile(row) if row else None

    def get_profile_by_name(self, name: str) -> Profile | None:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT p.profile_id, p.profile_name, c.camera_index,
                   t.sensitivity, t.smoothing, t.pinch_threshold,
                   t.area_top_left_x, t.area_top_left_y, t.area_bottom_right_x, t.area_bottom_right_y
            FROM Profiles p
              JOIN ProfileMap_Camera pmc ON pmc.profile_id = p.profile_id
              JOIN CameraConfigs c ON c.camera_config_id = pmc.camera_config_id
              JOIN ProfileMap_Tracking pmt ON pmt.profile_id = p.profile_id
              JOIN TrackingParams t ON t.tracking_params_id = pmt.tracking_params_id
            WHERE p.profile_name = ?
            """,
            (name,),
        )
        row = cur.fetchone()
        return self._row_to_profile(row) if row else None

    def get_all_profiles(self) -> list[Profile]:
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT p.profile_id, p.profile_name, c.camera_index,
                   t.sensitivity, t.smoothing, t.pinch_threshold,
                   t.area_top_left_x, t.area_top_left_y, t.area_bottom_right_x, t.area_bottom_right_y
            FROM Profiles p
              JOIN ProfileMap_Camera pmc ON pmc.profile_id = p.profile_id
              JOIN CameraConfigs c ON c.camera_config_id = pmc.camera_config_id
              JOIN ProfileMap_Tracking pmt ON pmt.profile_id = p.profile_id
              JOIN TrackingParams t ON t.tracking_params_id = pmt.tracking_params_id
            ORDER BY p.profile_id
            """
        )
        rows = cur.fetchall()
        return [self._row_to_profile(row) for row in rows]

    def update_profile(self, profile: Profile):
        cur = self.conn.cursor()
        cur.execute("UPDATE Profiles SET profile_name = ? WHERE profile_id = ?", (profile.name, profile.id))
        cur.execute(
            "SELECT camera_config_id FROM ProfileMap_Camera WHERE profile_id = ?",
            (profile.id,),
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                "UPDATE CameraConfigs SET camera_index = ? WHERE camera_config_id = ?",
                (profile.camera_index, row[0]),
            )
        cur.execute(
            "SELECT tracking_params_id FROM ProfileMap_Tracking WHERE profile_id = ?",
            (profile.id,),
        )
        row = cur.fetchone()
        if row:
            cur.execute(
                """
                UPDATE TrackingParams
                SET smoothing = ?, sensitivity = ?, pinch_threshold = ?,
                    area_top_left_x = ?, area_top_left_y = ?, area_bottom_right_x = ?, area_bottom_right_y = ?
                WHERE tracking_params_id = ?
                """,
                (
                    profile.smoothing,
                    profile.sensitivity,
                    profile.pinch_threshold,
                    profile.area_top_left_x,
                    profile.area_top_left_y,
                    profile.area_bottom_right_x,
                    profile.area_bottom_right_y,
                    row[0],
                ),
            )
        self.conn.commit()

    def delete_profile(self, profile_id: int):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT camera_config_id FROM ProfileMap_Camera WHERE profile_id = ?",
            (profile_id,),
        )
        cam_row = cur.fetchone()
        cur.execute(
            "SELECT tracking_params_id FROM ProfileMap_Tracking WHERE profile_id = ?",
            (profile_id,),
        )
        tr_row = cur.fetchone()
        cur.execute("DELETE FROM ProfileMap_Camera WHERE profile_id = ?", (profile_id,))
        cur.execute("DELETE FROM ProfileMap_Tracking WHERE profile_id = ?", (profile_id,))
        cur.execute("DELETE FROM Profiles WHERE profile_id = ?", (profile_id,))
        if cam_row:
            cur.execute("DELETE FROM CameraConfigs WHERE camera_config_id = ?", (cam_row[0],))
        if tr_row:
            cur.execute("DELETE FROM TrackingParams WHERE tracking_params_id = ?", (tr_row[0],))
        self.conn.commit()

    def close(self):
        self.conn.close()
