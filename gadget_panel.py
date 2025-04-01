from flask import Flask, render_template, jsonify, request
import subprocess
import os
import re

app = Flask(__name__)

# Directorio raíz del proyecto
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def clean_ansi(text):
    """Eliminar códigos ANSI"""
    ansi_pattern = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_pattern.sub('', text)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/rules')
def get_rules():
    """Obtener reglas del Makefile"""
    try:
        result = subprocess.run(
            f'cd {ROOT_DIR} && make help',
            shell=True, capture_output=True, text=True
        )
        
        rules = []
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('🔹'):
                    # Extraer nombre del comando
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        name = clean_ansi(parts[0])
                        if name:
                            rules.append({"name": name})
        
        return jsonify(rules)
    except Exception as e:
        print(f"Error: {e}")
        return jsonify([])

@app.route('/run', methods=['POST'])
def run_command():
    """Ejecutar una regla del Makefile"""
    data = request.json
    if not data or 'rule' not in data:
        return jsonify({"status": "error", "message": "Regla no especificada"}), 400
    
    rule = data['rule']
    
    try:
        process = subprocess.Popen(
            f'cd {ROOT_DIR} && make {rule}',
            shell=True, stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, text=True
        )
        
        output = []
        for line in process.stdout:
            clean_line = clean_ansi(line.strip())
            if clean_line:
                output.append(clean_line)
        
        process.stdout.close()
        return_code = process.wait()
        
        return jsonify({
            "status": "success" if return_code == 0 else "error",
            "output": output
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Crear directorio templates si no existe
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    print("Gadget Panel iniciado en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 