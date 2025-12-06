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
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                camera_index INTEGER NOT NULL,
                sensitivity REAL NOT NULL,
                smoothing REAL NOT NULL,
                pinch_threshold REAL NOT NULL,
                area_top_left_x REAL NOT NULL DEFAULT 0.0,
                area_top_left_y REAL NOT NULL DEFAULT 0.0,
                area_bottom_right_x REAL NOT NULL DEFAULT 1.0,
                area_bottom_right_y REAL NOT NULL DEFAULT 1.0
            )
        """)
        self.conn.commit()

        if not self.get_all_profiles():
            self.create_profile(Profile(
                id=None,
                name="Default",
                camera_index=0,
                sensitivity=1.0,
                smoothing=0.3,
                pinch_threshold=0.05
            ))

    def create_profile(self, profile: Profile) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO profiles (name, camera_index, sensitivity, smoothing, pinch_threshold,
                                  area_top_left_x, area_top_left_y, area_bottom_right_x, area_bottom_right_y)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (profile.name, profile.camera_index, profile.sensitivity, profile.smoothing, profile.pinch_threshold,
              profile.area_top_left_x, profile.area_top_left_y, profile.area_bottom_right_x, profile.area_bottom_right_y))
        self.conn.commit()
        return cursor.lastrowid

    def _row_to_profile(self, row) -> Profile:
        return Profile(
            id=row[0], name=row[1], camera_index=row[2],
            sensitivity=row[3], smoothing=row[4], pinch_threshold=row[5],
            area_top_left_x=row[6] if len(row) > 6 else 0.0,
            area_top_left_y=row[7] if len(row) > 7 else 0.0,
            area_bottom_right_x=row[8] if len(row) > 8 else 1.0,
            area_bottom_right_y=row[9] if len(row) > 9 else 1.0
        )

    def get_profile(self, profile_id: int) -> Profile | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()
        if row:
            return self._row_to_profile(row)
        return None

    def get_profile_by_name(self, name: str) -> Profile | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return self._row_to_profile(row)
        return None

    def get_all_profiles(self) -> list[Profile]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM profiles")
        rows = cursor.fetchall()
        return [self._row_to_profile(row) for row in rows]

    def update_profile(self, profile: Profile):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE profiles
            SET name = ?, camera_index = ?, sensitivity = ?, smoothing = ?, pinch_threshold = ?,
                area_top_left_x = ?, area_top_left_y = ?, area_bottom_right_x = ?, area_bottom_right_y = ?
            WHERE id = ?
        """, (profile.name, profile.camera_index, profile.sensitivity,
              profile.smoothing, profile.pinch_threshold,
              profile.area_top_left_x, profile.area_top_left_y,
              profile.area_bottom_right_x, profile.area_bottom_right_y, profile.id))
        self.conn.commit()

    def delete_profile(self, profile_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
