from flask import Flask, render_template, jsonify, request, send_from_directory
import subprocess
import os
import re
import json

app = Flask(__name__, 
            static_folder='../static',
            template_folder='../templates')

# Directorio raíz del proyecto (un nivel arriba de panels/)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clean_ansi(text):
    """Eliminar códigos ANSI"""
    ansi_pattern = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
    return ansi_pattern.sub('', text)

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/static/<path:path>')
def send_static(path):
    """Servir archivos estáticos"""
    return send_from_directory('../static', path)

@app.route('/rules')
def get_rules():
    """Obtener reglas del Makefile con descripciones"""
    try:
        # Imprimir el directorio actual para depuración
        print(f"Directorio raíz detectado: {ROOT_DIR}")
        
        # Verificar si existe el Makefile
        makefile_path = os.path.join(ROOT_DIR, 'Makefile')
        if not os.path.exists(makefile_path):
            print(f"⚠️ No se encontró el Makefile en: {makefile_path}")
            return jsonify({"categories": {}, "error": "No se encontró el Makefile"})
        else:
            print(f"✅ Makefile encontrado en: {makefile_path}")
        
        result = subprocess.run(
            f'cd {ROOT_DIR} && make help',
            shell=True, capture_output=True, text=True
        )
        
        rules = []
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.strip() and not line.startswith('🔹'):
                    # Extraer nombre y descripción del comando
                    parts = line.strip().split()
                    if len(parts) >= 2:
                        name = clean_ansi(parts[0])
                        # Intentar extraer descripción (todo después del primer #)
                        description = ""
                        desc_index = line.find('#')
                        if desc_index > -1:
                            description = clean_ansi(line[desc_index+1:].strip())
                        
                        if name:
                            # Categorizar comandos basados en prefijos comunes
                            category = "General"
                            if name.startswith('db-') or name == 'setup-db':
                                category = "Base de Datos"
                            elif name.startswith('deploy'):
                                category = "Despliegue"
                            elif name in ['clean', 'venv', 'install', 'build']:
                                category = "Configuración"
                            elif name in ['test', 'run', 'scrape']:
                                category = "Ejecución"
                            elif name == 'panel':
                                category = "Panel Web"
                            
                            rules.append({
                                "name": name,
                                "description": description,
                                "category": category
                            })
        
        # Agrupar comandos por categoría
        categories = {}
        for rule in rules:
            cat = rule["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(rule)
        
        return jsonify({"categories": categories})
    except Exception as e:
        print(f"Error al obtener reglas: {e}")
        return jsonify({"categories": {}, "error": str(e)})

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
            clean_line = clean_ansi(line.rstrip())
            if clean_line:
                # Añadir clase de estilo basada en el contenido de la línea
                line_class = "info"
                if "error" in clean_line.lower() or "❌" in clean_line:
                    line_class = "error"
                elif "warning" in clean_line.lower() or "⚠️" in clean_line:
                    line_class = "warning"
                elif "✅" in clean_line or "success" in clean_line.lower():
                    line_class = "success"
                
                output.append({"text": clean_line, "class": line_class})
        
        process.stdout.close()
        return_code = process.wait()
        
        return jsonify({
            "status": "success" if return_code == 0 else "error",
            "output": output
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/command-info', methods=['GET'])
def get_command_info():
    """Obtener información detallada sobre un comando específico"""
    command = request.args.get('command')
    if not command:
        return jsonify({"status": "error", "message": "Comando no especificado"}), 400
    
    try:
        result = subprocess.run(
            f'cd {ROOT_DIR} && make show-rule RULE={command}',
            shell=True, capture_output=True, text=True
        )
        
        if result.returncode == 0:
            return jsonify({
                "status": "success", 
                "command": command,
                "details": clean_ansi(result.stdout)
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No se pudo obtener información del comando"
            }), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Crear directorio templates si no existe
    templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    # Crear directorio static si no existe
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    print("Gadget Panel iniciado en http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)