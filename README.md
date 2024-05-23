# woocogs
Discogs to WooCommerce Import

This is a simple script that allows you to pull data from Discogs into your WooCommerce vinyl store. You can enter catalog ids manually or upload a CSV file (simple file with catalog ids separated by commas). I run this on my local machine. Requires Python & Flask

This does not sync your personal catalog directly with WooCommerce.

<strong>To Get Started:</strong>

You'll need to update the woocogs.py file with your Discogs and WooCommerce api information.  

From Discogs you'll need:<br> 
  - OAuth Keys (consumer & secret)
  - Access Tokens (access & secret)
    - The access tokens are generated the first time you run the app.  You will get a notice to visit a private Discogs url to get a code for verification.  Once you have that code a JSON file for the Access tokens will be generated.

From WooCommerce you'll need:<br>
  - Site URL
  - API Keys (Consumer & Secret)
<br><br>

<strong>Updating the files:</strong>
  - woocogs.py<br>
    - Update the Discogs OAuth setup with your keys (consumer_key & consumer_secret)
    - Update the WooCommerce API setup with your website url and keys (consumer_key and consumer_secret)
  - discogs_token.json<br>
    - Generated on first run of app. You should not need to verify again or edit this file.<br>

What is the app pulling from Discogs?<br>
  - Album Title 
  - Album Artist
  - Album Genre
  - Album Cover (main image used on Discogs)
  - Album Catalog Number
  - Album Release Year
<br>

In WooCommerce a new product is created. The product is pre-populated with:<br>
  - Album Name 
  - Album Artist
  - Short Description: (pulls in a few fields for SEO purposes: Artist, Album, Genre, Catalog number, Format, Release year)
  - Main Image (the main image is also renamed for SEO purposes using the name of the album)
  - Status: Draft Mode (I do this so I can review before pushing each one live)
  - Meta Data: Artist Name (this is a drop down so I can quickly access a specific artist or group them later. I set this up using a custom field via ACF)
  - Stock: True (enables stock management)
  - Stock Quantity: defaults to 1
  - In Stock: True (marks the product as in stock)<br><br>

For the front end I'm using Flask and a simple bootstrap dark theme. The html template is part of the woocogs.py file. From there you can update the logo, page heading, text, add additional countries to the drop down search, change colors, etcs...<br><br>

There isn't a working 'Success Message' on the web interface. There is a success message generated in the command terminal. I did attempt to add a success message but never went back to debug.

I hope this is helpful. It is worth noting that I am NOT a programmer and this is my first submission to Github. I'll try to answer and help as I can, I wrote this a few yrs back but it's still working great (as of May 2024).


  
