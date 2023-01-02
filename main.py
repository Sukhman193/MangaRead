# Import requests for the http requests
import requests
# BeautifulSoup for parsing the html 
from bs4 import BeautifulSoup
# import os to utilize operating system commands
import os
# import tqdm for user friendly progress bar
from tqdm import tqdm


class Validation:
    """
    Validation class
    """
    def isTitleValid(title):
        """
        Check if the title is valie
        @param title - Title of the manga name entered by the user
        @return True if the title is valid, otherwise return False
        """
        return len(title) < 20 and len(title) > 2

    def isOptionValid(option, min, max):
        """
        Check if an option is valid or not
        @param option - Option selected by theuser
        @param min - Minimum number for the validity of the option, This value is inclusive
        @param max - Maximum number for the validity of the option, This value is exclusive
        @returns True if the option is valid, otherwise it returns false
        """
        # Check if the option is a number
        if not option.isdigit():
            return False
        # Get the integer of the option
        intOption = int(option)
        # Check if the option is between the min value and the max value
        return intOption >= min and intOption < max


class Manga:
    """
    Manga class 
    @param name: Name of the manga
    @param url: URL of the mange
    """
    def __init__(self, name, url):
        # name of the manga
        self.name = name
        # url of the main page of the manga
        self.url = url
        # Chapters of the manga
        self.chapters = []


class Chapter: 
    """
    Chapter class for the manga
    """
    def __init__(self, number, url):
        # Chapter number
        self.number = number
        # Chapter url
        self.url = url
        # Images for the chapter
        self.images = []


class DisplayOptions:
    def getMangaFromUser(self):
        # Clear screen
        clearScreen()
        # Title of the screen
        print("MangaReader Downloader\n")
        # Prompt for the manga title
        print("Enter the name of the manga to download?", end="\t")
        # input for the manga title
        title = input()
        print()
        # Validate the title of the manga
        while not Validation.isTitleValid(title=title):
            print("Title must be between 2 and 20 characters", end="\t")
            title = input()

        return title


    def selectMangaOptions(self, mangas):
        # Clear the screen
        clearScreen()
        # Pritn the title of the screen
        print("Select one of the following options")
        # Display the exit option
        print("1. Exit")
        # Start iterating starting at 2
        i = 2
        # Iterate over all the mangas
        # Add 2 to the lenght because we start from 2
        while i < len(mangas) + 2:
            # Print the name of the manga for the user selection
            print(f"{i}. {mangas[i-2].name}")
            # Increment the value of the count
            i += 1
        # Get the input of the option selected by the user
        option = input()
        # Validate the option selection
        while not Validation.isOptionValid(option=option, min=1, max=len(mangas)-1):
            # Display the error message
            print("Please make a valid option selection")
            # Wait for the user input
            option = input()

        # if the user wants to exit than return
        if(option == "1"):
            return
        else:
            # Get the index of the manga the user selected
            index = int(option)-2
            # Return the manga selected by the user
            return mangas[index]


    def selectMangaChapter(self, manga):
        # Clear the screen for the user
        clearScreen()
        # Select an options
        print("Select one of the following options\n")
        # Display default options
        print("1. Download all chapters")
        print("2. Download from last chapter")
        print("3. Specify chapter") 
        # Wait for user input
        option = input()
        # Validate the user's input
        while not Validation.isOptionValid(option=option, min=1, max=4):
            # Display friendly message
            print("Please make a valid selection")
            # Ask for the input again
            option = input()

        # If the user wants to download all the chapters return -1
        if option == "1": 
            return -1
        elif option == "2":
            return -2
        else:
            # Let the user select the chapter to download
            print("Select the chapter")
            # Start the iteration at 1
            i = 1
            # Iterate over all the chapters inside the manga
            while i < len(manga.chapters) + 1:
                # Print the chapter number
                print(f"{i}. {manga.chapters[i - 1].number}")
                # increment by one the iterating value
                i += 1
            # Get the input from the user
            option = input()
            # Validate the options selection for the user's input
            while not Validation.isOptionValid(option=option, min=1, max=len(manga.chapters) + 1): 
                # Display a friendly message to the user
                print("Please make a valid selection")
                # get user's input again
                option = input()
            # Return the index of the manga chapter to download
            return int(option) - 1


# Base url for the mangapill website
mangaPillBaseUrl = "https://mangapill.com"

def getPageSoap(url):
    """
        Get the soap of a page.
        @param `url` - Url of the page to web scrape
        @returns soap of the scraped page
    """
    # Make the request
    r = requests.get(url)
    # get the soap by parsing the data
    soap = BeautifulSoup(r.content, 'html.parser')

    # Return the soap
    return soap


def getMangaNames(title):
    # Replace all spaces with a + sign
    formattedTitle = title.replace(" ", "+")
    # Get the soap for the searched manga
    soap = getPageSoap(f"{mangaPillBaseUrl}/quick-search?q={formattedTitle}")
    # Get all the names for the searched manga
    mangaNames = soap.find_all("div", class_="font-black")
    # urls of the screen
    mangaURL = soap.find_all("a", class_="grid-cols-1 bg-card rounded p-3")
    # array of mangas to return
    mangas = []
    # Count of all the manga screens
    count = 0
    while count < len(mangaNames):
        # fill in all the manga that we searched for
        name = mangaNames[count].text
        url = mangaURL[count].get("href")
        # Add the manga to the array
        mangas.append(Manga(name=name, url=url))
        # Increment the count
        count += 1

    # Return the manga
    return mangas


