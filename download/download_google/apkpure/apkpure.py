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
    def __init__(self, verbose = True) -> None:
        self.query_url = "https://apkpure.com/search?q="
        self.verbose = verbose

    def __check_name(self, name : str) -> None :
        """Verify if the query is valid to avoid errors
        
        Keyword arguments:
        name : the query
        Return: None | exit
        """
        
        name = name.strip()
        name.replace(":", " ")
        if not name:
            sys.exit(
                "No search query provided!",
            )
            
        self.show_status('The query is accepted')

    def __soup_factory(self, url : str) -> BeautifulSoup:
        """Returns soup object from an given URL,
        using cloudscraper to avoid cloudflare anti-bot protection
        
        Keyword arguments:
        url : the website URL
        Return: BeautifulSoup
        """
        
        response = self.__get_response(url=url)
        if not response:
            sys.exit("Error: Bad request!")
        return BeautifulSoup(response.text, "html.parser")

    def __get_response(self, url: str, **kwargs) -> requests.Response | None:
        """A wrapper for requests.get to avoid cloudflare anti-bot protection.
        This function accepts any argument for requests.get, like stream, timeout, etc.
        Also, it doesn't need headers, as cloudscraper already sets them by default.
        
        Keyword arguments:
        url : the target url
        kwargs : additional arguments for requests.get
        example:
        __get_response("https://google.com", timeout = 10)
        Return: requests.Response | None
        """
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

        """Get first app result from the search result page in ApkPure.
        Is harder to get app not found, because the search result is dynamic.
        To avoid the app not found, use the check_name method.
        
        Keyword arguments:
        name : the query
        Return: JSON string or Exception
        """
        self.__check_name(name)

        self.show_status(
            f'Searching: {name}'
        )

        query_url = self.query_url + name
        soup_obj = self.__soup_factory(query_url)

        first_div: BeautifulSoup = soup_obj.find("div", class_="brand-info-top")

        # package_url = first_div.find("a", class_="href")


        if first_div is None:
            print("App not found, we will try to find it in another way")

            target_div: BeautifulSoup = soup_obj.find("div", class_ = "search-section")
            result = scraper.extract_xiaozhong(target_div)
            return json.dumps(result, indent = 4)


        # if package_url is None:
        #     package_url = first_div.find("a", class_="dd")

        self.show_status('App found')

        result = scraper.extract_info_from_search(first_div)
        self.show_status(
            f'{name} information has been extracted'
        )

        return json.dumps(result, indent=4)
    
    def download(self, name: str, version: str = None, xapk: bool = False) -> str | None:
        """Download an apk or xapk.
        the downloaded app is the first result from the get_first_app_result() method, so check it before.
        
        Keyword arguments:
        name : the query
        version : the version of the app, if not specified it will be the lastest version on site
        XAPK : specify True to download an xapk, False by default
        Return: None
        """
        
        self.__check_name(name)

        
        try:
            package_info : dict = json.loads(self.get_first_app_result(name))
        except json.JSONDecodeError:
            self.show_status(f"Error: Failed to parse package information for {name}")
            return None
        
        app_type = 'XAPK' if 'XAPK' in package_info.get('apk_type') else 'APK'
        print(app_type)
        
        self.show_status(
            f'Downloading {app_type} file from app {name}'
        )


        # version_code = None
        
        # if version:
        #     versions : list[dict]= json.loads(self.get_versions(name))
        #     for version_ in versions:
        #         if str(version_.get('version')) == version:
        #             version_code = version_.get("version_code")
                    
        #             break

        #     if not version_code:
        #         self.show_status('The passed version is not founded')
        
        version_code = "latest"
        self.show_status(
                        f'the version code was been setted to {version_code}'
                        )
        # https://apkpure.com/garena-free-fire-android-2024/com.dts.freefireth/downloading
        # https://d.apkpure.com/b/APK/com.dts.freefireth?versionCode=2019117718
        base_url = f'https://d.apkpure.com/b/{app_type}/' \
                    + package_info.get('package_name') \
                    + '?version=' \
                    + version_code
        print(base_url)
        # 需要下载APK的话就要把{app_type}换成APK就行
        return self.__downloader(url=base_url, name=name, version_code=version_code)
    
    def __downloader(self, url: str, name: str = None, version_code: str = None) -> str | None:
        """The downloader method, don't use separately.
        """
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
        
        # Handle the name of the filename
        try:
            filename = response.headers.get('Content-Disposition').split('filename=')[1].replace('"', '').replace(" ", '').replace(';', '').replace(':', '')
        except (AttributeError, IndexError):
            self.show_status(f"Error: Failed to retrieve filename for {name}")
            return None
        
        self.show_status(f'The file will be saved as {version_code}_{filename}')
        
        # 目标保存路径
        save_path = r"C:\Users\22863\Desktop\毕设\app数据集\app集合"
        
        # 确保目录存在
        os.makedirs(save_path, exist_ok=True)

        # 拼接完整路径
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