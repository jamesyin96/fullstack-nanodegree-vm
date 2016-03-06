from geocode import getGeocodeLocation
import json
import httplib2

import sys
import codecs
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)

foursquare_client_id = "PQ35OKRC2MEAUEHEQYP2DW2DRIWY4PGV3Q0ZXUSTPLJMQZD5"
foursquare_client_secret = "QVINGDLZWJTMB5LPLWQYEAWXXMFPVBSLEYK3OJQ1GUNRED25"


def findARestaurant(mealType, location):
    # 1. Use getGeocodeLocation to get the latitude and longitude coordinates o
    # f the location string.
    firstRestaurant = []
    (lat, lng) = getGeocodeLocation(location)
    # 2.  Use foursquare API to find a nearby restaurant with the latitude,
    # longitude, and mealType strings.
    url = ("https://api.foursquare.com/v2/venues/search?v=20160108"
           "&client_id=" + foursquare_client_id +
           "&client_secret=" + foursquare_client_secret +
           "&ll=" + str(lat) + "," + str(lng) +
           "&query=" + mealType +
           "&intent=browse&radius=800"
           )

    h = httplib2.Http()
    response, content = h.request(url, 'GET')
    results = json.loads(content)
    # 3. Grab the first restaurant
    restaurants = results['response']['venues']
    restaurantName = ""
    restaurantAddress = ""
    if len(restaurants):
        firstRestaurant = restaurants[0]
        restaurantName = firstRestaurant['name']
        restaurantAddress = firstRestaurant['location']['formattedAddress']
    # 4. Get a  300x300 picture of the restaurant using the venue_id (you can
    # change this by altering the 300x300 value in the URL or replacing it with
    # 'orginal' to get the original picture
    restaurantDetail = []
    photourl = ""
    if len(firstRestaurant) > 0:
        url2 = ("https://api.foursquare.com/v2/venues/" +
                firstRestaurant['id'] +
                "?v=20160108" +
                "&client_id=" + foursquare_client_id +
                "&client_secret=" + foursquare_client_secret
                )
        h = httplib2.Http()
        response, content = h.request(url2, 'GET')
        result = json.loads(content)
        restaurantDetail = result['response']['venue']
        photos = restaurantDetail['photos']['groups']
        # 5. Grab the first image
        # 6. If no image is available, insert default a image url
        if restaurantDetail['photos']['count'] == 0:
            photo = []
            photourl = 'http://bit.ly/1NvadKw'
        else:
            photo = photos[0]['items'][0]
            photourl = photo['prefix'] + '300x300' + photo['suffix']

    # 7. Return a dictionary containing the restaurant name, address, image url
    restaurantDict = {'Name': restaurantName,
                      'Address': restaurantAddress,
                      'Photo URL': photourl
                      }

    print restaurantDict

if __name__ == '__main__':
    findARestaurant("Pizza", "Tokyo, Japan")
    findARestaurant("Tacos", "Jakarta, Indonesia")
    findARestaurant("Tapas", "Maputo, Mozambique")
    findARestaurant("Falafel", "Cairo, Egypt")
    findARestaurant("Spaghetti", "New Delhi, India")
    findARestaurant("Cappuccino", "Geneva, Switzerland")
    findARestaurant("Sushi", "Los Angeles, California")
    findARestaurant("Steak", "La Paz, Bolivia")
    findARestaurant("Gyros", "Sydney Australia")
