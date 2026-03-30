import base64
from pathlib import Path
import random
import string

from locust import HttpUser, between, task


# 1x1 transparent PNG, valid image payload for repeatable upload tests.
VALID_TEST_IMAGE_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
)

IMAGE_DIR = Path("/mnt/locust/images")
IMAGE_EXTENSIONS = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png"}


class PhotoUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.username = "user_" + "".join(
            random.choices(string.ascii_lowercase + string.digits, k=8)
        )
        self.password = "Password123!"
        self.token = None
        self.auth_headers = {}
        self.own_photo_ids = []
        self.image_files = self._discover_image_files()

        # Register
        with self.client.post(
            "/api/auth/register/",
            json={
                "username": self.username,
                "email": f"{self.username}@example.com",
                "password": self.password,
                "password2": self.password,
            },
            name="auth_register",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 201):
                resp.failure(f"register failed: {resp.status_code} {resp.text}")

        # Token login
        with self.client.post(
            "/api/auth/token/",
            json={"username": self.username, "password": self.password},
            name="auth_token",
            catch_response=True,
        ) as resp:
            if resp.status_code == 200:
                token = resp.json().get("token")
                if token:
                    self.token = token
                    self.auth_headers = {"Authorization": f"Token {self.token}"}
                    resp.success()
                else:
                    resp.failure("token missing in response")
            else:
                resp.failure(f"token login failed: {resp.status_code} {resp.text}")

    def _discover_image_files(self):
        if not IMAGE_DIR.exists():
            return []
        files = []
        for path in IMAGE_DIR.iterdir():
            if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
                files.append(path)
        return files

    def _get_upload_file(self):
        if not self.image_files:
            return ("fallback.png", VALID_TEST_IMAGE_BYTES, "image/png")

        file_path = random.choice(self.image_files)
        content_type = IMAGE_EXTENSIONS.get(file_path.suffix.lower(), "application/octet-stream")
        return (file_path.name, file_path.read_bytes(), content_type)

    @task(3)
    def list_photos(self):
        self.client.get("/api/photos/", name="photos_list")
        self.client.get("/api/photos/?sort=date", name="photos_list_sort_date")

    @task(2)
    def get_health(self):
        self.client.get("/api/health/ready/", name="health_ready")

    @task(2)
    def upload_photo(self):
        if not self.token:
            return

        file_name, file_bytes, content_type = self._get_upload_file()

        with self.client.post(
            "/api/photos/",
            headers=self.auth_headers,
            data={"name": "Load Test Photo"},
            files={"photo": (file_name, file_bytes, content_type)},
            name="photos_create",
            catch_response=True,
        ) as resp:
            if resp.status_code in (200, 201):
                try:
                    photo_id = resp.json().get("id")
                    if photo_id is not None:
                        self.own_photo_ids.append(photo_id)
                    resp.success()
                except Exception:
                    resp.failure("invalid JSON in create response")
            else:
                resp.failure(f"create failed: {resp.status_code} {resp.text}")

    @task(2)
    def get_photo_detail(self):
        photo_id = None
        if self.own_photo_ids:
            photo_id = random.choice(self.own_photo_ids)
        else:
            r = self.client.get("/api/photos/", name="photos_list_for_detail")
            if r.status_code == 200:
                try:
                    items = r.json()
                    if isinstance(items, list) and items:
                        photo_id = items[0].get("id")
                except Exception:
                    return

        if photo_id is not None:
            self.client.get(f"/api/photos/{photo_id}/", name="photos_detail")

    @task(1)
    def delete_own_photo(self):
        if not self.token or not self.own_photo_ids:
            return

        photo_id = self.own_photo_ids.pop()
        self.client.delete(
            f"/api/photos/{photo_id}/",
            headers=self.auth_headers,
            name="photos_delete",
        )

    @task(1)
    def login_endpoint_check(self):
        self.client.post(
            "/api/auth/login/",
            json={"username": self.username, "password": self.password},
            name="auth_login",
        )

    @task(1)
    def logout_and_reauth(self):
        if not self.token:
            return

        self.client.post(
            "/api/auth/logout/",
            headers=self.auth_headers,
            name="auth_logout",
        )

        r = self.client.post(
            "/api/auth/token/",
            json={"username": self.username, "password": self.password},
            name="auth_token_after_logout",
        )
        if r.status_code == 200:
            token = r.json().get("token")
            if token:
                self.token = token
                self.auth_headers = {"Authorization": f"Token {self.token}"}