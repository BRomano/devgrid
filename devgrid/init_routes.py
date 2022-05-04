

def init_routes(app):
    from devgrid.temperature import temperature_bp
    app.register_blueprint(temperature_bp, url_prefix='/temperature')
