# LitLyric---Beta
Beta page for LitLyric an Android AudioBookServer client

Application Pages Overview
This document provides a detailed overview of each page within the LitLyric application.

# 1. Login Screen
![Alt text](/images/Login-SSO.png?raw=true "Login SSO")
The Login Screen serves as the entry point for users to access their Audiobookshelf server. It supports both traditional username/password authentication and Single Sign-On (SSO) via OAuth2 for servers that have it enabled.

Key Features:

Server URL Input: Users must first enter the URL of their Audiobookshelf server. The app validates the URL by pinging the server and indicates whether the connection is successful. A "Skip server ping check" option is available for users who wish to bypass this validation step.

Authentication Methods:

Username/Password: Standard input fields for username and password.

SSO Login: An SSO button becomes available if the server supports OpenID. This option opens a custom Chrome tab for the user to complete the authentication process securely.

Remember Me: Users can opt to have their server URL and username pre-filled on subsequent launches for faster access.

Credential Management: If "Remember Me" is enabled, users can clear their saved credentials from the account screen.

# 2. Main Screen (Home)
![Alt text](/images/HomeScreen.png?raw=true "Home Screen")
The Main Screen is the central hub of the application, providing a personalized and dynamic overview of the user's library content.

Key Features:

Dynamic Library Selection: A top bar allows users to switch between their available libraries (e.g., audiobooks, podcasts). The selected library's icon and name are displayed, and tapping it opens a modal bottom sheet with a list of all libraries to choose from.

Integrated Search: The top bar also functions as a search bar. Tapping it navigates the user to the dedicated Search Screen for the currently selected library.

Personalized Content Sections: The main content area is organized into customizable sections:

Continue Listening: A prominent horizontal pager displays items the user is currently listening to, showing progress and time remaining.

Customizable Shelves: Users can add, remove, and reorder various shelves like "Discover," "Recently Added," "Continue Series," and "Newest Authors" using a scrollable chip row. This allows for a highly tailored home screen experience.

![Alt text](/images/Customize.png?raw=true "Customize")

Navigation Drawer: Accessible from the top bar, the drawer provides quick access to other app pages, including Account, User Stats, Downloads, and Settings, as well as a Logout button.

Pull-to-Refresh: Users can refresh the content of the current library by pulling down from the top of the screen.

# 3. Item Details Screen
![Alt text](/images/ItemDetails.png?raw=true "Item Details")
This screen provides a comprehensive view of a single audiobook or podcast, offering playback controls, metadata, and related content.

Key Features:

Detailed Information: Displays the item's cover art, title, author, narrator, series information, duration, and a full description.

Playback Controls: A prominent play/pause button allows users to start or resume listening. The app also includes a Download button for offline access and a "More" menu with additional options.

Progress Tracking: Shows the user's listening progress, including a "Finished" indicator if the book is completed and the date of completion.

Action Menu: The "More" menu provides options to:

Mark as Finished: Manually mark the item as complete.

Discard Progress: Remove all listening progress for the item.

Delete Local Item: If the item is downloaded, this option appears to remove it from the device's storage.

Series Information: If the item is part of a series, a dedicated section displays other books in the series, allowing for easy navigation between related content.

Metadata Display: Includes expandable sections for Chapters and Audio Files, and displays genres and tags associated with the item.

# 4. Author and Series Screens
![Alt text](/images/AuthorSeries.png?raw=true "Author and Series screens")
These pages help users discover and explore content by author or series.

Author Screen:

Displays the author's image, name, and a biographical description.

Lists all books and series by that author available in the user's library, organized for easy Browse.

Series Screen:

Shows a cover art collage of the books in the series.

Lists all books in the series in their correct order, with their title, publication year, and duration.

# 5. Podcast Screens
![Alt text](/images/Podcast.png?raw=true "Podcasts")
The app includes dedicated screens for discovering and listening to podcasts.

Podcast Details Screen:

Displays the podcast's cover art, title, and description.

Lists all available episodes in reverse chronological order, with options to play or download each one.

Podcast Episode Details Screen:

Provides detailed information about a single episode, including its title, description, publication date, and duration.

Features prominent Play and Download buttons, along with a "More" menu for actions like "Mark as Finished" and "Discard Progress".

# 6. Player Screen
![Alt text](/images/Player.png?raw=true "Player screen")
The Player Screen is a modal sheet that appears when media is playing, providing a rich, interactive playback experience.

Key Features:

Full-Screen Interface: Accessible by tapping the Mini Player, it expands to a full-screen view with large cover art and detailed playback information.

Advanced Playback Controls:

Seek Bar: A custom wavy progress indicator that allows users to scrub through the track.

Skip Controls: Buttons to skip forward and backward by user-defined intervals (e.g., 15, 30 seconds).

Chapter Navigation: Buttons to skip to the next or previous chapter.

Additional Features:

Playback Speed: Adjust the playback speed from 0.5x to 2.5x.

Sleep Timer: Set a timer to automatically pause playback after a certain duration or at the end of the current chapter.

Chapter List: View a full list of chapters and jump to any chapter.

Source Indicator: An icon indicates whether the media is streaming from the server or playing from a local download.

Seamless Local Playback Switching: If a user starts streaming an audiobook and decides to download it for offline listening, the app will automatically switch to the local version once the download is complete. This process is seamless and does not interrupt the listening experience. The player saves the current position, sends a final progress update to the server, and then immediately resumes playback from the downloaded file.

# 7. Downloads Screen
![Alt text](/images/Downloads.png?raw=true "Downloads screen")
The Downloads Screen allows users to manage all their offline content in one place.

Key Features:

Download Queue: Displays any downloads that are currently in progress, showing their status (e.g., Downloading, Paused, Failed) and progress percentage.

Downloaded Books: Lists all audiobooks and podcast episodes that have been successfully downloaded, with options to play or delete each item.

Storage Information: Provides a summary of the total space used by downloads and the free space remaining on the device.

Bulk Actions: Includes an option to delete all downloaded content at once to free up space.

# 8. Settings and Account Screens
![Alt text](/images/Settings.png?raw=true "Settings screen")
These screens provide options for customizing the app and managing the user's account.

Settings Screen:

Playback: Configure playback speed, skip lengths, and the default behavior of the progress bar (chapter vs. total book progress).

Sleep Timer: Set the default duration for the sleep timer and whether it should wait for the end of a chapter.

Account Screen:

Account Information: Displays the user's username and the server they are connected to.

Login Preferences: Manage the "Remember Me" setting.

App Information: Shows the current app version and the server version.
