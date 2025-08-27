from flask import Flask, request, jsonify
from typing import Dict, Any, Optional
import os
from ebook_annotations import (
    EbookAnnotationManager, MemoryAnnotationStorage, 
    EbookLocation, LocationType, Annotation, Bookmark
)

app = Flask(__name__)

# Initialize the annotation manager with memory storage
storage = MemoryAnnotationStorage()
annotation_manager = EbookAnnotationManager(storage)

def create_location_from_dict(data: Dict[str, Any]) -> EbookLocation:
    """Helper to create EbookLocation from request data"""
    return EbookLocation(
        type=LocationType(data["type"]),
        value=data["value"]
    )

@app.route('/api/library-items/<library_item_id>/annotations', methods=['POST'])
def create_annotation(library_item_id: str):
    """Create a new annotation (highlight or note)"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        annotation_type = data.get("type", "highlight")  # "highlight" or "note"
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        start_location = create_location_from_dict(data["start_location"])
        end_location = None
        if data.get("end_location"):
            end_location = create_location_from_dict(data["end_location"])
        
        if annotation_type == "note":
            annotation = annotation_manager.create_note(
                library_item_id=library_item_id,
                user_id=user_id,
                location=start_location,
                note=data.get("note", ""),
                text=data.get("text")
            )
        else:  # highlight
            annotation = annotation_manager.create_highlight(
                library_item_id=library_item_id,
                user_id=user_id,
                start_location=start_location,
                end_location=end_location,
                text=data.get("text"),
                color=data.get("color", "#ffff00")
            )
        
        return jsonify(annotation.to_dict()), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/library-items/<library_item_id>/annotations', methods=['GET'])
def get_annotations(library_item_id: str):
    """Get all annotations for a book"""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400
    
    annotations = annotation_manager.get_annotations_for_book(library_item_id, user_id)
    return jsonify({
        "annotations": [ann.to_dict() for ann in annotations]
    })

@app.route('/api/annotations/<annotation_id>', methods=['PUT'])
def update_annotation(annotation_id: str):
    """Update an annotation (add/edit note)"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        updates = {}
        if "note" in data:
            updates["note"] = data["note"]
        if "color" in data:
            updates["color"] = data["color"]
        
        annotation = annotation_manager.storage.update_annotation(annotation_id, updates)
        
        if not annotation:
            return jsonify({"error": "Annotation not found"}), 404
        
        return jsonify(annotation.to_dict())
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/annotations/<annotation_id>', methods=['DELETE'])
def delete_annotation(annotation_id: str):
    """Delete an annotation"""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400
    
    success = annotation_manager.delete_annotation(annotation_id, user_id)
    
    if success:
        return jsonify({"message": "Annotation deleted successfully"})
    else:
        return jsonify({"error": "Annotation not found or not authorized"}), 404

@app.route('/api/library-items/<library_item_id>/bookmarks', methods=['POST'])
def create_bookmark(library_item_id: str):
    """Create a new bookmark"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        location = create_location_from_dict(data["location"])
        
        bookmark = annotation_manager.create_bookmark(
            library_item_id=library_item_id,
            user_id=user_id,
            location=location,
            title=data.get("title", "Bookmark"),
            note=data.get("note")
        )
        
        return jsonify(bookmark.to_dict()), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/library-items/<library_item_id>/bookmarks', methods=['GET'])
def get_bookmarks(library_item_id: str):
    """Get all bookmarks for a book"""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400
    
    bookmarks = annotation_manager.get_bookmarks_for_book(library_item_id, user_id)
    return jsonify({
        "bookmarks": [bm.to_dict() for bm in bookmarks]
    })

@app.route('/api/bookmarks/<bookmark_id>', methods=['DELETE'])
def delete_bookmark(bookmark_id: str):
    """Delete a bookmark"""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400
    
    success = annotation_manager.delete_bookmark(bookmark_id, user_id)
    
    if success:
        return jsonify({"message": "Bookmark deleted successfully"})
    else:
        return jsonify({"error": "Bookmark not found or not authorized"}), 404

@app.route('/api/library-items/<library_item_id>/export', methods=['GET'])
def export_annotations_and_bookmarks(library_item_id: str):
    """Export all annotations and bookmarks for a book"""
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id parameter is required"}), 400
    
    export_data = annotation_manager.export_annotations(library_item_id, user_id)
    return jsonify(export_data)

@app.route('/api/library-items/<library_item_id>/import', methods=['POST'])
def import_annotations_and_bookmarks(library_item_id: str):
    """Import annotations and bookmarks for a book"""
    try:
        data = request.get_json()
        success = annotation_manager.import_annotations(data)
        
        if success:
            return jsonify({"message": "Import successful"})
        else:
            return jsonify({"error": "Import failed"}), 400
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "ebook-annotations"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
