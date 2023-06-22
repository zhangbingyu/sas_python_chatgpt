import re


def cleanup(string):
    """
    A function that remove extra space, comments, and so on from sas file
    :param string, from sas file
    :return a cleaned string
    """
    # replace line break with space
    string_cleaned = re.sub(r'\n|\t|\r', ' ', string)
    # replace multiple spaces with single space
    string_cleaned = re.sub(r'\s+', ' ', string_cleaned)
    # remove block comments
    string_cleaned = re.sub(r'/\*.*?\*/', '', string_cleaned)
    # remove single line comments
    string_cleaned = re.sub(r'^\s*\*.*?;', '', string_cleaned)
    string_cleaned = re.sub(r';\s*\*.*?;', ';', string_cleaned)
    # remove leading spaces of the file
    string_cleaned = re.sub(r'^\s+', '', string_cleaned)
    # remove spaces around ';', '(', and ')'
    string_cleaned = re.sub(r'\s*;\s*', ';', string_cleaned)
    string_cleaned = re.sub(r'\s*\(\s*', '(', string_cleaned)
    string_cleaned = re.sub(r'\s*\)\s*', ')', string_cleaned)
    string_cleaned = re.sub(r'\s*=\s*', '=', string_cleaned)
    string_cleaned = re.sub(r'\s*\+\s*', '+', string_cleaned)
    string_cleaned = re.sub(r'\s*-\s*', '-', string_cleaned)
    string_cleaned = re.sub(r'\s*\*\s*', '*', string_cleaned)
    string_cleaned = re.sub(r'\s*/\s*', '/', string_cleaned)
    string_cleaned = re.sub(r'\s*>\s*', '>', string_cleaned)
    string_cleaned = re.sub(r'\s*<\s*', '<', string_cleaned)
    # remove option statement
    string_cleaned = re.sub(r'options?.*?;', '', string_cleaned)
    return string_cleaned


def divide_to_blocks(string):
    """
    A function that divides the string into several SAS blocks.
    Blocks type: data block, proc block, macro block and %let block
    :param string
    :return a list of blocks
    """
    # separate to block by keywords data, proc,
    # %macro, run, %mend, %let, filename
    code_list = string.split(';')
    blocks = []
    blocks_macro = []
    blocks_macro_temp = []
    blocks_let = []
    block_item = []
    # dictionary that stores macros
    dict_macro = {}
    macro_count = 0
    for item in code_list:
        if re.search(r'^(data\s+)|(proc\s+)', item):
            if macro_count > 0:
                blocks_macro_temp[macro_count - 1].append(item + ";")
            elif block_item:
                blocks.append(block_item)
                block_item = []
                block_item.append(item + ";")
            else:
                block_item.append(item + ";")
        elif re.search(r'^run', item):
            if macro_count > 0:
                blocks_macro_temp[macro_count - 1].append(item + ";")
            elif block_item:
                blocks.append(block_item)
                block_item = []
        elif re.search(r'%let\s+', item):
            if macro_count > 0:
                blocks_macro_temp[macro_count - 1].append(item + ";")
            else:
                blocks.append(item + ";")
                blocks_let.append(item + ";")
        elif re.search(r'%macro\s+', item):
            macro_count += 1
            blocks_macro_temp.append([])
            if macro_count > 0:
                blocks_macro_temp[macro_count - 1].append(item + ";")
            else:
                # something wrong in the sas code
                pass
        elif re.search(r'%mend', item):
            macro_count -= 1
            blocks_macro.append(blocks_macro_temp.pop())
        elif re.search(r'^%', item):
            print(
                re.search(r'^%([_a-zA-Z][0-9a-zA-Z_]*)\s*\(.*?\)$',
                          item).group())

        else:
            if macro_count > 0:
                blocks_macro_temp[macro_count - 1].append(item + ";")
            elif block_item:
                block_item.append(item + ";")
            else:
                # something is wrong
                pass
    return (blocks, blocks_macro, blocks_let)


f = open(r'test/data_step_only.sas', 'r')
# read file into a long string
content = cleanup(f.read().lower())
blocks, macros, lets = divide_to_blocks(content)
print(blocks, macros, lets)
f.close()


