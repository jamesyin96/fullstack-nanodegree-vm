from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem


engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                id_name_list = session.query(Restaurant).all()
                output = ""
                output += "<html><body>"
                output += "<a href='/restaurants/new'>add new restaurant</a>"
                for id_name in id_name_list:
                    output += "<p><b>%s</b>" % (id_name.name)
                    output += '    <a href="/restaurants/%s/edit">edit</a>' % (id_name.id)
                    output += '    <a href="/restaurants/%s/delete">delete</a><br/></p>' % (id_name.id)
                output += "</body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1> Add new restaurant </h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurants/new'><h2>Input new restaurant name:</h2><input name="newRestaurantName" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith("/edit"):
                restaurant_id = self.path.split("/")[2]
                restaurant_edit = session.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurant_edit != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1> Edit %s </h1>" % (restaurant_edit.name)
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % (restaurant_id)
                    output += "<h2>Input new restaurant name:</h2><input name='editRestaurantName' type='text' ><input type='submit' value='Submit'> </form>"
                output += "</body></html>"
                self.wfile.write(output)
                return
            if self.path.endswith("/delete"):
                restaurant_id = self.path.split("/")[2]
                restaurant_delete = session.query(Restaurant).filter_by(id=restaurant_id).one()
                if restaurant_delete != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output += "<html><body>"
                    output += "<h1> Are you sure to delete %s </h1>" % (restaurant_delete.name)
                    output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % (restaurant_id)
                    output += "<input type='submit' value='Yes'> </form>"
                    output += "<a href='/restaurants'>No</a>"
                output += "</body></html>"
                self.wfile.write(output)

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('newRestaurantName')
                    # create new restaurant and add to database
                    new_restaurant = Restaurant(name=messagecontent[0])
                    session.add(new_restaurant)
                    session.commit()

                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            if self.path.endswith("/edit"):
                restaurant_id = self.path.split("/")[2]
                restaurant_edit = session.query(Restaurant).filter_by(id=restaurant_id).one()
                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('editRestaurantName')
                    # create new restaurant and add to database
                    new_name = messagecontent[0]
                    restaurant_edit.name = new_name
                    session.add(restaurant_edit)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
            if self.path.endswith("/delete"):
                restaurant_id = self.path.split("/")[2]
                restaurant_delete = session.query(Restaurant).filter_by(id=restaurant_id).one()
                # delete restaurant from database
                session.delete(restaurant_delete)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print "^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
