import os
import sys

# Permite importar metar.py, clientes.py etc. a partir da pasta tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
