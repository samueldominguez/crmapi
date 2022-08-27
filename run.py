from app import create_app

if __name__ == '__main__':
    try:
        app = create_app()
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000
        )
    except SystemExit:
        print("Debugger quit, please re-attach to continue debugging")
