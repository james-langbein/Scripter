import os
import time
import wikipedia


def copy_random_wikipedia_page():
    for n in range(1000):
        if n % 10 == 0:
            print(n)
        try:
            page_title = wikipedia.random(1)
            page = wikipedia.page(title=page_title)
            content = page.content

            with open('/home/james/PycharmProjects/PyQt-learn/Wikipedia Docs/' + page_title + '.txt', 'w') as file:
                file.write(content)
        except Exception:
            continue


def get_words(content):
    replace_dict = {'\n': ' ', ',': '', '.  ': '', '  ': ' ', '"': '', '.': '', '(': ' ', ')': ' ', '{': ' ', '}': ' ',
                    '\\': '', '[': '', ']': '', '_': '', '^': ''}
    res = ''.join(idx if idx not in replace_dict else replace_dict[idx] for idx in content)
    words = res.split(sep=' ')
    words = [word for word in words if word != '']
    return words


def get_filelist(root, subdirs=False):
    """Gets a master list of files with full paths."""
    file_list = []
    if subdirs:
        for path, subdirs, files in os.walk(top=root):
            for name in files:
                file_list.append({'file': name, 'full_path': os.path.join(path, name)})
    else:
        # files = os.walk(top=root).__next__()[2]  # gets file_list element of first os.walk iterator element
        files = os.listdir(root)
        for name in files:
            file_list.append({'file': name, 'full_path': os.path.join(root, name)})
    # names = [x['file'].split('.')[0] for x in file_list]
    return file_list


def index_pages_single_dir(folder):
    start = time.time()
    index = {}
    for file in os.listdir(folder):
        with open(folder + file, 'r') as f:
            content = f.read()
            words = get_words(content)
            unique_words = set(words)
            for word in unique_words:
                if word in index.keys():
                    index[word].append(file)
                else:
                    index[word] = [file]
    end = time.time()
    total = end - start
    print(index)
    print(f'\nTook {total} seconds to process 951 files.')
    print(f'Number of keys: {len(index.keys())}')


def index_data_source(root, subdirs=True, inclusions=None, exclusions=None):
    """
    Currently only supports file-system indexing.
    :param root: root folder
    :param subdirs: bool, traverse subdirs or not
    :param inclusions: exclusive list of folders to look in, all other folders will be ignored, defaults to None
    :param exclusions: exclusive list of folders to ignore, all files and subdirectories within each folder will be
    ignored, defaults to None
    :return: returns a dictionary representing all keywords found in files
    """
    start = time.time()
    indexed = {}
    if subdirs:
        for path, subdirs, files in os.walk(top=root):
            for file in files:
                with open(os.path.join(path, file), 'r') as f:
                    content = f.read()
                    words = get_words(content)
                    unique_words = set(words)
                    for word in unique_words:
                        if word in indexed.keys():
                            indexed[word].append(file)
                        else:
                            indexed[word] = [file]
    else:
        for file in os.listdir(root):
            with open(root + file, 'r') as f:
                content = f.read()
                words = get_words(content)
                unique_words = set(words)
                for word in unique_words:
                    if word in indexed.keys():
                        indexed[word].append(file)
                    else:
                        indexed[word] = [file]

    end = time.time()
    total = end - start
    print(indexed)
    print(f'\nTook {total} seconds to process 951 files.')
    print(f'Number of keys: {len(indexed.keys())}')


if __name__ == '__main__':
    index_data_source(root='/home/james/PycharmProjects/PyQt-learn/Wikipedia Docs/')
