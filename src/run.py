from trackyr import create_app
import lib.core.modules as modules

app = create_app()

modules.generate_sources_in_db()

if __name__ == '__main__':
    app.run(debug=True)