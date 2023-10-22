###
# Main application interface
###

from src import create_app

# create the app object
app = create_app()

if __name__ == '__main__':
    # debug mode for hot reloading)
    # this app will be bound to port 4000
    app.run(debug=True, host='0.0.0.0', port=4000)