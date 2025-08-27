from typing import List, Optional, Union, Dict, Any
from datetime import datetime
from enum import Enum
import json
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

class LocationType(Enum):
    CFI = "cfi"  # EPUB Canonical Fragment Identifier
    PAGE = "page"  # PDF page number

@dataclass
class EbookLocation:
    """Position in an ebook - either CFI for EPUB or page for PDF"""
    type: LocationType
    value: Union[str, int]  # CFI string for EPUB, page number for PDF
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "value": self.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EbookLocation':
        return cls(
            type=LocationType(data["type"]),
            value=data["value"]
        )

@dataclass
class Annotation:
    """Represents a highlight or note in an ebook"""
    id: str
    library_item_id: str  # AudioBookShelf library item ID
    user_id: str
    start_location: EbookLocation
    end_location: Optional[EbookLocation] = None  # For text selections
    text: Optional[str] = None  # Selected text content
    note: Optional[str] = None  # User's note
    color: str = "#ffff00"  # Highlight color
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["start_location"] = self.start_location.to_dict()
        if self.end_location:
            data["end_location"] = self.end_location.to_dict()
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Annotation':
        return cls(
            id=data["id"],
            library_item_id=data["library_item_id"],
            user_id=data["user_id"],
            start_location=EbookLocation.from_dict(data["start_location"]),
            end_location=EbookLocation.from_dict(data["end_location"]) if data.get("end_location") else None,
            text=data.get("text"),
            note=data.get("note"),
            color=data.get("color", "#ffff00"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )

@dataclass
class Bookmark:
    """Represents a bookmark in an ebook"""
    id: str
    library_item_id: str  # AudioBookShelf library item ID
    user_id: str
    location: EbookLocation
    title: str
    note: Optional[str] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["location"] = self.location.to_dict()
        data["created_at"] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bookmark':
        return cls(
            id=data["id"],
            library_item_id=data["library_item_id"],
            user_id=data["user_id"],
            location=EbookLocation.from_dict(data["location"]),
            title=data["title"],
            note=data.get("note"),
            created_at=datetime.fromisoformat(data["created_at"])
        )

class AnnotationStorage(ABC):
    """Abstract storage interface for annotations and bookmarks"""
    
    @abstractmethod
    def create_annotation(self, annotation: Annotation) -> Annotation:
        pass
    
    @abstractmethod
    def get_annotations(self, library_item_id: str, user_id: str) -> List[Annotation]:
        pass
    
    @abstractmethod
    def update_annotation(self, annotation_id: str, updates: Dict[str, Any]) -> Optional[Annotation]:
        pass
    
    @abstractmethod
    def delete_annotation(self, annotation_id: str, user_id: str) -> bool:
        pass
    
    @abstractmethod
    def create_bookmark(self, bookmark: Bookmark) -> Bookmark:
        pass
    
    @abstractmethod
    def get_bookmarks(self, library_item_id: str, user_id: str) -> List[Bookmark]:
        pass
    
    @abstractmethod
    def delete_bookmark(self, bookmark_id: str, user_id: str) -> bool:
        pass

class MemoryAnnotationStorage(AnnotationStorage):
    """In-memory storage implementation for testing"""
    
    def __init__(self):
        self.annotations: Dict[str, Annotation] = {}
        self.bookmarks: Dict[str, Bookmark] = {}
    
    def create_annotation(self, annotation: Annotation) -> Annotation:
        self.annotations[annotation.id] = annotation
        return annotation
    
    def get_annotations(self, library_item_id: str, user_id: str) -> List[Annotation]:
        return [
            ann for ann in self.annotations.values()
            if ann.library_item_id == library_item_id and ann.user_id == user_id
        ]
    
    def update_annotation(self, annotation_id: str, updates: Dict[str, Any]) -> Optional[Annotation]:
        if annotation_id not in self.annotations:
            return None
        
        annotation = self.annotations[annotation_id]
        
        for key, value in updates.items():
            if hasattr(annotation, key):
                setattr(annotation, key, value)
        
        annotation.updated_at = datetime.now()
        return annotation
    
    def delete_annotation(self, annotation_id: str, user_id: str) -> bool:
        if annotation_id in self.annotations:
            annotation = self.annotations[annotation_id]
            if annotation.user_id == user_id:
                del self.annotations[annotation_id]
                return True
        return False
    
    def create_bookmark(self, bookmark: Bookmark) -> Bookmark:
        self.bookmarks[bookmark.id] = bookmark
        return bookmark
    
    def get_bookmarks(self, library_item_id: str, user_id: str) -> List[Bookmark]:
        return [
            bm for bm in self.bookmarks.values()
            if bm.library_item_id == library_item_id and bm.user_id == user_id
        ]
    
    def delete_bookmark(self, bookmark_id: str, user_id: str) -> bool:
        if bookmark_id in self.bookmarks:
            bookmark = self.bookmarks[bookmark_id]
            if bookmark.user_id == user_id:
                del self.bookmarks[bookmark_id]
                return True
        return False

class EbookAnnotationManager:
    """Main service for managing ebook annotations and bookmarks"""
    
    def __init__(self, storage: AnnotationStorage):
        self.storage = storage
    
    def create_highlight(
        self,
        library_item_id: str,
        user_id: str,
        start_location: EbookLocation,
        end_location: Optional[EbookLocation] = None,
        text: Optional[str] = None,
        color: str = "#ffff00"
    ) -> Annotation:
        """Create a new highlight annotation"""
        import uuid
        
        annotation = Annotation(
            id=str(uuid.uuid4()),
            library_item_id=library_item_id,
            user_id=user_id,
            start_location=start_location,
            end_location=end_location,
            text=text,
            color=color
        )
        
        return self.storage.create_annotation(annotation)
    
    def create_note(
        self,
        library_item_id: str,
        user_id: str,
        location: EbookLocation,
        note: str,
        text: Optional[str] = None
    ) -> Annotation:
        """Create a new note annotation"""
        import uuid
        
        annotation = Annotation(
            id=str(uuid.uuid4()),
            library_item_id=library_item_id,
            user_id=user_id,
            start_location=location,
            text=text,
            note=note,
            color="transparent"  # Notes don't need highlight color
        )
        
        return self.storage.create_annotation(annotation)
    
    def get_annotations_for_book(self, library_item_id: str, user_id: str) -> List[Annotation]:
        """Get all annotations for a specific book"""
        return self.storage.get_annotations(library_item_id, user_id)
    
    def delete_annotation(self, annotation_id: str, user_id: str) -> bool:
        """Delete an annotation"""
        return self.storage.delete_annotation(annotation_id, user_id)
    
    def create_bookmark(
        self,
        library_item_id: str,
        user_id: str,
        location: EbookLocation,
        title: str,
        note: Optional[str] = None
    ) -> Bookmark:
        """Create a new bookmark"""
        import uuid
        
        bookmark = Bookmark(
            id=str(uuid.uuid4()),
            library_item_id=library_item_id,
            user_id=user_id,
            location=location,
            title=title,
            note=note
        )
        
        return self.storage.create_bookmark(bookmark)
    
    def get_bookmarks_for_book(self, library_item_id: str, user_id: str) -> List[Bookmark]:
        """Get all bookmarks for a specific book"""
        return self.storage.get_bookmarks(library_item_id, user_id)
    
    def delete_bookmark(self, bookmark_id: str, user_id: str) -> bool:
        """Delete a bookmark"""
        return self.storage.delete_bookmark(bookmark_id, user_id)
    
    def export_annotations(self, library_item_id: str, user_id: str) -> Dict[str, Any]:
        """Export all annotations and bookmarks for a book"""
        annotations = self.get_annotations_for_book(library_item_id, user_id)
        bookmarks = self.get_bookmarks_for_book(library_item_id, user_id)
        
        return {
            "library_item_id": library_item_id,
            "user_id": user_id,
            "exported_at": datetime.now().isoformat(),
            "annotations": [ann.to_dict() for ann in annotations],
            "bookmarks": [bm.to_dict() for bm in bookmarks]
        }
    
    def import_annotations(self, data: Dict[str, Any]) -> bool:
        """Import annotations and bookmarks from exported data"""
        try:
            for ann_data in data.get("annotations", []):
                annotation = Annotation.from_dict(ann_data)
                self.storage.create_annotation(annotation)
            
            for bm_data in data.get("bookmarks", []):
                bookmark = Bookmark.from_dict(bm_data)
                self.storage.create_bookmark(bookmark)
            
            return True
        except Exception:
            return False