def fillMangaChapters(manga: Manga):
    # Get the soap of the manga info page
    soap = getPageSoap(url=f"{mangaPillBaseUrl}{manga.url}")
    # Find all the chapters in the manga
    mangaChapters = soap.find_all("a", class_="border border-border p-1 hover:bg-brand hover:text-white")
    for chapter in mangaChapters:
        manga.chapters.append(Chapter(number=chapter.text, url=chapter.get("href")))


def fillChapterContent(chapter: Chapter):
    # Get the soap of the chapter images
    soap = getPageSoap(url=f"{mangaPillBaseUrl}{chapter.url}")
    # Get the images of the chapter
    chapterImages = soap.find_all("img", class_="js-page")
    # Fill in the chapters
    for image in chapterImages:
        # print(image.get("data-src"))
        chapter.images.append(image.get("data-src"))


def getChapterImageNumber(url):
    # return the last part of the url
    return url.split("/")[-1].split("?")[0]


def saveMangaChapter(name, chapter: Chapter):
    """
    Locally save the chapter of the manga
    @param name - Name of the manga to save
    @param chapter - Chapter of the manga to save
    """
    # Create the manga directory
    createFolder(name=name)
    # Create chapter folder 
    createFolder(name=chapter.number, location=name)
    # Download all the chapters
    for imageUrl in tqdm(chapter.images, total=len(chapter.images)):
         # Save the image to a filee
        filepath = f"./{name}/{chapter.number}/{getChapterImageNumber(url=imageUrl)}"
        # If the file already exists, there is no need for the request
        if os.path.exists(filepath): 
            continue

        # make the image request
        image = requests.get(imageUrl)

        with open(filepath, 'wb') as f:
            # Write the content of the image
            f.write(image.content)


def createFolder(name, location=""):
    """
    Create a directory for the manga if it doesn't already exist
    @param name - Name of the folder to create
    @param location - Main location for the folder creation
    """
    try:
        # Get the index of the directory
        os.listdir(f"./{location}").index(name)
    except ValueError:
        if location == "":
            # If an error occurs than create the directory
            os.system(f"mkdir './{name}'")
        else: 
            os.system(f"mkdir './{location}/{name}'")
    

def main():
    # Get instance of the display options
    displayOptions = DisplayOptions()
    # Get the title of the manga from the user
    title = displayOptions.getMangaFromUser()
    # Get all the searched up mangas
    mangas = getMangaNames(title=title)
    # display the options for the mangas
    manga = displayOptions.selectMangaOptions(mangas=mangas)
    # Fill the content of the chapters
    fillMangaChapters(manga)
    # Check if the instance is of type of Manga
    if not isinstance(manga, Manga):
        return
    # Get the chapter that needs to be downloaded
    chapterToDownload = displayOptions.selectMangaChapter(manga=manga)

    # Check if we are starting from the beginning
    if(chapterToDownload == -2):
        try:
            chapterIndex = manga.chapters.index(findIndexForMangaChapter(manga=manga))
            while chapterIndex < len(manga.chapters):
                # Get the chapter to download
                chapter = manga.chapters[chapterIndex]
                #fill the chapter and download it
                fillAndSaveChapter(name=manga.name, chapter=chapter)
                # Increment the index of the chapter
                chapterIndex -= 1
        except FileNotFoundError:
            # Display friendly message
            print("Manga has not been downloaded previously, starting from chapter 1")
            # set the value for the chapterToDownload so that it starts downloading all the chapters
            chapterToDownload = -1
            
    # If the user wants to donwload all the chapters
    if(chapterToDownload == -1):
        # Reverse the chapter array so it starts from the first chapter
        manga.chapters.reverse()
        # Print all the chapters
        for chapter in manga.chapters:
            # Get the chapters and save them
            fillAndSaveChapter(manga.name, chapter=chapter)
    else:
        chapter = manga.chapters[chapterToDownload]
        # Get the images for the chapter and save them
        fillAndSaveChapter(manga.name, chapter=chapter)


def findIndexForMangaChapter(manga):
     # Start from the first element inside the os library
        chapterToSearch = os.listdir(f"./{manga.name}")[0]
        for chapter in manga.chapters:
            # look for the searched chapter
            if(chapter.number == chapterToSearch):
                # return the matching chapter
                return chapter
        # This should never happen, unless the directory has been tempered with
        raise FileNotFoundError

def fillAndSaveChapter(name, chapter):
    """
    This function is a helper function to retrieve
    the images from the chapter and download them
    """
    # Add the images to the chapter
    fillChapterContent(chapter=chapter)
    # Display which chapter is being currently downloaded
    print(f"{name}: Downloading chapter {chapter.number}")
    # Download the chapter
    saveMangaChapter(name, chapter=chapter)

def clearScreen():
    """
    Clear the screen for user experience
    """
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")

if __name__ == "__main__":
    main()