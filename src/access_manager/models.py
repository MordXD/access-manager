from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, Table, DateTime, func
from sqlalchemy.orm import DeclarativeBase, relationship # Исправлен импорт

class Base(DeclarativeBase):
    pass

# Таблица ассоциации для связи Многие-ко-Многим между User и Role
user_roles_association_table = Table( # Добавил _table для ясности, что это объект Table
    "user_roles", # Имя таблицы в БД
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
)

# Таблица ассоциации для связи Многие-ко-Многим между Role и Permission
role_permissions_association_table = Table( # Добавил _table для ясности
    "role_permissions", # Имя таблицы в БД
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id"), primary_key=True),
    Column("permission_id", Integer, ForeignKey("permissions.id"), primary_key=True) # Исправлена опечатка
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False) # Был 'name'
    email = Column(String(255), unique=True, index=True, nullable=False)    # Важное поле
    hashed_password = Column(String(255), nullable=False)                   # Важное поле
    is_active = Column(Boolean, default=True)                               # Важное поле
    is_superuser = Column(Boolean, default=False)                           # Важное поле
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    roles = relationship( # Исправлено relationships на relationship
        'Role',
        secondary=user_roles_association_table, # Используем имя переменной таблицы
        back_populates='users'
    )

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True) # Вернули description
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    users = relationship( # Исправлено
        'User',
        secondary=user_roles_association_table, # Используем имя переменной таблицы
        back_populates='roles'
    )
    permissions = relationship( # Исправлено
        'Permission',
        secondary=role_permissions_association_table, # Используем имя переменной таблицы
        back_populates='roles' # Эта связь ведет к Permission, а Permission.roles будет back_populates='permissions'
    )

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True) # Вернули description
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    roles = relationship( # Исправлено
        'Role',
        secondary=role_permissions_association_table, # Используем имя переменной таблицы
        back_populates='permissions' # Здесь правильно: Role.permissions back_populates='roles'
    )

    def __repr__(self):
        return f"<Permission(id={self.id}, name='{self.name}')>"