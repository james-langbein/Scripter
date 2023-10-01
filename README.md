# Scripter (WIP)

Designed to remove all the hassle in managing scripts. The initial idea for Scripter occurred to me when I was first 
learning to be a DBA. 

It seemed like madness to me that all the DBAs that I knew were managing their scripts as simple text files in folders. 
That system has many paint points (for me) that I could see would be avoidable with the right well-designed application...
 - Having to navigate to a file every time you want to use the script in it.
 - Having to open the file to copy the contents.
 - Not being able to reference scripts in multiple categories without having multiple copies, one per folder.
 - Needing to remember which folder you put that script in that you last used 6 months ago.
 - Dealing with Microsoft Window's terribly slow search functionality.

Scripter takes all of these problems and attempts to remove those pain points. The main GUI consists of two parts, one 
part with the list of files in your script repository, and the second part being a preview of the currently selected file.
 - You can filter the list in real-time by using the search bar, on file contents as well as filenames. 
 - It's very fast - the search functionality has been tested on ~10,000 files without noticing any slowdown. 
 - As soon as you've found the file you want, there's a handy Copy button which puts the file's contents on the clipboard. 
 - You can safely edit the file's contents within Scripter without editing the actual file, then copy the edited file contents, and leave the original file untouched... or you can edit the file and save it to the
filesystem if desired.

This project is a work in progress due to family/time constraints.