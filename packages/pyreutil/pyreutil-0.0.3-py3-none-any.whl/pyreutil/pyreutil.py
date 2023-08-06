import re
import os
import shutil

from typing import List, Union

from .utils import *

class ReUtil:
    
    def __init__(self, verbose : bool = False, **kwargs):
        self.verbose : bool = verbose
        self.color_search : List[int] = [255,0,0]
        self.color_replace : List[int] = [0,255,0]
    
    @mutually_exclusive('replace', 'group')
    def search_and_replace(self, regex : str, text : str, replace : str = None, group : int = 0) -> str:
        """Searches through text and replaces with string."""
        if replace is None:
            return re.sub(r'{}'.format(regex), lambda m: m.group(group), text)
        return re.sub(r'{}'.format(regex), r'{}'.format(replace), text) 
    
    def lambda_search_and_replace(self, regex : str, text : str, lambda_str : str) -> str:
        """Regex search and replace with a lambda function."""
        return re.sub(r'{}'.format(regex), lambda x: eval(lambda_str), text)
    
    def search(self, regex: str, text : str) -> int:
        """Returns the number of matches found in the text."""
        count = len(re.findall(r'{}'.format(regex), text))
        return count 
    
    def remove(self, regex : str, text : str) -> str:
        """Removes matches from a given text."""
        return re.sub(r'{}'.format(regex), '', text) 
    
    def save_changes(self, mode : str) -> None:
        modes = ['inplace', 'copy']
        if mode not in modes:
            raise Exception("Error: The mode {} is not valid. Input 'inplace' or 'copy'.")
        
    def remove_extra_whitespaces(self, text : str) -> str:
        """Removes extra whitespaces from a given text."""
        text = re.sub(r'\s+', ' ', text.strip())
        text = re.sub('[ ]([,|.|\)])', r'\1', text)
        return text
        
    def colored_search(self, regex : str, text : str, color = None) -> str:
        """Returns string with regex matches colored."""
        if color is not None and (len(color) != 3 or not all(isinstance(k, int) for k in color)):
            raise TypeError("Error: Color must be a list or tuple of three integers.")
        print_color = self.color_search if color is None else color
        return re.sub(regex, lambda m: self._colored(print_color, m.group()), text)
    
    @mutually_exclusive('replace', 'group', 'lambda_func')
    def colored_replace(self, regex : str, text : str, replace : str = None, group : int = 0, lambda_func : str = None, color = None) -> str:
        """Returns a string with the regex substitutes colored."""
        if color is not None and (len(color) != 3 or not all(isinstance(k, int) for k in color)):
            raise TypeError("Error: Color must be a list or tuple of three integers.")
        print_color = self.color_replace if color is None else color
        if lambda_func: 
            return re.sub(regex, lambda x: self._colored(print_color, eval(lambda_func)), text)
        if group > 0:
            return re.sub(regex, lambda m: self._colored(print_color, m.group(group)), text)
        return re.sub(regex, self._colored(print_color, replace), text)
            
    def _colored(self, values : List[int], text : str) -> str:
        """Returns a colored version of the string."""
        r, g, b = values[0], values[1], values[2]
        return "\033[38;2;{};{};{}m{}\033[m".format(r, g, b, text)
    
    def print_line_divider(self, char : str = '-') -> None:
        """Prints a divider based on the length of the terminal."""
        assert(len(char) == 1)
        print(char*shutil.get_terminal_size().columns)
    

