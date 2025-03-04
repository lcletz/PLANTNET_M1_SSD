import requests
import zipfile
import io
import os

def fetch_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return None

#def extract_and_print_headers(zip_content):
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        for file_name in z.namelist():
            with z.open(file_name) as f:
                print(f"Headers for {file_name}:")
                headers = f.readline().decode('utf-8').strip()
                print(headers)

#def extract_and_print_data(zip_content, num_lines=5): # num_lines à changer si besoin
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        for file_name in z.namelist():
            with z.open(file_name) as f:
                print(f"Data from {file_name}:")
                for _ in range(num_lines):
                    line = f.readline().decode('utf-8').strip()
                    if not line:
                        break
                    print(line)
                print("\n")

def extract_and_save_data(zip_content, output_dir="extracted_data", num_lines=200): # num_lines à changer si besoin
    os.makedirs(output_dir, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
        for file_name in z.namelist():
            if file_name.endswith('/'):
                continue 
            relative_path = os.path.join(output_dir, *file_name.split('/')[1:])
            os.makedirs(os.path.dirname(relative_path), exist_ok=True)
            with z.open(file_name) as f:
                with open(relative_path, 'wb') as out_file:
                    for _ in range(num_lines):
                        line = f.readline()
                        if not line:
                            break
                        out_file.write(line)
            print(f"Saved first {num_lines} lines of {file_name} to {relative_path}")

if __name__ == "__main__":
    url = "https://zenodo.org/record/10782465/files/plantnet_swe.zip"
    zip_content = fetch_data(url)
    if zip_content:
        print("Data fetched successfully:")
        #extract_and_print_headers(zip_content)
        #extract_and_print_data(zip_content)
        extract_and_save_data(zip_content, num_lines=200)  # num_lines à changer si besoin