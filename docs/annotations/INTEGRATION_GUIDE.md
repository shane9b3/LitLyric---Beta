# Android Integration Guide

## Overview
Step-by-step guide for integrating the annotation system into LitLyric's Android app.

## Prerequisites
- LitLyric v0.6.1+ with ebook reader
- Existing `EbookRepository`, `LitLyricReaderFragment`, and `UserPreferencesRepository`
- AudioBookShelf API client setup

## Phase 1: Core Integration

### 1. Add API Client Methods

#### AudiobookshelfApi.kt
```kotlin
interface AudiobookshelfApi {
    // Existing methods...
    
    @POST("library-items/{id}/annotations")
    suspend fun createAnnotation(
        @Path("id") libraryItemId: String,
        @Body request: CreateAnnotationRequest
    ): Annotation
    
    @GET("library-items/{id}/annotations")
    suspend fun getAnnotations(
        @Path("id") libraryItemId: String,
        @Query("user_id") userId: String
    ): AnnotationsResponse
    
    @PUT("annotations/{id}")
    suspend fun updateAnnotation(
        @Path("id") annotationId: String,
        @Body request: UpdateAnnotationRequest
    ): Annotation
    
    @DELETE("annotations/{id}")
    suspend fun deleteAnnotation(
        @Path("id") annotationId: String,
        @Query("user_id") userId: String
    ): ResponseBody
    
    @POST("library-items/{id}/bookmarks")
    suspend fun createBookmark(
        @Path("id") libraryItemId: String,
        @Body request: CreateBookmarkRequest
    ): Bookmark
    
    @GET("library-items/{id}/bookmarks")
    suspend fun getBookmarks(
        @Path("id") libraryItemId: String,
        @Query("user_id") userId: String
    ): BookmarksResponse
}
2. Add Data Models
AnnotationModels.kt
@Serializable
data class Annotation(
    val id: String,
    val libraryItemId: String,
    val userId: String,
    val startLocation: EbookLocation,
    val endLocation: EbookLocation? = null,
    val text: String? = null,
    val note: String? = null,
    val color: String = "#ffff00",
    val createdAt: String,
    val updatedAt: String
)

@Serializable
data class Bookmark(
    val id: String,
    val libraryItemId: String,
    val userId: String,
    val location: EbookLocation,
    val title: String,
    val note: String? = null,
    val createdAt: String
)

@Serializable
data class CreateAnnotationRequest(
    val userId: String,
    val type: String, // "highlight" or "note"
    val startLocation: EbookLocation,
    val endLocation: EbookLocation? = null,
    val text: String? = null,
    val note: String? = null,
    val color: String = "#ffff00"
)

@Serializable
data class CreateBookmarkRequest(
    val userId: String,
    val location: EbookLocation,
    val title: String,
    val note: String? = null
)

@Serializable
data class AnnotationsResponse(
    val annotations: List<Annotation>
)

@Serializable
data class BookmarksResponse(
    val bookmarks: List<Bookmark>
)
3. Extend EbookRepository
EbookRepository.kt
class EbookRepository @Inject constructor(
    private val api: AudiobookshelfApi,
    // ... existing dependencies
) {
    // ... existing methods
    
    suspend fun createAnnotation(
        libraryItemId: String,
        userId: String,
        type: String,
        startLocation: EbookLocation,
        endLocation: EbookLocation? = null,
        text: String? = null,
        note: String? = null,
        color: String = "#ffff00"
    ): Result<Annotation> {
        return try {
            val request = CreateAnnotationRequest(
                userId = userId,
                type = type,
                startLocation = startLocation,
                endLocation = endLocation,
                text = text,
                note = note,
                color = color
            )
            val annotation = api.createAnnotation(libraryItemId, request)
            Result.success(annotation)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getAnnotations(
        libraryItemId: String,
        userId: String
    ): Result<List<Annotation>> {
        return try {
            val response = api.getAnnotations(libraryItemId, userId)
            Result.success(response.annotations)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun createBookmark(
        libraryItemId: String,
        userId: String,
        location: EbookLocation,
        title: String,
        note: String? = null
    ): Result<Bookmark> {
        return try {
            val request = CreateBookmarkRequest(
                userId = userId,
                location = location,
                title = title,
                note = note
            )
            val bookmark = api.createBookmark(libraryItemId, request)
            Result.success(bookmark)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    suspend fun getBookmarks(
        libraryItemId: String,
        userId: String
    ): Result<List<Bookmark>> {
        return try {
            val response = api.getBookmarks(libraryItemId, userId)
            Result.success(response.bookmarks)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
Phase 2: Reader UI Integration
1. Add to ReaderViewModel
ReaderViewModel.kt
class ReaderViewModel @AssistedInject constructor(
    // ... existing parameters
    private val ebookRepository: EbookRepository
) : ViewModel() {
    
    // ... existing code
    
    private val _annotations = MutableStateFlow<List<Annotation>>(emptyList())
    val annotations: StateFlow<List<Annotation>> = _annotations.asStateFlow()
    
    private val _bookmarks = MutableStateFlow<List<Bookmark>>(emptyList())
    val bookmarks: StateFlow<List<Bookmark>> = _bookmarks.asStateFlow()
    
    private val _showAnnotationMenu = MutableStateFlow(false)
    val showAnnotationMenu: StateFlow<Boolean> = _showAnnotationMenu.asStateFlow()
    
    fun loadAnnotations() {
        viewModelScope.launch {
            libraryItem.value?.let { item ->
                currentUser.value?.let { user ->
                    ebookRepository.getAnnotations(item.id, user.id)
                        .onSuccess { annotations ->
                            _annotations.value = annotations
                        }
                        .onFailure { error ->
                            // Handle error
                        }
                }
            }
        }
    }
    
    fun onTextSelected(selection: TextSelection) {
        _showAnnotationMenu.value = true
    }
    
    fun createHighlight(color: String) {
        viewModelScope.launch {
            // Implementation for creating highlights
            loadAnnotations() // Refresh
            _showAnnotationMenu.value = false
        }
    }
    
    fun createBookmark(title: String, note: String? = null) {
        viewModelScope.launch {
            // Implementation for creating bookmarks
            loadBookmarks() // Refresh
        }
    }
    
    private fun loadBookmarks() {
        viewModelScope.launch {
            libraryItem.value?.let { item ->
                currentUser.value?.let { user ->
                    ebookRepository.getBookmarks(item.id, user.id)
                        .onSuccess { bookmarks ->
                            _bookmarks.value = bookmarks
                        }
                }
            }
        }
    }
}

data class TextSelection(
    val text: String,
    val startLocation: EbookLocation,
    val endLocation: EbookLocation
)
2. Update LitLyricReaderFragment
LitLyricReaderFragment.kt
class LitLyricReaderFragment : Fragment() {
    
    // ... existing code
    
    private fun setupAnnotationHandling() {
        // Add text selection listener to Readium navigator
        navigator.listener = object : Navigator.Listener {
            override fun onTextSelected(selection: Selection) {
                val textSelection = TextSelection(
                    text = selection.text,
                    startLocation = selection.locator.locations.cfi?.let { 
                        EbookLocation(LocationType.CFI, it) 
                    } ?: EbookLocation(LocationType.PAGE, selection.locator.locations.position ?: 0),
                    endLocation = selection.endLocator?.locations?.cfi?.let {
                        EbookLocation(LocationType.CFI, it)
                    }
                )
                viewModel.onTextSelected(textSelection)
            }
        }
        
        // Observe annotation menu state
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.showAnnotationMenu.collect { show ->
                if (show) {
                    // Show annotation menu
                }
            }
        }
        
        // Load existing annotations
        viewModel.loadAnnotations()
    }
}
Phase 3: Testing
Unit Tests
class AnnotationRepositoryTest {
    
    @Test
    fun `createAnnotation returns success for valid input`() = runTest {
        // Mock API response
        val annotation = createTestAnnotation()
        coEvery { api.createAnnotation(any(), any()) } returns annotation
        
        val result = repository.createAnnotation(
            libraryItemId = "test-book",
            userId = "test-user", 
            type = "highlight",
            startLocation = EbookLocation(LocationType.CFI, "/6/4[chap01]!/4/2/1:10")
        )
        
        assertTrue(result.isSuccess)
        assertEquals(annotation, result.getOrNull())
    }
}