from trackyr import create_app
import lib.core.modules as modules

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
    modules.generate_sources_in_db()