class TextUtil(ReUtil):
    
    @mutually_exclusive('text', 'filenames')
    def __init__(self, text : List[str]=[], filenames : Union[str, List[str]] = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_dir : str = None
        if type(filenames) is str and isdir(filenames):
            self.original_dir = filenames
        self.original_filenames : List[str] = filenames
        self.original_text : List[str] = text
        self.text : List[str] = text
        if len(filenames) > 0:
            self.original_filenames = iterate_files(filenames, search_subdirs=kwargs['search_subdirs']) if isdir(filenames) else [ filenames ]
            to_remove = []
            self.original_filenames.sort()
            for filepath in self.original_filenames:
                try:
                    with open(filepath, 'r') as f:
                        self.original_text.append(f.read())
                except Exception as e:
                    print("Error: Could not read file '{}'. Removing from search list.".format(filepath))
                    to_remove.append(filepath)
                    super().print_line_divider()
            for file in to_remove:
                self.original_filenames.remove(file)
            self.text = self.original_text
    
    @mutually_exclusive('replace', 'from_file', 'group', 'lambda_func')
    def search_and_replace(self, regex : str, replace : str = None, from_file : str = None, group: int = -1, lambda_func: str = None) -> List[str]:
        new_text = []
        if from_file is not None:
            replace = get_file_contents(from_file)
        for i, txt in enumerate(self.text):
            if replace or from_file:
                new = super().search_and_replace(regex, txt, replace=replace)
                colored_replace = self.colored_replace(regex, txt, replace=replace)
            elif lambda_func:
                new = super().lambda_search_and_replace(regex, txt, lambda_func)
                colored_replace = self.colored_replace(regex, txt, lambda_func=lambda_func)
            else:
                new = super().search_and_replace(regex, txt, group=group)
                colored_replace = self.colored_replace(regex, txt, group=group)
            if self.verbose:
                if self.original_filenames:
                    print("Search and replacing in '{}'...\n".format(self.original_filenames[i]))
                colored_search = self.colored_search(regex, txt)
                print(colored_search)
                count = ReUtil().search(regex, txt)
                print(">> {} matches found.".format(count))
                print(colored_replace)
                super().print_line_divider()
            new_text.append(new)
        self.text = new_text
        return self.text
    
    def search(self, regex : str) -> int:
        count = 0
        for i, txt in enumerate(self.text):
            searches = super().search(regex, txt)
            if self.verbose:
                if self.original_filenames:
                    print("Searching in '{}'...\n".format(self.original_filenames[i]))
                colored_search = self.colored_search(regex, txt)
                print(colored_search)
                super().print_line_divider()
            count += searches
        if self.verbose and self.original_filenames:
            print(">> {} matches found in {} file(s)".format(count, len(self.original_filenames)))
        else:
            print(">> {} total matches found.".format(count))
        return count
    
    def remove(self, regex : str) -> List[str]:
        """Returns a list of texts with the regex matches removed"""
        new_text = []
        if self.verbose:
            print("Removing searches...")
        for i, txt in enumerate(self.text):
            if self.verbose and self.original_filenames:
                print("Searching for matches to remove in '{}'...\n".format(self.original_filenames[i]))
            new = super().remove(regex, txt)
            count = super().search(regex, txt)
            if self.verbose:
                if count == 0:
                    print("No matches to '{}' were found.".format(regex))
                else:
                    colored_search = self.colored_search(regex, txt)
                    print(colored_search)
                    print("  {} matches to be removed were found".format(count))
                super().print_line_divider()
            new_text.append(new)
        self.text = new_text
        return self.text

    def append(self, content : str, is_file : bool=False) -> List[str]:
        """Appends content to the end of each file. Given either a string to
        append or a path to a file with contents to append."""
        if self.verbose:
            if is_file:
                print(f"Appending {content} contents to the end of each file...")
            else:
                print("Appending text to the end of each file...")
        if is_file:
            content = get_file_contents(content)
        
        new_text = []
        for i, txt in enumerate(self.text):
            if self.verbose:
                if self.original_filenames:
                    print("Appending to '{}'...\n".format(self.original_filenames[i]))
                print(txt)
                colored_append = self.colored_search(".*", content, color=[0,255,0])
                print(colored_append + '\n')
                super().print_line_divider()
            txt += '\n' + content + '\n'
            new_text.append(txt)
        self.text = new_text
        return self.text
    
    def save_changes(self, mode : str = 'inplace') -> None:
        """Saves content changes to original files, or to a copy of the file(s)."""
        super().save_changes(mode)
        if len(self.original_filenames) == 0:
            print("No files to save changes to.")
            return
        if len(self.original_filenames) != len(self.text):
            raise Exception("Error! Length of original and modified files are not the same.")
        
        if mode == 'inplace':
            for i in range(0, len(self.original_text)):
                with open(self.original_filenames[i], 'w') as f:
                    f.write(self.text[i])
            if self.verbose:
                print("Changes saved inplace.")

        if mode == 'copy':
            if self.original_dir:
                from pathlib import Path
                
                new_dir = self.original_dir + "_copy"
                
                for i, original_path in enumerate(self.original_filenames):
                    subdirs, filename = get_subdir_and_file_from_dir(original_path, self.original_dir)
                    dir_path = os.path.join(new_dir, *subdirs)
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                    with open(os.path.join(dir_path, filename), 'w') as f:
                        f.write(self.text[i])
                if self.verbose:
                    print("Changes saved as files in a new directory '{}'".format(dir_path))
            else:
                for i, original_path in enumerate(self.original_filenames):
                    head, tail, ext = split_fullpath(original_path)
                    tail += "_copy"
                    new_path = os.path.join(head, tail + ext)
                    with open(new_path, 'w') as f:
                        f.write(self.text[i])
                if self.verbose:
                    print("Changes saved as new files.")
    
    def remove_extra_whitespaces(self) -> str:
        """Removes redundant whitespaces (leading, trailing, and spaces before a period, comma or bracket)."""
        if self.verbose:
            print("Removing extra whitespaces...")
        new_text = []
        for txt in self.text:
            new_text.append(super().remove_extra_whitespaces(txt))
        self.text = new_text
        return self.text
    
    # CUSTOM TEXT FUNCTIONS
    
    def strip_markdown_links(self) -> List[str]:
        """Returns the text with stripped markdown links replaced with the link name."""
        link_name = "[\[]?[^\[^\]]+[\]]?"
        link_url = "http[s]?://[^\)]+"
        mdlink_regex = f"\[{link_name}]\({link_url}\)"
        mdlink_parts_regex = f"\[({link_name})]\(({link_url})\)"
        
        new_text = []
        if self.verbose:
            print("Stripping markdown links in text...")
        for i, txt in enumerate(self.text):
            new = super().search_and_replace(mdlink_parts_regex, txt, group=1)
            count = ReUtil().search(mdlink_regex, txt)
            if self.verbose:
                if self.original_filenames:
                    print("Searching '{}'...".format(self.original_filenames[i]))
                if count == 0:
                    print("No links were found.")
                else:
                    colored_search = self.colored_search(mdlink_parts_regex, txt)
                    colored_replace = self.colored_replace(mdlink_parts_regex, txt, group=1)
                    print(colored_search)
                    print("  {} link(s) found".format(count))
                    print(colored_replace,'\n')
            new_text.append(new)
        self.text = new_text
        return self.text


class FilenameUtil(ReUtil):
    
    @mutually_exclusive('path', 'pathnames')
    def __init__(self, path : str = None, pathnames : List[str] = [], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path = path
        self.original_pathnames : List[str] = pathnames
        self.pathnames : List[str] = pathnames
        if path is not None:
            self.original_pathnames = iterate_files(path, search_subdirs=kwargs['search_subdirs']) if isdir(path) else [path]
            self.original_pathnames.sort()
            self.pathnames = self.original_pathnames
    
    @mutually_exclusive('replace', 'from_file', 'group', 'lambda_func')
    def search_and_replace(self, regex : str, replace : str = None, from_file : str = None, group : int = 0, lambda_func : str = None) -> List[str]:
        """Substitutes regex searches with a string replacement, returning a list of new pathnames."""
        new_names = []
        files_changed = 0
        if from_file is not None:
            replace = get_file_contents(from_file)
        for path in self.pathnames:
            head, tail, ext = split_fullpath(path)
            if replace or from_file:
                new_tail = super().search_and_replace(regex, tail, replace=replace)
                colored_replace = os.path.join(head, self.colored_replace(regex,tail,replace=replace)+ext)
            elif lambda_func:
                new_tail = super().lambda_search_and_replace(regex, tail, lambda_str=lambda_func)
                colored_replace = os.path.join(head, self.colored_replace(regex,tail,lambda_func=lambda_func)+ext)
            else:
                new_tail = super().search_and_replace(regex, tail, group=group)
                colored_replace = os.path.join(head, self.colored_replace(regex,tail,group=group)+ext)
            if new_tail != tail:
                files_changed += 1
            colored_search = os.path.join(head, self.colored_search(regex,tail)+ext)
            if self.verbose:
                if colored_search == colored_replace:
                    print(colored_search)
                else:
                    print("{} ==> {}".format(colored_search, colored_replace))
            new_names.append(os.path.join(head, new_tail+ext))
        if self.verbose:
            print("  Changes in {}/{} filenames.".format(files_changed, len(self.pathnames)))
        self.pathnames = new_names
        return self.pathnames
    
    def search(self, regex : str) -> int:
        """Returns number of regex matches in the names."""
        count = 0
        for path in self.pathnames:
            head, tail, ext = split_fullpath(path)
            # matches, colored_search = super().search(regex, tail)
            matches = super().search(regex, tail)
            if self.verbose:
                colored_search = self.colored_search(regex, tail)
                print(os.path.join(head,colored_search+ext))
            count += matches
        if self.verbose:
            print(">> {} matches found in {} filename(s).".format(count, len(self.pathnames)))
        return count
    
    def remove(self, regex : str) -> List[str]:
        """Returns a list of new pathnames with the regex search removed."""
        new_names = []
        for path in self.pathnames:
            head, tail, ext = split_fullpath(path)
            tail = super().remove(regex, tail)
            if self.verbose:
                print("To be removed...")
                colored_search = self.colored_search(regex, tail)
                print(os.path.join(head, colored_search+ext))
            new_names.append(os.path.join(head,tail+ext))
        self.pathnames = new_names
        return self.pathnames
    
    def append(self, content : str, is_file : bool=False) -> List[str]:
        """Appends content to the end of the filenames."""
        if self.verbose:
            if is_file:
                print(f"Appending content from '{content}' to the filenames...")
            else:
                print(f"Appending '{content}' to the end of the filenames...")
        if is_file:
            content = get_file_contents(content)
            
        new_names = []
        for path in self.pathnames:
            head, tail, ext = split_fullpath(path)
            new_name = tail+content+ext
            content_copy = content
            # Checks if filename is too long
            if len(new_name) > 255:
                warning_txt = "WARNING: Filename exceeds 255 characters and has been truncated."
                print(super()._colored([255,0,0], warning_txt))
                content = content[:255-len(tail)-len(ext)]
                new_name = tail+content+ext
            if self.verbose:
                colored_append = self.colored_search(".*", content, color=[0,255,0])
                print(os.path.join(head, tail+colored_append+ext))
            new_names.append(os.path.join(head, new_name))
            content = content_copy
        self.pathnames = new_names
        return self.pathnames
    
    def save_changes(self, mode : str = 'inplace') -> None:
        """Saves the filename changes inplace (renames input paths), or creates a copy."""
        super().save_changes(mode)
        if len(self.original_pathnames) != len(self.pathnames):
            raise Exception("Error! Length of original and modified filenames are not the same.")
        
        if mode is 'inplace':
            for i in range(0, len(self.original_pathnames)):
                os.rename(self.original_pathnames[i], self.pathnames[i])
            if self.verbose:
                print("Changes saved inplace.")
        
        if mode is 'copy':
            if self.path and isdir(self.path):
                from pathlib import Path
                new_dir = self.path + '_copy'
                for original_path, new_path in zip(self.original_pathnames, self.pathnames):
                    subdirs, filename = get_subdir_and_file_from_dir(new_path, self.path)
                    dir_path = os.path.join(new_dir, *subdirs)
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(original_path, os.path.join(dir_path, filename))
                if self.verbose:
                    print("Changes saved in a copy of the original directory '{}'".format(new_dir))
            else:
                for original_path, new_path in zip(self.original_pathnames, self.pathnames):
                    shutil.copyfile(original_path, new_path)
                if self.verbose:
                    print("Changes saved as a copy.")
                    
    def remove_extra_whitespaces(self) -> str:
        """Removes extra whitespaces from the filenames."""
        if self.verbose:
            print("Removing extra whitespaces from the filenames...")
        new_names = []
        for filename in self.pathnames:
            new_names.append(super().remove_extra_whitespaces(filename))
        self.pathnames = new_names
        return self.pathnames