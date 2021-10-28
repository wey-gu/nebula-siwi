from siwi import app

application = app = app.app

def siwi_api():
   application.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
