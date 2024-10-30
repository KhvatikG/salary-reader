from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship


Base = declarative_base()

class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    employees = relationship("Employee", back_populates="department")


class Employee(Base):
    __tablename__ = 'employee'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    # ForeignKey('department.id')
    department_id = Column(Integer, ForeignKey('department.id'))
    department = relationship("Department", back_populates="employees")


class MotivationProgram(Base):
    __tablename__ = 'motivation_program'
    motivation_id = Column(Integer, primary_key=True)
    motivation_name = Column(String(250), nullable=False)
    employees = relationship("Employee", back_populates="motivation_program")
    thresholds = relationship("MotivateThreshold", back_populates="motivation_program")

class MotivateThreshold(Base):
    __tablename__ = 'motivate_threshold'
    threshold_id = Column(Integer, primary_key=True)
    # ForeignKey('motivation_program.motivation_id')
    motivation_program_id = Column(Integer, ForeignKey('motivation_program.motivation_id'))
    # Порог при достижении которого получаем вознаграждение
    revenue_threshold = Column(Integer, nullable=False)
    # Вознаграждение при достижении порога
    salary = Column(Integer, nullable=False)
    # Привязываем к мотивационной программе
    motivation_program = relationship("MotivationProgram", back_populates="thresholds")
