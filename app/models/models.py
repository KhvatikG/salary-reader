from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Вспомогательная таблица для связи многие ко многим
association_table = Table(
    'employee_department_association',
    Base.metadata,
    Column('employee_id', Integer, ForeignKey('employees.id')),
    Column('department_id', Integer, ForeignKey('departments.id'))
)


class Department(Base):
    """Таблица отделов"""
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)
    name = Column(String(250), nullable=False)

    employees = relationship(
        "Employee",
        secondary=association_table,
        back_populates="departments"
    )


class Employee(Base):
    """Таблица сотрудников"""
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    motivation_program_id = Column(Integer, ForeignKey('motivation_programs.motivation_id'))

    departments = relationship(
        "Department",
        secondary=association_table,
        back_populates="employees"
    )
    motivation_program = relationship("MotivationProgram", back_populates="employees")


class MotivationProgram(Base):
    """Таблица мотивационных программ"""
    __tablename__ = 'motivation_programs'

    motivation_id = Column(Integer, primary_key=True)
    motivation_name = Column(String(250), nullable=False)

    employees = relationship("Employee", back_populates="motivation_program")
    thresholds = relationship("MotivateThreshold", back_populates="motivation_program")


class MotivateThreshold(Base):
    """Таблица уровней мотивационных программ"""
    __tablename__ = 'motivate_thresholds'

    threshold_id = Column(Integer, primary_key=True)
    motivation_program_id = Column(Integer, ForeignKey('motivation_programs.motivation_id'))
    # Порог при достижении которого получаем вознаграждение
    revenue_threshold = Column(Integer, nullable=False)
    # Вознаграждение при достижении порога
    salary = Column(Integer, nullable=False)
    # Привязываем к мотивационной программе
    motivation_program = relationship("MotivationProgram", back_populates="thresholds")
