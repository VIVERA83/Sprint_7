from datetime import datetime
from uuid import uuid4

from sqlalchemy import BOOLEAN, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID, VARCHAR
from sqlalchemy.orm import backref, relationship
from src.db.postgres import db_postgres


class User(db_postgres.Model):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    email = Column(String(80), unique=True, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, unique=True)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.now)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.now)

    roles = relationship(
        "Role",
        secondary="users_roles",
        backref=backref("users", lazy="joined", cascade="all,delete"),
        lazy="joined",
    )

    agents = relationship("UserSignIn", lazy="joined", cascade="all,delete")

    super_user = Column(BOOLEAN, unique=True, nullable=True)


class Role(db_postgres.Model):
    __tablename__ = "roles"
    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    name = Column(
        VARCHAR(255),
        nullable=False,
        unique=True,
    )


class UserRole(db_postgres.Model):
    __tablename__ = "users_roles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    id_user = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    id_role = Column(UUID(as_uuid=True), ForeignKey("roles.id"))


class SocialAccounts(db_postgres.Model):
    __tablename__ = "social_accounts"
    __table_args__ = (UniqueConstraint("social_id", "social_name", name="social_pk"),)

    id = Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    social_id = Column(String(255), nullable=False)
    social_name = Column(String(255), nullable=False)

    user = relationship("User", backref=backref("social_accounts", lazy=True))

    def __repr__(self):
        return f"<SocialAccount {self.social_name}:{self.user_id}>"


def create_partition(target, connection, **kw) -> None:
    """creating partition by user_sign_in"""
    # Эта байда не работает, ошибки которые здесь происходят где-то, перехватываются.
    # К сожалению не заною как посмотреть ошибки которые здесь появляются
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_smart" PARTITION OF "users_sign_in" FOR VALUES IN ('pc')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_mobile" PARTITION OF "users_sign_in" FOR VALUES IN ('mobile')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_tablet" PARTITION OF "users_sign_in" FOR VALUES IN ('tablet')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_sign_in_other" PARTITION OF "users_sign_in" FOR VALUES IN ('other')"""
    )
    1 + "поэтому пришлось создавать связи в инициализации БД "  # noqa


class UserSignIn(db_postgres.Model):
    __tablename__ = "users_sign_in"
    __table_args__ = (
        UniqueConstraint("id", "user_device_type"),
        {
            "postgresql_partition_by": "LIST (user_device_type)",
            "listeners": [("after_create", create_partition)],
        },
    )

    id = db_postgres.Column(
        UUID(as_uuid=True), primary_key=True, default=uuid4, nullable=False
    )
    user_device_type = db_postgres.Column(db_postgres.Text, primary_key=True)
    user_agent = db_postgres.Column(db_postgres.Text)
    logged_in_at = db_postgres.Column(db_postgres.DateTime, default=datetime.utcnow)
    user_id = db_postgres.Column(UUID(as_uuid=True), db_postgres.ForeignKey("users.id"))

    def __repr__(self):
        return f"<UserSignIn {self.user_id}:{self.logged_in_at}>"
