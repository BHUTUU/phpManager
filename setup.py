import os, requests,subprocess, sys
from tqdm import tqdm
from bs4 import BeautifulSoup
import zipfile
def get_url_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving content from {url}: {e}")
        return False
def download_file(url, destination):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192  # You can adjust this value based on your preference

        with open(destination, 'wb') as file, tqdm(
                desc="Downloading",
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    file.write(chunk)
                    bar.update(len(chunk))
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")
        return False
def __windowsPhpDownloader():
    mainUrl="http://www.php.net"
    url = mainUrl+"/downloads.php"
    first_url_content = get_url_content(url)
    soup = BeautifulSoup(first_url_content, 'html.parser')
    link = soup.find('a', href=lambda href: href and 'windows.php.net' in href)
    if link:
        result_url = link['href']
    else:
        return False
    second_url_content = get_url_content(result_url)
    soup_second_url = BeautifulSoup(second_url_content, 'html.parser')
    zip_line = soup_second_url.find(string='Zip')
    if zip_line:
        zip_tag = zip_line.find_parent('a')
        if zip_tag:
            downloadLinkPath=zip_tag['href']
        else:
            return False
    else:
        return False
    finalLink="https://windows.php.net"+downloadLinkPath
    print(finalLink)
    download_file(finalLink, os.path.join(os.path.expanduser("~"), "Downloads\\php.zip"))
    # return downloadedStatus
if os.name == 'nt':
    import ctypes
    def is_admin():
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    def run_as_admin():
        if is_admin():

            # downloadedStatus = __windowsPhpDownloader()
            # print(downloadedStatus)
            phpPath = "C:\\Program Files\\php"
            if not os.path.exists("C:\\Program Files\\php\\php.exe"):
                print("PHP is not installed on your system! Downloading..............\n\n\n\n")
                __windowsPhpDownloader()
                with zipfile.ZipFile(os.path.join(os.path.expanduser("~"), "Downloads\\php.zip"), "r") as phpZip:
                    phpZip.extractall("C:\\Program Files\\php")
                phpZip.close()
                # subprocess.run(['setx', 'PATH', f'"{phpPath};{os.environ["PATH"]}"'])
            else:
                print("Php already downloaded")
        else:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
    run_as_admin()
elif sys.name == "GNU/Linux" or sys.name == "posix":
    os.system("sudo apt install php -y || printf 'Install php manually!\n'")