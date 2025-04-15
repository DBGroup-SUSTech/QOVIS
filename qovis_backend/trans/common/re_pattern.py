import re

# expression
# AttrPattern = re.compile(r"(?<!\")[a-zA-Z0-9_]+#-?\d+L?(?!\")")
AttrPattern = re.compile(r"[a-zA-Z0-9_]+#-?\d+L?")
FullAttrPattern = re.compile(r"^[a-zA-Z0-9_()]+#-?\d+L?$")
RenamePattern = re.compile(r"^[a-zA-Z0-9_]+#-?\d+L? AS [a-zA-Z0-9_()]+#-?\d+L?$")
FuncPattern = re.compile(r"^[a-zA-Z0-9_]+\(.*\) AS [a-zA-Z0-9_()]+#-?\d+L?$")
OtherPattern = re.compile(r"^.* AS [a-zA-Z0-9_()]+#-?\d+L?$")