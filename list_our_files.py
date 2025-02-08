import os

def write_file_content(output_file, file_path):
    output_file.write(f"\n{'='*80}\n")
    output_file.write(f"File: {file_path}\n")
    output_file.write(f"{'='*80}\n")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            output_file.write(f.read())
            output_file.write('\n')
    except Exception as e:
        output_file.write(f"Error reading file: {e}\n")

def list_our_files(root_dir='Admin_Kiosk3_Backend', output_filename='our_files_content.txt'):
    # Lista de extensiones que queremos revisar
    extensions = {'.py', '.yml', '.yaml', '.md', '.conf', '.txt', '.json', '.jsx', '.js'}
    
    # Lista de directorios a ignorar
    ignore_dirs = {'.git', '__pycache__', 'venv', 'node_modules'}
    
    # Lista de archivos a ignorar
    ignore_files = {'model.pkl', 'our_files_content.txt'}

    with open(output_filename, 'w', encoding='utf-8') as output_file:
        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Ignorar directorios que no queremos
            dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
            
            for filename in filenames:
                if filename in ignore_files:
                    continue
                    
                file_path = os.path.join(dirpath, filename)
                _, ext = os.path.splitext(filename)
                
                if ext in extensions:
                    write_file_content(output_file, file_path)

if __name__ == '__main__':
    list_our_files()
    print("Contenido guardado en 'our_files_content.txt'") 