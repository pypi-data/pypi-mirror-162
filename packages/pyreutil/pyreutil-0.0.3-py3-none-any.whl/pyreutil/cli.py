import argparse

from .pyreutil import *

def run(args) -> None:
    
    if args.textfiles:
        content = TextUtil(filenames=args.textfiles, verbose=not args.silence, search_subdirs=args.deep)
    elif args.filenames:
        content = FilenameUtil(path=args.filenames, verbose=not args.silence, search_subdirs=args.deep)
    
    # Build-in regex function
    # if args.textfiles and args.remove_md_links:
    #     content.strip_markdown_links()
    
    # Core functions
    if args.remove:
        content.remove(args.remove)
    if args.append_file:
        content.append(args.append_file, is_file=True)
    if args.append:
        content.append(args.append)
    if not args.search and (args.replace or args.group):
        raise("Error: --replace and --group must be used with --search")
    if args.replace and args.group:
        raise("Error: --replace and --group cannot be used together")
    if args.search and not (args.replace or args.replacement_file or args.group or args.lambda_func):
        content.search(args.search)
    if args.search and args.replace:
        content.search_and_replace(args.search, replace=args.replace)
    if args.search and args.replacement_file:
        content.search_and_replace(args.search, from_file=args.replacement_file)
    if args.search and args.group:
        content.search_and_replace(args.search, group=args.group)
    if args.search and args.lambda_func:
        content.search_and_replace(args.search, lambda_func=args.lambda_func)
    if args.remove_whitespaces:
        content.remove_extra_whitespaces()

    # Save content
    if args.search and (args.replace or args.replacement_file, args.group or args.lambda_func) and not (args.inplace or args.copy):
        print("Warning: Changes have not been saved. Use -i --inplace or -c --copy to save changes.")
    if args.inplace:
        content.save_changes(mode='inplace')
    if args.copy:
        content.save_changes(mode='copy')
    

def main() -> None:
    """Process command line arguments and execute the given command.""" 
    parser = argparse.ArgumentParser(description="pyreutil - A python command line utility for searching and modifying files and filenames using regex.")
    
    # Two Modes
    core = parser.add_mutually_exclusive_group()
    core.add_argument('-t', '--textfiles', help='text source', type=str, required=False)
    core.add_argument('-f', '--filenames', help='filenames source', type=str, required=False)
    
    # Global commands
    parser.add_argument('-a', '--append', help='text to append', type=str, required=False)
    parser.add_argument('-af', '--append-file', help='appends file contents', type=str, required=False) # only for textfiles
    parser.add_argument('-c', '--copy', help='saves changes as a copy of the original directory/file', action='store_true', required=False)
    parser.add_argument('-d', '--deep', help='search subdirectories if a directory is given', action='store_true', required=False)
    parser.add_argument('-i', '--inplace', help='save changes to the existing directory/file', action='store_true', required=False)
    parser.add_argument('-l', '--lambda-func', help='code string to execute in a lambda function. Must be used with -s --search', type=str, required=False)
    parser.add_argument('-r', '--replace', help='raw string to replace searches with. Must be used with -s --search', type=str, required=False)
    parser.add_argument('-rf', '--replacement-file', help='file containing contents to replaces regex searches with. Must be used with -s --search', type=str, required=False) 
    parser.add_argument('-g', '--group', help='integer representing the group to replace. Must be used with -s --search', type=int, required=False)
    parser.add_argument('-rm', '--remove', help='removes regex matches', type=str, required=False)
    parser.add_argument('-s', '--search', help='searches for regex matches', type=str, required=False)
    parser.add_argument('-si', '--silence', help='silences the output', action='store_true', required=False)
    parser.add_argument('-w', '--remove-whitespaces', help='removes redundant whitespaces (repeat, leading, trailing, and spaces before a period or comma)', action='store_true', required=False)
    # Exclusive to modifying contents
    # parser.add_argument('-md', '--remove-md-links', help='removes markdown links and replaces it with the link name', action='store_true', required=False)
    
    for g in parser._action_groups:
        g._group_actions.sort(key=lambda x:x.dest)
    
    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    main()
    
    
# "\[([\[]?[^\[^\]]+[\]]?)]\((http[s]?://[^\)]+)\)"