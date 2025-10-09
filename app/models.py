from sqlalchemy import Column,String,DateTime,Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime,timezone
import uuid
from app.database import Base

class Memory(Base):
    __tablename__="memories"
    id=Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4)
    user_id=Column(UUID(as_uuid=True),nullable=False,index=True)
    content=Column(String,nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    __table_args__=(
        Index('ix_memories_user_id_created_at','user_id','created_at'),
    )
