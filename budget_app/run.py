import os
from dotenv import load_dotenv


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    print("Attention: Fichier .env non trouvé. Certaines configurations pourraient manquer.")

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)