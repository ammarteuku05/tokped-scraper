# Tokopedia Scraper Project
This project is a simple project to get the top 100 results of a certain search keyword to be extracted as csv file.
Usage: simply clone this project and install the dependencies and run:
```
python tokopedia-scraper.py
```
and then type in your search keyword when prompted. This will generate a csv file titled "Top 100 <your keyword>.csv" file in the same directory as this file itself.

The structure of the csv is like this (visualized in table view for easier read):
| Product Name | Product Image Link | Product Price | Product Rating | Product Average Rating | Product Description | Merchant Name |
| ------------ | ------------------ | ------------- | -------------- | ---------------------- | ------------------- | ------------- |
| sample data  | sample data        | sample data   | sample data    | sample data            | sample data         | sample data   |

**Note**: Currently the description doesn't work, can see in the code inline documentation for the explanation and possible improvements.
  
**Side Note**: I've added sample data called "Top 100 handphone.csv" for reference.
