import os
from llama_index.core.node_parser import CodeSplitter
from tree_sitter_languages import get_language, get_parser

def get_files_by_language(directory, extensions):
    """
    Get files from the directory that match the specified extensions.
    
    :param directory: Path to the directory to scan.
    :param extensions: List of file extensions to filter by (e.g., ['.py', '.js']).
    :return: List of file paths matching the extensions.
    """
    matching_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                matching_files.append(os.path.join(root, file))
    return matching_files

def chunk_files(files):
    """
    Chunk the content of the provided files using llamaindex's CodeChunker.
    
    :param files: List of file paths to chunk.
    """
    language_str = "python"  # Specify the language for chunking
    language = get_language('python')
    #https://tree-sitter.github.io/tree-sitter/using-parsers/3-advanced-parsing.html
    parser = get_parser('python')
    chunker = CodeSplitter.from_defaults(language=language_str, parser=parser)
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        chunks = chunker.split_text(content)
        print(f"Chunks for {file_path}:")
        for chunk in chunks:
            print(chunk)

def main():
    # Define the directory to scan and the file extensions to filter by
    directory = "../ragengine/"  # Change this to your target directory
    extensions = '.py'  # Add more extensions as needed

    # Get files matching the specified language
    files = get_files_by_language(directory, extensions)
    print(f"Found {len(files)} files matching the extensions {extensions}.")

    # Chunk the files
    chunk_files(files)

if __name__ == "__main__":
    main()
