from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurant"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                engine = create_engine('sqlite:///restaurantmenu.db')
                Base.metadata.bind = engine
                DBSession = sessionmaker(bind=engine)
                session = DBSession()
                id_name_list = session.query(Restaurant).all()
                output = ""
                output += "<html><body>"
                for id_name in id_name_list:
                    output += "<p><b>%s</b>" % (id_name.name)
                    output += '    <a href="/restaurant/%s/edit">edit</a>' % (id_name.id)
                    output += '    <a href="/restaurant/%s/delete">delete</a><br/></p>' % (id_name.id)
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
            if self.path.endswith("/restaurant/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                engine = create_engine('sqlite:///restaurantmenu.db')
                Base.metadata.bind = engine
                DBSession = sessionmaker(bind=engine)
                session = DBSession()
                id_name_list = session.query(Restaurant).all()
                output = ""
                output += "<html><body>"
                output += "<h1> Add new restaurant </h1>"
                output += '''<form method='POST' enctype='multipart/form-data' action='/restaurant/new'><h2>Input new restaurant name:</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(
                self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
            engine = create_engine('sqlite:///restaurantmenu.db')
            Base.metadata.bind = engine
            DBSession = sessionmaker(bind=engine)
            session = DBSession()
            output = ""
            output += "<html><body>"
            output += " <h2> Okay, new restaurant added </h2>"
            output += "<h1> %s </h1>" % messagecontent[0]
            new_restaurant = Restaurant(name=messagecontent[0])
            session.add(new_restaurant)
            session.commit()
            output += '''<form method='POST' enctype='multipart/form-data' action='/restaurant/new'><h2>Input new restaurant name:</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
            output += "</body></html>"
            self.wfile.write(output)
            print output
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
