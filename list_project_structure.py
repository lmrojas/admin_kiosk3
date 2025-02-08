import os

def list_project_files(startpath):
    """
    Lista todos los archivos y carpetas del proyecto recursivamente
    """
    with open('project_structure.txt', 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(startpath):
            # Ignorar carpetas comunes que no queremos listar
            if '.git' in dirs:
                dirs.remove('.git')
            if '__pycache__' in dirs:
                dirs.remove('__pycache__')
            if '.pytest_cache' in dirs:
                dirs.remove('.pytest_cache')
            
            level = root.replace(startpath, '').count(os.sep)
            indent = '│   ' * level
            f.write(f'{indent}├── {os.path.basename(root)}/\n')
            
            subindent = '│   ' * (level + 1)
            for file in files:
                if not file.endswith('.pyc'):
                    f.write(f'{subindent}├── {file}\n')
                    # Opcionalmente, podemos también mostrar el contenido del archivo
                    # with open(os.path.join(root, file), 'r', encoding='utf-8') as content:
                    #     f.write(f'{subindent}    {content.read()}\n')

if __name__ == '__main__':
    # Asumiendo que el script se ejecuta desde la raíz del proyecto
    project_root = '.'
    list_project_files(project_root)
    print("Estructura del proyecto guardada en 'project_structure.txt'") 