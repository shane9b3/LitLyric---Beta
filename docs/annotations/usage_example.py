#!/usr/bin/env python3
"""
LitLyric Annotations API Usage Example
Demonstrates complete annotation workflow for ebook reader integration
"""

import requests
import json
from datetime import datetime

def main():
    """Demonstrate the LitLyric annotation system"""
    
    base_url = "http://localhost:5000"
    library_item_id = "litlyric-demo-book"
    user_id = "demo-user"
    
    print("📚 LitLyric Annotations System Demo")
    print("=" * 45)
    
    # Health check
    try:
        response = requests.get(f"{base_url}/api/health")
        if response.status_code != 200:
            print("❌ API server not running. Start with: python server/annotations/annotation_api.py")
            return
        print("✅ Annotation API is ready")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Start the server first.")
        return
    
    # Demo 1: EPUB Highlighting with CFI
    print("\n📖 EPUB Annotation (CFI-based)")
    print("-" * 30)
    
    epub_highlight = {
        "user_id": user_id,
        "type": "highlight",
        "start_location": {
            "type": "cfi",
            "value": "/6/4[chap01ref]!/4[body01]/10[para05]/3:10"
        },
        "end_location": {
            "type": "cfi",
            "value": "/6/4[chap01ref]!/4[body01]/10[para05]/3:45"
        },
        "text": "LitLyric's integration with Readium enables precise CFI-based positioning for EPUB annotations.",
        "color": "#ffff00"
    }
    
    response = requests.post(
        f"{base_url}/api/library-items/{library_item_id}/annotations",
        json=epub_highlight
    )
    
    if response.status_code == 201:
        highlight = response.json()
        print(f"✅ Created EPUB highlight: {highlight['id'][:8]}...")
        print(f"   CFI Location: {highlight['start_location']['value']}")
        print(f"   Text: \"{highlight['text'][:60]}...\"")
    
    # Demo 2: PDF Note with Page Number
    print("\n📄 PDF Annotation (Page-based)")
    print("-" * 30)
    
    pdf_note = {
        "user_id": user_id,
        "type": "note",
        "start_location": {
            "type": "page",
            "value": 42
        },
        "note": "This page demonstrates PDF annotation compatibility with LitLyric's page-based positioning system."
    }
    
    response = requests.post(
        f"{base_url}/api/library-items/{library_item_id}/annotations",
        json=pdf_note
    )
    
    if response.status_code == 201:
        note = response.json()
        print(f"✅ Created PDF note: {note['id'][:8]}...")
        print(f"   Page: {note['start_location']['value']}")
        print(f"   Note: \"{note['note'][:60]}...\"")
    
    # Demo 3: Bookmark for Navigation
    print("\n🔖 Bookmark Creation")
    print("-" * 20)
    
    bookmark_data = {
        "user_id": user_id,
        "location": {
            "type": "cfi",
            "value": "/6/4[chap03ref]!/4[body01]/2[para01]/1:0"
        },
        "title": "Chapter 3: Android Integration",
        "note": "Implementation details for LitLyric mobile app"
    }
    
    response = requests.post(
        f"{base_url}/api/library-items/{library_item_id}/bookmarks",
        json=bookmark_data
    )
    
    if response.status_code == 201:
        bookmark = response.json()
        print(f"✅ Created bookmark: {bookmark['title']}")
        print(f"   Location: {bookmark['location']['value']}")
    
    # Demo 4: Retrieve All Data
    print("\n📊 Data Retrieval")
    print("-" * 17)
    
    # Get annotations
    response = requests.get(
        f"{base_url}/api/library-items/{library_item_id}/annotations",
        params={"user_id": user_id}
    )
    
    if response.status_code == 200:
        annotations = response.json()["annotations"]
        print(f"✅ Retrieved {len(annotations)} annotations")
        
        for i, ann in enumerate(annotations, 1):
            location_type = ann['start_location']['type'].upper()
            location_value = ann['start_location']['value']
            print(f"   {i}. {location_type}: {location_value}")
    
    # Get bookmarks  
    response = requests.get(
        f"{base_url}/api/library-items/{library_item_id}/bookmarks",
        params={"user_id": user_id}
    )
    
    if response.status_code == 200:
        bookmarks = response.json()["bookmarks"]
        print(f"✅ Retrieved {len(bookmarks)} bookmarks")
        
        for i, bm in enumerate(bookmarks, 1):
            print(f"   {i}. {bm['title']}")
    
    # Demo 5: AudioBookShelf Sync Export
    print("\n🔄 AudioBookShelf Sync Export")
    print("-" * 30)
    
    response = requests.get(
        f"{base_url}/api/library-items/{library_item_id}/export",
        params={"user_id": user_id}
    )
    
    if response.status_code == 200:
        export_data = response.json()
        print("✅ Export successful for AudioBookShelf sync:")
        print(f"   Library Item: {export_data['library_item_id']}")
        print(f"   Annotations: {len(export_data['annotations'])}")
        print(f"   Bookmarks: {len(export_data['bookmarks'])}")
        print(f"   Export Time: {export_data['exported_at']}")
        
        # Save export file
        filename = f"litlyric_annotations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"   Saved to: {filename}")
    
    print("\n🎉 LitLyric Annotations Demo Complete!")
    print("\nKey Integration Points:")
    print("• Compatible with LitLyric v0.6.1 EbookLocation format")
    print("• Supports Readium CFI positioning for EPUB files")
    print("• Handles page-based positioning for PDF files")
    print("• Ready for AudioBookShelf server synchronization")
    print("• Designed for Android app integration")
    
    print("\nNext Steps:")
    print("1. Integrate API client into LitLyric Android app")
    print("2. Add annotation UI to LitLyricReaderFragment")
    print("3. Implement sync with AudioBookShelf server")
    print("4. Test with real ebook files and user scenarios")

if __name__ == "__main__":
    main()
