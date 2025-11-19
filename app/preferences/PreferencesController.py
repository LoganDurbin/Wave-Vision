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
                pinch_threshold REAL NOT NULL
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
            INSERT INTO profiles (name, camera_index, sensitivity, smoothing, pinch_threshold)
            VALUES (?, ?, ?, ?, ?)
        """, (profile.name, profile.camera_index, profile.sensitivity, profile.smoothing, profile.pinch_threshold))
        self.conn.commit()
        return cursor.lastrowid

    def get_profile(self, profile_id: int) -> Profile | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()
        if row:
            return Profile(id=row[0], name=row[1], camera_index=row[2],
                         sensitivity=row[3], smoothing=row[4], pinch_threshold=row[5])
        return None

    def get_profile_by_name(self, name: str) -> Profile | None:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM profiles WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return Profile(id=row[0], name=row[1], camera_index=row[2],
                         sensitivity=row[3], smoothing=row[4], pinch_threshold=row[5])
        return None

    def get_all_profiles(self) -> list[Profile]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM profiles")
        rows = cursor.fetchall()
        return [Profile(id=row[0], name=row[1], camera_index=row[2],
                       sensitivity=row[3], smoothing=row[4], pinch_threshold=row[5])
                for row in rows]

    def update_profile(self, profile: Profile):
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE profiles
            SET name = ?, camera_index = ?, sensitivity = ?, smoothing = ?, pinch_threshold = ?
            WHERE id = ?
        """, (profile.name, profile.camera_index, profile.sensitivity,
              profile.smoothing, profile.pinch_threshold, profile.id))
        self.conn.commit()

    def delete_profile(self, profile_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()
