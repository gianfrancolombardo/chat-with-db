# utils/connections.py

import os
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

Base = declarative_base()

class Connection(Base):
    __tablename__ = "connections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)
    host = Column(String, nullable=True)
    port = Column(String, nullable=True)
    user = Column(String, nullable=True)
    password = Column(String, nullable=True)
    database = Column(String, nullable=True)
    path = Column(String, nullable=True)  # For SQLite

class ConnectionManager:
    def __init__(self):
        """Initialize the ConnectionManager with the database engine and session."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, "../chatwithdata.db")
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def init_db(self) -> None:
        """Initialize the database by creating all necessary tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
        except SQLAlchemyError as e:
            raise Exception(f"Error initializing database: {e}")

    def add_connection(self, name: str, type_: str, host: str, port: str, user: str, password: str, database: str, path: str) -> None:
        """Add a new connection to the database."""
        session = self.SessionLocal()
        try:
            new_connection = Connection(
                name=name, type=type_, host=host, port=port,
                user=user, password=password, database=database, path=path
            )
            session.add(new_connection)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise ValueError("Connection name already exists")
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error adding connection: {e}")
        finally:
            session.close()

    def get_connections(self) -> list:
        """Retrieve all saved connections from the database."""
        session = self.SessionLocal()
        try:
            return session.query(Connection).all()
        except SQLAlchemyError as e:
            raise Exception(f"Error retrieving connections: {e}")
        finally:
            session.close()

    def delete_connection(self, conn_id: int) -> None:
        """Delete a connection from the database by its ID."""
        session = self.SessionLocal()
        try:
            connection = session.query(Connection).filter(Connection.id == conn_id).first()
            if connection:
                session.delete(connection)
                session.commit()
            else:
                raise ValueError("Connection not found")
        except SQLAlchemyError as e:
            session.rollback()
            raise Exception(f"Error deleting connection: {e}")
        finally:
            session.close()

    def get_engine(self, connection: Connection) -> create_engine:
        """Create and return a SQLAlchemy engine based on the selected connection."""

        if connection.type == 'postgresql':
            db_url = f"postgresql://{connection.user}:{connection.password}@{connection.host}:{connection.port}/{connection.database}"
        elif connection.type == 'sqlite':
            db_url = f"sqlite:///{connection.path}"
        else:
            raise ValueError("Unsupported connection type")
        
        try:
            return create_engine(db_url)
        except SQLAlchemyError as e:
            raise Exception(f"Error creating engine: {e}")