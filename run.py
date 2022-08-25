from app import create_app
import os

if __name__ == '__main__':
    if os.getenv('ENV') == 'DEV':
        try:
            app = create_app()
            app.run(debug=True, host='0.0.0.0', port=5000)
        except:
            pass
