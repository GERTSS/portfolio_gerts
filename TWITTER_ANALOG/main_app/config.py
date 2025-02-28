import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:user@localhost/twitter")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "user")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "user")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "twitter")
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "uploads")
    ALLOWED_EXTENSIONS = {'png', 'jpeg', 'jpg', 'mp4', 'mov'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    template_folder = os.path.join(BASE_DIR, "templates")
    static_folder = os.path.join(BASE_DIR, "static")
    