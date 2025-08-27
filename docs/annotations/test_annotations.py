import pytest
import json
from datetime import datetime
from ebook_annotations import (
    EbookAnnotationManager, MemoryAnnotationStorage,
    EbookLocation, LocationType, Annotation, Bookmark
)
from annotation_api import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def sample_locations():
    return {
        "epub_cfi": EbookLocation(LocationType.CFI, "/6/4[chap01ref]!/4[body01]/10[para05]/3:10"),
        "pdf_page": EbookLocation(LocationType.PAGE, 42)
    }

class TestEbookAnnotationManager:
    def test_create_highlight_epub(self, sample_locations):
        storage = MemoryAnnotationStorage()
        manager = EbookAnnotationManager(storage)
        
        annotation = manager.create_highlight(
            library_item_id="book123",
            user_id="user456", 
            start_location=sample_locations["epub_cfi"],
            text="This is highlighted text",
            color="#ff0000"
        )
        
        assert annotation.library_item_id == "book123"
        assert annotation.user_id == "user456"
        assert annotation.start_location.type == LocationType.CFI
        assert annotation.text == "This is highlighted text"
        assert annotation.color == "#ff0000"
        assert annotation.created_at is not None

    def test_create_note_pdf(self, sample_locations):
        storage = MemoryAnnotationStorage()
        manager = EbookAnnotationManager(storage)
        
        annotation = manager.create_note(
            library_item_id="book789",
            user_id="user456",
            location=sample_locations["pdf_page"],
            note="Important concept here"
        )
        
        assert annotation.library_item_id == "book789"
        assert annotation.start_location.type == LocationType.PAGE
        assert annotation.start_location.value == 42
        assert annotation.note == "Important concept here"
        assert annotation.color == "transparent"

    def test_create_bookmark(self, sample_locations):
        storage = MemoryAnnotationStorage()
        manager = EbookAnnotationManager(storage)
        
        bookmark = manager.create_bookmark(
            library_item_id="book123",
            user_id="user456",
            location=sample_locations["epub_cfi"],
            title="Chapter 1 Start",
            note="Beginning of the story"
        )
        
        assert bookmark.library_item_id == "book123"
        assert bookmark.title == "Chapter 1 Start"
        assert bookmark.note == "Beginning of the story"
        assert bookmark.location.type == LocationType.CFI

    def test_get_annotations_for_book(self, sample_locations):
        storage = MemoryAnnotationStorage()
        manager = EbookAnnotationManager(storage)
        
        # Create multiple annotations
        ann1 = manager.create_highlight(
            library_item_id="book123",
            user_id="user456",
            start_location=sample_locations["epub_cfi"],
            text="First highlight"
        )
        
        ann2 = manager.create_note(
            library_item_id="book123", 
            user_id="user456",
            location=sample_locations["pdf_page"],
            note="Important note"
        )
        
        # Create annotation for different book (should not be returned)
        manager.create_highlight(
            library_item_id="book999",
            user_id="user456",
            start_location=sample_locations["epub_cfi"],
            text="Different book highlight"
        )
        
        annotations = manager.get_annotations_for_book("book123", "user456")
        assert len(annotations) == 2
        assert all(ann.library_item_id == "book123" for ann in annotations)

    def test_export_import_annotations(self, sample_locations):
        storage = MemoryAnnotationStorage()
        manager = EbookAnnotationManager(storage)
        
        # Create test data
        manager.create_highlight(
            library_item_id="book123",
            user_id="user456",
            start_location=sample_locations["epub_cfi"],
            text="Test highlight"
        )
        
        manager.create_bookmark(
            library_item_id="book123",
            user_id="user456", 
            location=sample_locations["pdf_page"],
            title="Test bookmark"
        )
        
        # Export
        export_data = manager.export_annotations("book123", "user456")
        assert len(export_data["annotations"]) == 1
        assert len(export_data["bookmarks"]) == 1
        
        # Clear storage and import
        storage2 = MemoryAnnotationStorage()
        manager2 = EbookAnnotationManager(storage2)
        success = manager2.import_annotations(export_data)
        
        assert success
        annotations = manager2.get_annotations_for_book("book123", "user456")
        bookmarks = manager2.get_bookmarks_for_book("book123", "user456")
        assert len(annotations) == 1
        assert len(bookmarks) == 1

class TestAnnotationAPI:
    def test_create_highlight_api(self, client):
        response = client.post('/api/library-items/book123/annotations', 
            json={
                "user_id": "user456",
                "type": "highlight", 
                "start_location": {
                    "type": "cfi",
                    "value": "/6/4[chap01ref]!/4[body01]/10[para05]/3:10"
                },
                "end_location": {
                    "type": "cfi", 
                    "value": "/6/4[chap01ref]!/4[body01]/10[para05]/3:25"
                },
                "text": "Selected text",
                "color": "#ffff00"
            })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["library_item_id"] == "book123"
        assert data["user_id"] == "user456"
        assert data["text"] == "Selected text"
        assert data["start_location"]["type"] == "cfi"

    def test_create_note_api(self, client):
        response = client.post('/api/library-items/book789/annotations',
            json={
                "user_id": "user456",
                "type": "note",
                "start_location": {
                    "type": "page",
                    "value": 42
                },
                "note": "This is my note"
            })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["library_item_id"] == "book789"
        assert data["note"] == "This is my note"
        assert data["start_location"]["type"] == "page"
        assert data["start_location"]["value"] == 42

    def test_create_bookmark_api(self, client):
        response = client.post('/api/library-items/book123/bookmarks',
            json={
                "user_id": "user456",
                "location": {
                    "type": "cfi",
                    "value": "/6/4[chap01ref]!/4[body01]/10[para05]/3:10"
                },
                "title": "Important Chapter",
                "note": "Remember to review this"
            })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data["title"] == "Important Chapter"
        assert data["note"] == "Remember to review this"

    def test_get_annotations_api(self, client):
        # First create an annotation
        client.post('/api/library-items/book123/annotations',
            json={
                "user_id": "user456",
                "type": "highlight",
                "start_location": {
                    "type": "cfi", 
                    "value": "/6/4[chap01ref]!/4[body01]/10[para05]/3:10"
                },
                "text": "Test highlight"
            })
        
        # Get annotations
        response = client.get('/api/library-items/book123/annotations?user_id=user456')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["annotations"]) >= 1

    def test_get_bookmarks_api(self, client):
        # First create a bookmark
        client.post('/api/library-items/book123/bookmarks',
            json={
                "user_id": "user456",
                "location": {
                    "type": "page",
                    "value": 1
                },
                "title": "Start"
            })
        
        # Get bookmarks
        response = client.get('/api/library-items/book123/bookmarks?user_id=user456')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data["bookmarks"]) >= 1

    def test_export_import_api(self, client):
        # Create test data
        client.post('/api/library-items/book123/annotations',
            json={
                "user_id": "user456",
                "type": "highlight",
                "start_location": {"type": "page", "value": 10},
                "text": "Export test"
            })
        
        # Export
        response = client.get('/api/library-items/book123/export?user_id=user456')
        assert response.status_code == 200
        export_data = response.get_json()
        
        # Import (in real scenario this would be to a different storage)
        response = client.post('/api/library-items/book123/import',
            json=export_data)
        assert response.status_code == 200

    def test_health_check(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["service"] == "ebook-annotations"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
