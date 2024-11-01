from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Вспомогательная таблица для связи многие ко многим между таблицами Employee и Department
association_table = Table(
    'employee_department_association',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey('employees.id')),
    Column('department_id', Integer, ForeignKey('departments.id'))
)


class Department(Base):
    """Таблица, представляющая отделы в компании.

   Содержит основную информацию об отделе, такую как
   уникальный код и имя.
   """
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String(250), nullable=False)

    # Связь многие ко многим с сотрудниками
    employees = relationship(
        "Employee",
        secondary=association_table,
        back_populates="departments"
    )

    # Один-ко-многим связь с мотивационными программами
    motivation_programs = relationship(
        "MotivationProgram",
        back_populates="department"
    )


class Employee(Base):
    """Таблица, представляющая сотрудников.

    Содержит информацию об имени и мотивационной программе сотрудника.
    """
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    motivation_program_id = Column(Integer, ForeignKey('motivation_programs.id'))

    # Связь многие ко многим с отделами
    departments = relationship(
        "Department",
        secondary=association_table,
        back_populates="employees"
    )
    # Связь с текущей мотивационной программой
    motivation_program = relationship("MotivationProgram", back_populates="employees")


class MotivationProgram(Base):
    """Таблица, представляющая мотивационные программы.

    Включает ключевые характеристики программы.
    Также сопровождается порогами мотивации и связями с сотрудниками.
    """
    __tablename__ = 'motivation_programs'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    # Внешний ключ для связи с отделом
    department_code = Column(Integer, ForeignKey('departments.code'))

    # Один-ко-многим связь с сотрудниками
    employees = relationship(
                            "Employee",
                            back_populates="motivation_program"
    )

    # Один-ко-многим связь с порогами мотивации
    thresholds = relationship(
                            "MotivationThreshold",
                            back_populates="motivation_program",
                            cascade="all, delete-orphan"
    )

    # Один-ко-многим связь с отделами
    department = relationship(
                            "Department",
                            back_populates="motivation_programs"
    )


class MotivationThreshold(Base):
    """Таблица, представляющая уровни порогов мотивации.

   Хранит условия вознаграждения, такие как требуемый доход
   и соответствующая награда.
   """
    __tablename__ = 'motivate_thresholds'

    id = Column(Integer, primary_key=True)

    motivation_program_id = Column(Integer, ForeignKey('motivation_programs.id'))
    # Порог при достижении которого получаем вознаграждение
    revenue_threshold = Column(Integer, nullable=False)
    # Вознаграждение при достижении порога
    salary = Column(Integer, nullable=False)
    # Связь с мотивационной программой
    motivation_program = relationship("MotivationProgram", back_populates="thresholds")
