from typing import TypeVar, Generic, Optional, List, Dict, Any, Type
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from sqlalchemy.exc import IntegrityError

# Tipos genéricos para el repository
ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Repositorio base con operaciones CRUD comunes"""
    
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model
        
    def get(self, id: int) -> Optional[ModelType]:
        """Obtener entidad por ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Obtener múltiples entidades con filtros"""
        query = self.db.query(self.model)
        
        # Aplicar filtros
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    column = getattr(self.model, field)
                    if isinstance(value, list):
                        query = query.filter(column.in_(value))
                    else:
                        query = query.filter(column == value)
        
        # Aplicar ordenamiento
        if order_by and hasattr(self.model, order_by):
            column = getattr(self.model, order_by)
            if order_desc:
                query = query.order_by(desc(column))
            else:
                query = query.order_by(asc(column))
        
        return query.offset(skip).limit(limit).all()
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Contar entidades con filtros"""
        query = self.db.query(self.model)
        
        if filters:
            for field, value in filters.items():
                if hasattr(self.model, field) and value is not None:
                    column = getattr(self.model, field)
                    if isinstance(value, list):
                        query = query.filter(column.in_(value))
                    else:
                        query = query.filter(column == value)
        
        return query.count()
    
    def exists(self, id: int) -> bool:
        """Verificar si existe una entidad por ID"""
        return self.db.query(self.model).filter(self.model.id == id).first() is not None
    
    def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Crear nueva entidad"""
        if hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump()
        elif hasattr(obj_in, 'dict'):
            obj_data = obj_in.dict()
        else:
            obj_data = obj_in
        
        db_obj = self.model(**obj_data)
        
        try:
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Error al crear: {str(e)}")
    
    def update(
        self,
        db_obj: ModelType,
        obj_in: UpdateSchemaType
    ) -> ModelType:
        """Actualizar entidad existente"""
        if hasattr(obj_in, 'model_dump'):
            update_data = obj_in.model_dump(exclude_unset=True)
        elif hasattr(obj_in, 'dict'):
            update_data = obj_in.dict(exclude_unset=True)
        else:
            update_data = obj_in
        
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_obj)
            return db_obj
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"Error al actualizar: {str(e)}")
    
    def delete(self, id: int) -> bool:
        """Eliminar entidad por ID"""
        obj = self.get(id)
        if obj:
            try:
                self.db.delete(obj)
                self.db.commit()
                return True
            except IntegrityError as e:
                self.db.rollback()
                raise ValueError(f"Error al eliminar: {str(e)}")
        return False
