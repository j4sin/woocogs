import json
from flask import Flask, request, render_template_string
from requests_oauthlib import OAuth1Session
from woocommerce import API

# Discogs OAuth setup
consumer_key = 'xxxx-your-OAsetup-key'
consumer_secret = 'xxxx-your-OAsetup-secret-key'
token_file = 'discogs_token.json'

try:
    with open(token_file, 'r') as file:
        tokens = json.load(file)
        access_token = tokens['access_token']
        access_token_secret = tokens['access_token_secret']
except FileNotFoundError:
    discogs = OAuth1Session(consumer_key, consumer_secret, callback_uri='oob')
    request_token_url = 'https://api.discogs.com/oauth/request_token'
    request_token_response = discogs.fetch_request_token(request_token_url)
    authorize_url = 'https://www.discogs.com/oauth/authorize'
    authorization_url = discogs.authorization_url(authorize_url, oauth_token=request_token_response['oauth_token'])
    print(f'Please go to the following URL to authorize the application: {authorization_url}')
    verifier_code = input('Please enter the verifier code: ')
    access_token_url = 'https://api.discogs.com/oauth/access_token'
    access_token_response = discogs.fetch_access_token(access_token_url, verifier=verifier_code)
    access_token = access_token_response['oauth_token']
    access_token_secret = access_token_response['oauth_token_secret']
    with open(token_file, 'w') as file:
        json.dump({'access_token': access_token, 'access_token_secret': access_token_secret}, file)

discogs = OAuth1Session(consumer_key, consumer_secret, access_token, access_token_secret)
url = 'https://api.discogs.com/database/search'

# WooCommerce API setup
wcapi = API(
    url="https://yourWooCommerceWebsite.com",
    consumer_key="xxx-your-woocommerce-key",
    consumer_secret="xxx-your-woocommerce-secret-key",
    timeout=30  # increase the timeout to 30 seconds
)

def create_product_in_woocommerce(product_data):
    response = wcapi.post("products", product_data)
    if response.status_code == 201:
        print(f"Product '{product_data['name']}' created successfully!")
    else:
        print(f"Failed to create product '{product_data['name']}'. Error: {response.text}")

def search_by_catalog_numbers(catalog_numbers, country='US', format='vinyl', released=None, sort='artist'):
    any_imported = False
    for catalog_number in catalog_numbers.split(','):
        params = {
            'catno': catalog_number.strip(),
            'country': country,
            'format': format,
            'type': 'release',
            'sort': sort
        }
        if released:
            params['released'] = released

        response = discogs.get(url, params=params)
        result = response.json()

        # Check if results are found
        if result['pagination']['items'] > 0:
            # Extract the first result
            record = result['results'][0]

            # Extract required fields
            title_and_artist = record['title']  # Assuming the title contains both artist and album name
            artist_name, album_title = title_and_artist.split(' - ', 1)  # Splitting by ' - ' to separate artist and album
            genre = ', '.join(record['genre'])
            main_image = record['cover_image']
            catalog_number = catalog_number.strip()
            release_year = record['year'] if 'year' in record else None
            image_alt_text_and_title = f"{album_title} Vinyl"

            # Prepare data for WooCommerce
            product_data = {
               'name': title_and_artist,
               'short_description': f"Artist: {artist_name}\nAlbum: {album_title}\nGenre: {genre}\nCatalog Number: {catalog_number}\nFormat: {format}\nRelease Year: {release_year}", # Moved to short description  # noqa: E501
               'images': [
        {
            'src': main_image,
            'name': image_alt_text_and_title,  # Set the image Title
            'alt': image_alt_text_and_title,  # Set the Alt Text
        }
    ],
               'status': 'draft',
               'meta_data': [{'key': 'artist_name', 'value': artist_name}], # Using meta_data for ACF custom field
               'manage_stock': True,  # Enable stock management
               'stock_quantity': 1,   # Set stock quantity to 1
               'in_stock': True,      # Mark the product as in stock
            }

            create_product_in_woocommerce(product_data)
            print(f"Import Complete for catalog number: {catalog_number.strip()}")  # Success message for each catalog number
            any_imported = True  # Set the flag to True if any catalog number is imported
        else:
            print(f"No results found for catalog number: {catalog_number.strip()}")  # Error message for each catalog number

    if any_imported:
        return 'Import successful! Visit your <a href="https://product-page-on-your-woocommerce-site-url.com">Products page</a> to review new imports.'
    else:
        return "No results found for all catalog numbers."


# Flask app setup
app = Flask(__name__)

# HTML template for the form with Bootstrap dark theme
template_html = '''

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
    <title>Catalog Importer</title>
    
<style>
    body {
        font-family: 'Courier New', monospace;
        background-color: #f4f4f4;
        color: #333;
    }
    .container {
        max-width: 480px; /* Mobile width */
    }
    #logo {
        display: block;
        margin: 20px auto;
        width: 300px; /* Logo width */
    }
</style>
<style>
        body {
            background-color: #343a40;
            color: #ffffff;
        }
        #success-message {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container mt-5"><img id="logo" src="https://i0.wp.com/vinyltavern.com/wp-content/uploads/2021/10/VinylTavernLogo-NEW-1.png" alt="Vinyl Tavern Logo">
        <h2 class="text-center">WooCogs: Discogs2WooCommerce</h2>
        <div id="success-message" class="{{ success_class }}">{{ success_message }}</div>
        <form action="/" method="post" enctype="multipart/form-data" class="mt-4">
            <div class="form-group">
                <label for="catalog_numbers">Catalog Numbers (comma-separated)</label>
                <input type="text" class="form-control" id="catalog_numbers" name="catalog_numbers" placeholder="Enter catalog numbers">
            </div>
            <div class="form-group">
    <label for="search_country">Search Country</label>
    <select class="form-control" id="search_country" name="search_country">
        {% for code, name in countries %}
        <option value="{{ code }}" {% if code == default_country %}selected{% endif %}>{{ name }}</option>
        {% endfor %}
    </select>
            </div>
            <div class="form-group">
                <label for="csv_file">Or Upload CSV File</label>
                <input type="file" class="form-control-file" id="csv_file" name="csv_file">
            </div>
            <button type="submit" class="btn btn-primary">Import</button>
        </form>
    </div>
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    success_message = "Import successful!"
    success_class = "d-none"
    countries = [
    ("US", "United States"),
    ("CA", "Canada"),
    ("GB", "United Kingdom"),
    ("DE", "Germany"),
    ("FR", "France"),
    ("AU", "Australia"),
    ("JP", "Japan"),
    ("BR", "Brazil"),
    ("IT", "Italy"),
    ("ES", "Spain"),
    # Add more countries as needed
                ]

    if request.method == 'POST':
        catalog_numbers = request.form.get('catalog_numbers')
        csv_file = request.files.get('csv_file')

        if catalog_numbers or csv_file:
            if csv_file:
                csv_content = csv_file.read().decode('utf-8')
                catalog_numbers = '\n'.join([line.split(',')[0] for line in csv_content.splitlines() if line])

            success_message = search_by_catalog_numbers(catalog_numbers)
            success_class = "alert alert-success" if success_message == 'Import successful!' else "d-none"

    return render_template_string(template_html, success_message=success_message, success_class=success_class, countries=countries)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

