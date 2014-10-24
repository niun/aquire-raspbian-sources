import subprocess, urllib2, re
from urlparse import urljoin

class LinkCache(dict):

    href_pattern = re.compile('href="([^"]*)"')

    def filter_descending(self, base_url, links):
        results = []
        for link in links:
            link_url = urljoin(base_url,link)
            if link_url.startswith(base_url) and (len(link_url) > len(base_url)): # link_url is down the directory tree
                results.append(link)
        return results


    def get_relative_links(self,url):
        if self.has_key(url):
            return self[url]
        else:
            print "    requesting " + url
            response = urllib2.urlopen(url)
            html = response.read()                                                                                                              
            links = self.filter_descending(url, self.href_pattern.findall(html))
            self[url] = links
            return self[url]
    
    
    def get_link_urls(self,base_url):
        links = self.get_relative_links(base_url)
        return [urljoin(base_url,link) for link in links]


cache = LinkCache()

source_pattern = re.compile(r'Source: (.*)')

url_prefix = "http://sourcearchive.raspbian.org/main/"
packages = subprocess.check_output('dpkg-query --showformat="\\${Package}//\\${Version};;" --show', shell=True).split(';;')

for package in packages:
    if package:
        name, version = package.split('//',1)
        source = source_pattern.search(subprocess.check_output('apt-cache show ' + name + "=" + version, shell=True))
        if source:
            source = source.groups()[0].split(' ')
            if len(source) > 1:
                version = source[1]
            source = source[0]
        else:
            source = name
        package = "_".join([source,version])
        if package.startswith('lib'):
            directory = package[0:4] + '/'
        else:
            directory = package[0] + '/'
        
        cache.get_relative_links

        print "{}: searching for package {} in {}".format(name,source,url_prefix + directory)
        pkg_dirs_online = cache.get_relative_links(url_prefix + directory)
        if source + '/' in pkg_dirs_online:
            print "    found package " + source
            # TODO: download sources
        else:
            # TODO: try "http://sourcearchive.raspbian.org/firmware/"
            print "    could not find package " + source

