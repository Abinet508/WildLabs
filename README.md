# WildLabs Web Scraper

This project is a web scraper designed to extract data from the WildLabs website. The scraper collects information about members and saves the data into an Excel file.

## Features

- Fetches the total number of pages to scrape.
- Collects links to individual member pages.
- Extracts detailed information from each member page.
- Saves the collected data into an Excel file.
- Uses multithreading to improve performance by concurrently fetching member information.
- Save the collected data into an Excel file named `wildlabs.xlsx`.

## Project Structure

- WildLabs:
    - README.md
    - requiremnts.txt
    - wildlabs_scraper.py
    - wildlabs.xlsx

## Requirements

- Python 3.6+
- Required Python packages (listed in `requiremnts.txt`)

## Setup

1. **Install Python**: Ensure that Python 3.6 or higher is installed on your system. You can download it from [python.org](https://www.python.org/downloads/).

2. **Install Required Packages**: Navigate to the `WildLabs` directory and install the required Python packages using the following command:

    ```sh
    pip install -r requiremnts.txt
    ```

## Usage

To run the web scraper, execute the following command in the 

WildLabs

 directory:

```sh
python wildlabs_scraper.py
```

## Output

The output Excel file will be saved in the 

WildLabs

 directory with the name `wildlabs.xlsx`. The file contains the following columns:

- LINK: The URL to the member's page.
- NAME: The name of the member.
- MEMBER_PHOTO: The URL to the member's photo.
- LOCATION: The location of the member.
- ORGANIZATION: The organization of the member.
- GROUP: The group of the member.
- SOCIAL: The social media links of the member.
- BIO: The biography of the member.
- LANGUAGES: The languages spoken by the member.

## Troubleshooting

If you encounter any issues while running the script, ensure that all required packages are installed and that you have an active internet connection. If the problem persists, please check the error messages for more details.

## Contact

For any questions or support, please contact me at:
Mail: `abinatmail@gmmail.com`
PHONE:`+251937875246`