import json
import os
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import sys
import cloudscraper

# Utils
import extractors as scraper

class ApkPure:
    def __init__(self, verbose=True) -> None:
        self.query_url = "https://apkpure.com/search?q="
        self.verbose = verbose

    def __check_name(self, name: str) -> None:
        """Verify if the query is valid to avoid errors"""
        name = name.strip().replace(":", " ")
        if not name:
            sys.exit("No search query provided!")
        self.show_status('The query is accepted')

    def __soup_factory(self, url: str) -> BeautifulSoup:
        """Returns soup object from a given URL"""
        response = self.__get_response(url=url)
        if not response:
            sys.exit("Error: Bad request!")
        return BeautifulSoup(response.text, "html.parser")

    def __get_response(self, url: str, **kwargs) -> requests.Response | None:
        """A wrapper for requests.get to avoid cloudflare anti-bot protection"""
        self.show_status(f'Requesting: {url}')
        try:
            scraper = cloudscraper.create_scraper()
            response = scraper.get(url=url, **kwargs)
            if response.status_code == 403:
                self.show_status("Error: Request was blocked, try to update the ApkPure API!")
                return None
            return response if response.status_code == 200 else None
        except Exception as e:
            self.show_status(f"Error: Failed to get response for {url}. Reason: {e}")
            return None

    def show_status(self, msg):
        if self.verbose:
            print(msg)

    def get_first_app_result(self, name: str) -> str | Exception:
        """Get first app result from the search result page in ApkPure"""
        self.__check_name(name)
        self.show_status(f'Searching: {name}')
        query_url = self.query_url + name
        soup_obj = self.__soup_factory(query_url)
        first_div = soup_obj.find("div", class_="brand-info-top")

        if first_div is None:
            self.show_status("App not found, trying another way")
            target_div = soup_obj.find("div", class_="search-section")
            result = scraper.extract_xiaozhong(target_div)
            return json.dumps(result, indent=4)

        self.show_status('App found')
        result = scraper.extract_info_from_search(first_div)
        self.show_status(f'{name} information has been extracted')
        return json.dumps(result, indent=4)

    def download(self, name: str, version: str = None, xapk: bool = False) -> str | None:
        """Download an apk or xapk"""
        self.__check_name(name)
        try:
            package_info = json.loads(self.get_first_app_result(name))
        except json.JSONDecodeError:
            self.show_status(f"Error: Failed to parse package information for {name}")
            return None

        app_type = 'XAPK' if 'XAPK' in package_info.get('apk_type') else 'APK'
        self.show_status(f'Downloading {app_type} file from app {name}')
        version_code = "latest"
        self.show_status(f'The version code was set to {version_code}')
        base_url = f'https://d.apkpure.com/b/{app_type}/{package_info.get("package_name")}?version={version_code}'
        return self.__downloader(url=base_url, name=name, version_code=version_code)

    def __downloader(self, url: str, name: str = None, version_code: str = None) -> str | None:
        """The downloader method, don't use separately."""
        try:
            response = self.__get_response(url=url, stream=True)
            if response is None:
                self.show_status(f"Error: Failed to get response for {name}. Skipping...")
                return None
            file_size = int(response.headers.get('Content-Length', 0))
        except requests.RequestException as e:
            self.show_status(f"Error: Failed to download {name}. Reason: {e}")
            return None

        self.show_status(f'The {name} app has {file_size / 1000000} MB size')
        try:
            filename = response.headers.get('Content-Disposition').split('filename=')[1].replace('"', '').replace(" ", '').replace(';', '').replace(':', '')
        except (AttributeError, IndexError):
            self.show_status(f"Error: Failed to retrieve filename for {name}")
            return None

        self.show_status(f'The file will be saved as {version_code}_{filename}')
        save_path = r"C:\Users\22863\Desktop\毕设\app数据集\OBD app"
        os.makedirs(save_path, exist_ok=True)
        file_path = os.path.join(save_path, f"{version_code}_{filename}")

        try:
            with open(file_path, 'wb') as package_file:
                progress_bar = tqdm(total=file_size, unit='B', unit_scale=True, desc=f'Downloading {name}', dynamic_ncols=True, leave=True)
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        package_file.write(chunk)
                        progress_bar.update(len(chunk))
                progress_bar.close()
        except IOError as e:
            self.show_status(f"Error: Failed to save {name}. Reason: {e}")
            return None

        return f'{name} was downloaded to {file_path}' if response else f'Error while trying to download {url}'