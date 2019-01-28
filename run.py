from app import create_app
from app.models import Seed, Strain

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'Seed': Seed, 'Strain': Strain}

