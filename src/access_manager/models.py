from sqlalchemy import Column, Table, ForeignKey, Integer, String, Boolean, DateTime, func, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Общее метаданные
metadata = MetaData()

# Таблицы ассоциаций
user_roles = Table(
    'user_roles', metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

role_permissions = Table(
    'role_permissions', metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class Base(DeclarativeBase):
    metadata = metadata

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    roles: Mapped[list['Role']] = relationship(
        'Role', secondary=user_roles, back_populates='users'
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"

class Role(Base):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    users: Mapped[list[User]] = relationship(
        'User', secondary=user_roles, back_populates='roles'
    )
    permissions: Mapped[list['Permission']] = relationship(
        'Permission', secondary=role_permissions, back_populates='roles'
    )

    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name='{self.name}')>"

class Permission(Base):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    roles: Mapped[list[Role]] = relationship(
        'Role', secondary=role_permissions, back_populates='permissions'
    )

    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name='{self.name}')>"
